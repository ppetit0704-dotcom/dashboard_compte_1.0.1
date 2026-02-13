
# -*- coding: utf-8 -*-
"""
Module tables.py
@author: P.PETIT
"""


import streamlit as st
import pandas as pd
#import sys

st.markdown("""
<style>
.detail-box {
    background-color: #f2f2f2;   /* gris clair */
    padding: 1rem 1.2rem;
    border-radius: 6px;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #b0b0b0;
}

.detail-box-title {
    font-weight: 600;
    margin-bottom: 0.2rem;
}

.detail-box-subtitle {
    color: #555;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)



# Colonnes Liquidé
COLS_LIQUIDE = [f"Liquidé_N_{i}" for i in range(1, 6)]

# --- Tableau des chapitres avec Détails ---
def tableau_chapitres(df, annees, budget, section, sens):

    # Colonnes numériques de base
    cols_base = ["Total_Prévu", "Réalisé", "Reste_engagé"]

    # Colonnes réellement présentes
    cols_liquide = [c for c in COLS_LIQUIDE if c in df.columns]
    cols_annees = [c for c in annees if c in df.columns]

    cols_numeriques = cols_base + cols_liquide + cols_annees

    # Sécurisation conversion numérique
    for col in cols_numeriques:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Agrégation par chapitre
    table = df.groupby("Chapitre")[cols_numeriques].sum().reset_index()

    # État ouvert/fermé
    if "chapitres_ouverts" not in st.session_state:
        st.session_state.chapitres_ouverts = {}

    st.subheader("📋 Tableau des chapitres")

    # ---- ENTÊTE ----
    header_cols = st.columns([2] + [2] * len(cols_base + cols_liquide) + [1])
    header_cols[0].markdown("**Chapitre**")

    for i, col in enumerate(cols_base + cols_liquide, start=1):
        header_cols[i].markdown(f"**{col.replace('_', ' ')}**")

    header_cols[-1].markdown("**Détails**")

    # ---- LIGNES ----
    for idx, row in table.iterrows():
        cols = st.columns([2] + [2] * len(cols_base + cols_liquide) + [1])

        cols[0].write(row["Chapitre"])

        for i, col in enumerate(cols_base + cols_liquide, start=1):
            valeur = row[col]
            # Sécurisation : Series → scalaire
            if isinstance(valeur, pd.Series):
                valeur = valeur.sum()
            
            valeur = 0.0 if pd.isna(valeur) else float(valeur)
            
            cols[i].write(f"{valeur:,.2f} €".replace(",", " "))

        # Bouton détail
        if cols[-1].button(
            "..." if not st.session_state.chapitres_ouverts.get(idx, False) else "...",
            key=f"detail_{idx}"
        ):
            st.session_state.chapitres_ouverts[idx] = not st.session_state.chapitres_ouverts.get(idx, False)

        # Affichage détail
        if st.session_state.chapitres_ouverts.get(idx, False):
            voir_detail_chapitre(df, budget, section, sens, row["Chapitre"])


# --- Détail d’un chapitre ---
def voir_detail_chapitre(df, budget, section, sens, chapitre):

    cols_base = ["Compte", "Total_Prévu", "Réalisé", "Reste_engagé"]
    cols_liquide = [c for c in COLS_LIQUIDE if c in df.columns]
    cols_affichees = cols_base + cols_liquide

    df_detail = df.loc[
        (df["Libellé_budget"] == budget) &
        (df["Section"] == section) &
        (df["Sens"] == sens) &
        (df["Chapitre"] == chapitre),
        cols_affichees
    ].copy()

    # Conversion + formatage manuel (SANS Styler)
    for col in cols_affichees:
        if col != "Compte":
            df_detail[col] = (
                pd.to_numeric(df_detail[col], errors="coerce")
                .fillna(0)
                .map(lambda x: f"{x:,.2f} €".replace(",", " "))
            )

    st.write(f"**Détails du Chapitre {chapitre} ({budget} / {section} / {sens})**")
    
    st.markdown(
       f"""
       <div class="detail-box">
           <strong>Détails du Chapitre {chapitre}</strong><br>
           <em>{budget} / {section} / {sens}</em>
       </div>
       """,
       unsafe_allow_html=True
     )

    st.dataframe(df_detail, use_container_width=True)
