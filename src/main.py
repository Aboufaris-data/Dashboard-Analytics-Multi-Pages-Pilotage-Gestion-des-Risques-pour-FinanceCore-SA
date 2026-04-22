import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ======================================
# CONFIG PAGE
# ======================================
st.set_page_config(
    page_title="FinanceCore Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏦 FinanceCore Banking Dashboard")

# ======================================
# DATABASE CONNECTION
# ======================================
load_dotenv()

try:
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    db_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)

    st.success("✅ Database Connected Successfully")

except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# ======================================
# LOAD DATA
# ======================================
@st.cache_data
def load_data():
    with engine.connect() as con:
        segment = pd.read_sql(text("SELECT * FROM segment"), con)
        client = pd.read_sql(text("SELECT * FROM client"), con)
        produit = pd.read_sql(text("SELECT * FROM produit"), con)
        agence = pd.read_sql(text("SELECT * FROM agence"), con)
        transactions = pd.read_sql(text("SELECT * FROM transactions"), con)

    df = transactions.merge(client, on="client_id", how="left")
    df = df.merge(segment, on="segment_id", how="left")
    df = df.merge(produit, on="produit_id", how="left")
    df = df.merge(agence, on="agence_id", how="left")

    df["date_transaction"] = pd.to_datetime(df["date_transaction"], errors="coerce")
    df["mois"] = df["date_transaction"].dt.to_period("M").astype(str)
    df["annee"] = df["date_transaction"].dt.year

    return df

df = load_data()

# ======================================
# SIDEBAR NAVIGATION
# ======================================
page = st.sidebar.radio(
    "📂 Navigation",
    ["📊 Vue Exécutive", "⚠️ Analyse des Risques"]
)

# ======================================
# FILTERS
# ======================================
st.sidebar.header("🔎 Filtres")

agence_filter = st.sidebar.multiselect(
    "Agence",
    df["agence"].dropna().unique(),
    default=df["agence"].dropna().unique()
)

segment_filter = st.sidebar.multiselect(
    "Segment Client",
    df["segment_client"].dropna().unique(),
    default=df["segment_client"].dropna().unique()
)

produit_filter = st.sidebar.multiselect(
    "Produit",
    df["produit"].dropna().unique(),
    default=df["produit"].dropna().unique()
)

year_filter = st.sidebar.slider(
    "Période",
    int(df["annee"].min()),
    int(df["annee"].max()),
    (int(df["annee"].min()), int(df["annee"].max()))
)

# ======================================
# APPLY FILTERS
# ======================================
df_filtered = df[
    (df["agence"].isin(agence_filter)) &
    (df["segment_client"].isin(segment_filter)) &
    (df["produit"].isin(produit_filter)) &
    (df["annee"].between(year_filter[0], year_filter[1]))
]

# ======================================================
# PAGE 1 : VUE EXECUTIVE
# ======================================================
if page == "📊 Vue Exécutive":

    st.header("📊 Vue Exécutive")

    volume_transactions = df_filtered["transaction_id"].count()
    ca_total = df_filtered["montant"].sum()
    clients_actifs = df_filtered["client_id"].nunique()
    marge_moyenne = df_filtered["montant"].mean() * 0.1

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💳 Volume Transactions", f"{volume_transactions:,}")
    col2.metric("💰 CA Total", f"{ca_total:,.2f} MAD")
    col3.metric("👤 Clients Actifs", f"{clients_actifs}")
    col4.metric("📈 Marge Moyenne", f"{marge_moyenne:,.2f} MAD")

    st.divider()

    df_line = df_filtered.groupby(["mois", "type_operation"])["montant"].sum().reset_index()
    df_agence = df_filtered.groupby("agence")["montant"].sum().reset_index()
    df_produit = df_filtered.groupby("produit")["montant"].sum().reset_index()
    df_segment = df_filtered["segment_client"].value_counts()

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("📈 Débits vs Crédits")
        fig, ax = plt.subplots(figsize=(8,4))
        sns.lineplot(data=df_line, x="mois", y="montant", hue="type_operation", marker="o", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with col6:
        st.subheader("🏦 CA par Agence")
        fig, ax = plt.subplots(figsize=(8,4))
        sns.barplot(data=df_agence, x="agence", y="montant", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    col7, col8 = st.columns(2)

    with col7:
        st.subheader("💳 CA par Produit")
        fig, ax = plt.subplots(figsize=(8,4))
        sns.barplot(data=df_produit, x="produit", y="montant", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with col8:
        st.subheader("👥 Répartition Clients")
        fig, ax = plt.subplots(figsize=(6,6))
        ax.pie(df_segment, labels=df_segment.index, autopct="%1.1f%%")
        st.pyplot(fig)

# ======================================================
# PAGE 2 : ANALYSE DES RISQUES
# ======================================================
elif page == "⚠️ Analyse des Risques":

    st.header("⚠️ Analyse des Risques")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Heatmap Corrélation")
        corr = df_filtered[["score_credit_client", "montant", "taux_change_eur"]].corr()

        fig, ax = plt.subplots(figsize=(7,4))
        sns.heatmap(corr, annot=True, cmap="Reds", ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("📍 Score Crédit vs Montant")
        fig, ax = plt.subplots(figsize=(7,4))
        sns.scatterplot(
            data=df_filtered,
            x="score_credit_client",
            y="montant",
            hue="segment_client",
            ax=ax
        )
        st.pyplot(fig)

    st.subheader("🚨 Top 10 Clients à Risque")

    risk_clients = df_filtered.groupby("client_id").agg({
        "score_credit_client": "mean",
        "montant": "sum"
    }).reset_index()

    risk_clients = risk_clients.sort_values("score_credit_client").head(10)

    def color_risk(val):
        if val < 40:
            return "background-color: red"
        elif val < 60:
            return "background-color: orange"
        else:
            return "background-color: lightgreen"

    styled_df = risk_clients.style.map(color_risk, subset=["score_credit_client"])

    st.dataframe(styled_df)

# ======================================
# EXPORT CSV
# ======================================
st.divider()

st.download_button(
    label="Télécharger les données filtrées",
    data=df_filtered.to_csv(index=False).encode("utf-8"),
    file_name="financecore_filtered_data.csv",
    mime="text/csv"
)