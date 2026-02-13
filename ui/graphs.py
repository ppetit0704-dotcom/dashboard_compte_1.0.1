import matplotlib.pyplot as plt
import streamlit as st

def camembert(df, top_n=4):
    grp = df.groupby("Chapitre")["Réalisé"].sum()
    grp = grp[grp > 0].sort_values(ascending=False)

    if len(grp) > top_n:
        top = grp.head(top_n)
        autres = grp.iloc[top_n:].sum()
        labels = list(top.index) + ["Autres"]
        values = list(top.values) + [autres]
    else:
        labels = grp.index
        values = grp.values

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")

    st.pyplot(fig)
