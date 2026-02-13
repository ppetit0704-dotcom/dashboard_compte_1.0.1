import streamlit as st

def filtres(df):
    st.sidebar.header("Filtres")

    #budgets = sorted(df["Libellé_budget"].dropna().unique())
    
    # Convertir en string pour le tri
    budgets = st.sidebar.selectbox("Libellé_budget", sorted(df["Libellé_budget"].dropna().astype(str).unique()))
    section = st.sidebar.selectbox("Section", sorted(df["Section"].dropna().astype(str).unique()))   
    sens = st.sidebar.selectbox("Sens", sorted(df["Sens"].dropna().astype(str).unique()))
    chapitre = st.sidebar.selectbox("Chapitre", sorted(df["Chapitre"].dropna().astype(str).unique()))
    compte = st.sidebar.selectbox("Compte", sorted(df["Compte"].dropna().astype(str).unique()))
  
    return budgets, section, sens, chapitre, compte
