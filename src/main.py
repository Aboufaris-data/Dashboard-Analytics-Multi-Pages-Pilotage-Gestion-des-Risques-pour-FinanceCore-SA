import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Finance Dashboard", layout="wide")
st.title("💰 Finance Dashboard")

COLOR_MAP = {"credit": "#00CC96", "debit": "#EF553B"}

# ---------------- DATABASE ----------------
@st.cache_resource
def get_engine():
    load_dotenv()
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

engine = get_engine()

# ---------------- DATA ----------------
@st.cache_data
def load_data():
    tables = ["segment", "client", "produit", "agence", "transactions"]
    data = {}

    with engine.connect() as con:
        for t in tables:
            data[t] = pd.read_sql(text(f"SELECT * FROM {t}"), con)

    df = data["transactions"] \
        .merge(data["client"], on="client_id") \
        .merge(data["segment"], on="segment_id") \
        .merge(data["produit"], on="produit_id") \
        .merge(data["agence"], on="agence_id")

    df["date_transaction"] = pd.to_datetime(df["date_transaction"])
    df["type_operation"] = df["type_operation"].str.lower().str.strip()
    df["mois"] = df["date_transaction"].dt.to_period("M").astype(str)
    df["annee"] = df["date_transaction"].dt.year

    return df

df = load_data()

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio("Navigation", ["Executive", "Risks"])

def apply_filters(df):
    agence = st.sidebar.multiselect("Agence", df["agence"].unique(), df["agence"].unique())
    segment = st.sidebar.multiselect("Segment", df["segment_client"].unique(), df["segment_client"].unique())
    produit = st.sidebar.multiselect("Produit", df["produit"].unique(), df["produit"].unique())

    years = st.sidebar.slider(
        "Year",
        int(df["annee"].min()),
        int(df["annee"].max()),
        (int(df["annee"].min()), int(df["annee"].max()))
    )

    return df[
        df["agence"].isin(agence) &
        df["segment_client"].isin(segment) &
        df["produit"].isin(produit) &
        df["annee"].between(*years)
    ]

df_filtered = apply_filters(df)

# ---------------- EXECUTIVE ----------------
if page == "Executive":

    st.subheader("📊 Executive Overview")

    credit = df_filtered.query("type_operation=='credit'")["montant"].sum()
    debit = df_filtered.query("type_operation=='debit'")["montant"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Credit", f"{credit:,.0f} MAD")
    col2.metric("Debit", f"{debit:,.0f} MAD")
    col3.metric("Net", f"{credit - debit:,.0f} MAD")
    col4.metric("Clients", df_filtered["client_id"].nunique())

    st.divider()

    # -------- DATA --------
    df_line = df_filtered.groupby(["mois", "type_operation"])["montant"].sum().reset_index()
    df_agence = df_filtered.query("type_operation=='credit'").groupby("agence")["montant"].sum().reset_index()
    df_produit = df_filtered.query("type_operation=='credit'").groupby("produit")["montant"].sum().reset_index()
    df_segment = df_filtered["segment_client"].value_counts().reset_index()
    df_segment.columns = ["segment", "count"]

    # -------- CHARTS --------
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.line(
            df_line,
            x="mois",
            y="montant",
            color="type_operation",
            color_discrete_map=COLOR_MAP,
            markers=True
        )
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(df_segment, names="segment", values="count")
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig = px.bar(
            df_agence,
            x="agence",
            y="montant",
            color="montant",
            color_continuous_scale="Greens"
        )
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.bar(
            df_produit,
            x="produit",
            y="montant",
            color="produit"
        )
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- RISKS ----------------
else:
    st.subheader("⚠️ Risk Analysis")

    col1, col2 = st.columns(2)

    corr = df_filtered[["score_credit_client", "montant", "taux_change_eur"]].corr()

    with col1:
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu")
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            df_filtered,
            x="score_credit_client",
            y="montant",
            color="segment_client"
        )
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Risky Clients")

    risk = df_filtered.groupby("client_id").agg({
        "score_credit_client": "mean",
        "montant": "sum"
    }).sort_values("score_credit_client").head(10)

    st.dataframe(risk, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "Download CSV",
    df_filtered.to_csv(index=False).encode(),
    "finance.csv",
    "text/csv"
)