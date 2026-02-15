# -*- coding: utf-8 -*-
"""
Dashboard comptable M57
@author : P. PETIT
Version : 1.09.01
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

from core.loader import load_csv
from ui.cards import badge, badgeGreen, badgeOrange


# =====================================================
# FONCTIONS FORMATAGE
# =====================================================
def format_euro(val):
    return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " €"

def format_entier(val):
    return f"{int(val):,}".replace(",", " ")


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

st.markdown("""
<style>
div.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.6em 0.8em;
    font-weight: 600;
}
div.stButton > button:hover {
    background-color: #388E3C;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# SESSION STATE
# =====================================================
if "tiers_selected" not in st.session_state:
    st.session_state.tiers_selected = "Tous"


# =====================================================
# HEADER
# =====================================================
logo_path = ROOT_DIR / "assets" / "logo.png"
st.image(str(logo_path), width=480)
st.title("📊 Tableau de bord compte – M57")
st.caption("Version 1.09.01 | Tableau de bord compte [M57] | P. PETIT")


# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:

    st.header("⚙️ Paramètres")

    file = st.file_uploader("📁 Charger le fichier CSV", type="csv")

    budget = section = service = sens = compte = tiers = "Tous"

    if file:

        df_temp = load_csv(file)

        # --- Budget
        budgets = sorted(df_temp["Libellé_budget"].dropna().astype(str).unique())
        budget = st.selectbox("Budget", ["Tous"] + budgets)

        df_budget = df_temp if budget == "Tous" else df_temp[df_temp["Libellé_budget"] == budget]

        # --- Section
        sections = sorted(df_budget["Section"].dropna().astype(str).unique())
        section = st.selectbox("Section", ["Tous"] + sections)

        df_section = df_budget if section == "Tous" else df_budget[df_budget["Section"] == section]

        # --- Service
        if "Service" in df_section.columns:
            services = sorted(df_section["Service"].dropna().astype(str).unique())
            service = st.selectbox("Service", ["Tous"] + services)
            df_service = df_section if service == "Tous" else df_section[df_section["Service"] == service]
        else:
            df_service = df_section

        # --- Sens
        sens_list = sorted(df_service["Sens"].dropna().astype(str).unique())
        sens = st.selectbox("Sens", ["Tous"] + sens_list)
        df_sens = df_service if sens == "Tous" else df_service[df_service["Sens"] == sens]

        # --- Compte
        comptes = sorted(df_sens["Compte"].dropna().astype(str).unique())
        compte = st.selectbox("Compte", ["Tous"] + comptes)
        df_compte = df_sens if compte == "Tous" else df_sens[df_sens["Compte"] == compte]

        # --- Tiers (réactif)
        if "Tiers" in df_compte.columns:
            tiers_list = sorted(df_compte["Tiers"].dropna().astype(str).unique())
            options_tiers = ["Tous"] + tiers_list

            if st.session_state.tiers_selected not in options_tiers:
                st.session_state.tiers_selected = "Tous"

            # Fonction pour mettre à jour le tiers sélectionné
            def update_tiers():
                st.session_state.tiers_selected = st.session_state["tiers_box"]

            tiers = st.selectbox(
                "Tiers",
                options_tiers,
                index=options_tiers.index(st.session_state.tiers_selected),
                key="tiers_box",
                on_change=update_tiers
            )


# =====================================================
# CONTENU PRINCIPAL
# =====================================================
if file:

    df = load_csv(file)
    df_filtre = df.copy()

    # ---------- Application filtres
    if budget != "Tous":
        df_filtre = df_filtre[df_filtre["Libellé_budget"] == budget]
    if section != "Tous":
        df_filtre = df_filtre[df_filtre["Section"] == section]
    if service != "Tous":
        df_filtre = df_filtre[df_filtre["Service"] == service]
    if sens != "Tous":
        df_filtre = df_filtre[df_filtre["Sens"] == sens]
    if compte != "Tous":
        df_filtre = df_filtre[df_filtre["Compte"] == compte]

    tiers = st.session_state.tiers_selected
    if tiers != "Tous":
        df_filtre = df_filtre[df_filtre["Tiers"] == tiers]

    # ---------- Conversion numérique sécurisée
    if "Liquidé" in df_filtre.columns:
        df_filtre["Liquidé"] = pd.to_numeric(df_filtre["Liquidé"], errors="coerce").fillna(0)
    if "Exercice" in df_filtre.columns:
        df_filtre["Exercice"] = pd.to_numeric(df_filtre["Exercice"], errors="coerce").fillna(0)

    # =====================================================
    # PREPARATION TABLE
    # =====================================================
    colonnes_affichage = [
        "Exercice", "Section", "Sens", "Service",
        "Chapitre", "Compte", "Type", "Imputation",
        "Tiers", "Liquidé", "N_Bordereau", "N_Pièce"
    ]

    colonnes_existantes = [c for c in colonnes_affichage if c in df_filtre.columns]
    table = df_filtre[colonnes_existantes].copy()
    total_liquide = table["Liquidé"].sum() if "Liquidé" in table else 0

    # ---------- FORMATAGE AFFICHAGE
    if "Liquidé" in table.columns:
        table["Liquidé"] = table["Liquidé"].apply(format_euro)
    if "Exercice" in table.columns:
        table["Exercice"] = table["Exercice"].apply(format_entier)

    # ---------- Ligne TOTAL
    table_total = table.copy()
    if "Liquidé" in table.columns:
        total_row = {col: "" for col in table_total.columns}
        total_row[table_total.columns[0]] = "TOTAL"
        total_row["Liquidé"] = format_euro(total_liquide)
        table_total.loc[len(table_total)] = total_row

    # =====================================================
    # BADGE GLOBAL
    # =====================================================
    st.subheader("📋 Résultats")
    badgeOrange(f"{budget} - {section} - {sens} - {compte} - {tiers}", format_euro(total_liquide))

    # =====================================================
    # BADGES PAR TIERS
    # =====================================================
    if "Tiers" in df_filtre.columns and "Liquidé" in df_filtre.columns:
    
        st.markdown("### 💼 Totaux par tiers (Top 10)")
    
        # Sécurisation totale du numérique
        df_filtre["Liquidé"] = pd.to_numeric(
            df_filtre["Liquidé"], errors="coerce"
        ).fillna(0)
    
        tiers_totaux = (
            df_filtre
            .groupby("Tiers", as_index=False)["Liquidé"]
            .sum()
            .sort_values(by="Liquidé", ascending=False)
            .reset_index(drop=True)
            .head(10)
        )
        #Bouton Tiers
        st.markdown("""
            <style>
            .stButton > button {
                white-space: pre-line;
            }
            </style>
        """, unsafe_allow_html=True)
        batch_size = 10
        nb_cols = 5
        
        for i in range(0, len(tiers_totaux), nb_cols):
        
            st.divider()
        
            # ✅ batch existe ici
            batch = tiers_totaux.iloc[i:i+nb_cols]
        
            cols = st.columns(len(batch))
        
            for idx, (col_idx, row) in enumerate(
                    zip(range(len(batch)), batch.itertuples())):
        
                with cols[col_idx]:
        
                    if st.button(
                        f"{row.Tiers}\n{format_euro(row.Liquidé)}",
                        use_container_width=True,
                        key=f"tiers_{i}_{idx}_{row.Tiers}"
                    ):
                        st.session_state.tiers_selected = row.Tiers




    # =====================================================
    # TABLE
    # =====================================================
    st.divider()
    st.dataframe(table_total, use_container_width=True)

else:
    st.info("⬅️ Veuillez charger un fichier CSV depuis le panneau latéral.")
