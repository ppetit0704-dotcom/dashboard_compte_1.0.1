import streamlit as st

def badge(label, value, color="#FB9223"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:12px;
            border-radius:8px;
            text-align:center;
            font-size:16px;
            font-weight:600;">
            <div style="font-size:19px; color:white;">{label}</div>
            <div>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )