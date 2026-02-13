# -*- coding: utf-8 -*-
"""
Dashboard comptable M57
@author : P. PETIT
Version : 1.08.00
"""

import sys
from pathlib import Path
import streamlit as st

from core.loader import load_csv
from ui.cards import badge


# =====================================================
# CONFIGURATION
# =====================================================
ROOT_DIR = Path(__file__).resolve().parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

st.set_page_config(
    layout="wide",
    page_title="Dashboard comptable M57"
)


# =====================================================
# HEADER
# =====================================================
logo_path = ROOT_DIR / "assets" / "logo.png"

st.image(str(logo_path), width=480)
st.title("📊 Tableau de bord compte – M57")
st.caption("Version 1.01.13 | Tableau de bord compte [M57] | P. PETIT")


# -----------------------------
# SIDEBAR - PARAMETRES
# -----------------------------
with st.sidebar:

    st.header("⚙️ Paramètres")

    file = st.file_uploader(
        "📁 Charger le fichier CSV",
        type="csv"
    )

    budget = None
    section = None
    service = None  # Nouveau filtre
    sens = None
    compte = None

    if file:

        df_temp = load_csv(file)

        # --- Budget
        budgets = sorted(
            df_temp["Libellé_budget"]
            .dropna()
            .astype(str)
            .unique()
        )
        budget = st.selectbox("Budget", ["Tous"] + budgets)
        df_budget = df_temp.copy()
        if budget != "Tous":
            df_budget = df_budget[df_budget["Libellé_budget"] == budget]

        # --- Section
        sections = sorted(
            df_budget["Section"]
            .dropna()
            .astype(str)
            .unique()
        )
        section = st.selectbox("Section", ["Tous"] + sections)
        df_section = df_budget.copy()
        if section != "Tous":
            df_section = df_section[df_section["Section"] == section]

        # --- Service (nouveau filtre)
        if "Service" in df_section.columns:
            services = sorted(
                df_section["Service"]
                .dropna()
                .astype(str)
                .unique()
            )
            service = st.selectbox("Service", ["Tous"] + services)
            df_service = df_section.copy()
            if service != "Tous":
                df_service = df_service[df_service["Service"] == service]
        else:
            df_service = df_section.copy()
            service = "Tous"

        # --- Sens
        sens_list = sorted(
            df_service["Sens"]
            .dropna()
            .astype(str)
            .unique()
        )
        sens = st.selectbox("Sens", ["Tous"] + sens_list)
        df_sens = df_service.copy()
        if sens != "Tous":
            df_sens = df_sens[df_sens["Sens"] == sens]

        # --- Compte
        comptes = sorted(
            df_sens["Compte"]
            .dropna()
            .astype(str)
            .unique()
        )
        compte = st.selectbox("Compte", ["Tous"] + comptes)



# =====================================================
# CONTENU PRINCIPAL
# =====================================================
if file:

    df = load_csv(file)
    df_filtre = df.copy()

    # -----------------------------
    # Application des filtres
    # -----------------------------
    if budget and budget != "Tous":
        df_filtre = df_filtre[df_filtre["Libellé_budget"] == budget]
    
    if section and section != "Tous":
        df_filtre = df_filtre[df_filtre["Section"] == section]
    
    # Nouveau filtre Service
    if service and service != "Tous":
        df_filtre = df_filtre[df_filtre["Service"] == service]
    
    if sens and sens != "Tous":
        df_filtre = df_filtre[df_filtre["Sens"] == sens]
    
    if compte and compte != "Tous":
        df_filtre = df_filtre[df_filtre["Compte"] == compte]


    # -----------------------------
    # PREPARATION TABLE
    # -----------------------------
    colonnes_affichage = [
        "Exercice",
        "Section",
        "Sens",
        "Service",
        "Chapitre",
        "Compte",
        "Type",
        "Imputation",
        "Tiers",
        "Liquidé",
        "N_Bordereau",
        "N_Pièce"
    ]

    colonnes_existantes = [
        col for col in colonnes_affichage
        if col in df_filtre.columns
    ]

    table = df_filtre[colonnes_existantes].copy()

    total_liquide = 0

    # ==========================
    # AJOUT LIGNE TOTAL
    # ==========================
    colonnes_numeriques = table.select_dtypes(include="number").columns
    table_total = table.copy()

    if len(colonnes_numeriques) > 0:

        total_row = {col: "" for col in table.columns}
        total_row[table.columns[0]] = "TOTAL"

        for col in colonnes_numeriques:
            total_row[col] = table[col].sum()

        if "Liquidé" in colonnes_numeriques:
            total_liquide = total_row["Liquidé"]
            total_row["Liquidé"] = f"{total_liquide:,.2f} €"

        table_total.loc[len(table_total)] = total_row

    # =====================================================
    # BADGE (AVANT LE TABLEAU)
    # =====================================================
    st.subheader("📋 Résultats")

    badge(
        f"{budget} - {section} - {sens} - {compte}",
        f"{total_liquide:,.2f} €"
    )
   # =====================================================
    # BADGES PAR TIERS (TRIÉS ET MULTI-LIGNES)
    # =====================================================
    if "Tiers" in df_filtre.columns and "Liquidé" in df_filtre.columns:
    
        st.markdown("### 💼 Totaux par tiers (Top 20)")
    
        # Somme des liquidés par tiers, tri décroissant, top 20 (ou tous si tu veux)
        tiers_totaux = (
            df_filtre
            .groupby("Tiers")["Liquidé"]
            .sum()
            .sort_values(ascending=False)
            .head(20)  # change ou supprime pour tous
        )
    
        # Transformation en liste pour itération
        items = list(tiers_totaux.items())
        batch_size = 5  # nombre de badges par ligne
    
        # Création des lignes de badges
        for i in range(0, len(items), batch_size):
            st.divider()
            batch = items[i:i+batch_size]
            cols = st.columns(len(batch))
            for col, (tiers, montant) in zip(cols, batch):
                with col:
                    badge(
                        tiers,
                        f"{montant:,.2f} €",
                        color="#4CAF50"
                    )


    # =====================================================
    # TABLE
    # =====================================================
    st.dataframe(
        table_total,
        use_container_width=True
    )

else:
    st.info("⬅️ Veuillez charger un fichier CSV depuis le panneau latéral.")
