# 🏦 FinanceCore Banking Dashboard

> Interactive banking analytics dashboard built with **Streamlit** and **PostgreSQL**.  
> Two pages: executive overview and risk analysis, with global sidebar filters.

---

## ⚙️ Prerequisites

- Python 3.9+
- PostgreSQL (local or remote)
- pip

```bash
pip install streamlit pandas seaborn matplotlib sqlalchemy python-dotenv
```

---

## 🔧 Setup

### 1. Environment Variables

Create a `.env` file at the project root:

```env
DB_USER=your_username
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financecore
```

### 2. Database Schema

The app expects these tables in PostgreSQL:

| Table | Key Columns |
|-------|-------------|
| `transactions` | transaction_id, client_id, produit_id, agence_id, montant, date_transaction, type_operation |
| `client` | client_id, segment_id, score_credit_client |
| `segment` | segment_id, segment_client |
| `produit` | produit_id, produit |
| `agence` | agence_id, agence |

### 3. Run

```bash
streamlit run src/main.py
```

Opens at **http://localhost:8501**

---

## 📊 Pages

### Vue Exécutive

| KPI | Description |
|-----|-------------|
| 💳 Volume Transactions | Total transaction count |
| 💰 CA Total | Total revenue in MAD |
| 👤 Clients Actifs | Unique active clients |
| 📈 Marge Moyenne | Estimated margin (10% of mean transaction) |

Charts: Débits vs Crédits (line), CA par Agence (bar), CA par Produit (bar), Répartition Clients (pie)

### Analyse des Risques

- **Heatmap Corrélation** — score_credit_client × montant × taux_change_eur
- **Scatter Plot** — Credit score vs amount, colored by segment
- **Top 10 Clients à Risque** — lowest credit scores, color-coded (🔴 <40 / 🟠 <60 / 🟢 ≥60)

---

## 🔎 Sidebar Filters

All filters apply globally across both pages:

- **Agence** — multi-select branch filter
- **Segment Client** — multi-select segment filter
- **Produit** — multi-select product filter
- **Période** — year range slider

---

## 📥 Export

A **CSV download button** is available at the bottom of every page.  
File: `financecore_filtered_data.csv` (UTF-8 encoded, filtered data only)

---

## 🗂 Project Structure

```
Dashboard-Analytics/
├── .vscode/
│   └── settings.json       # VS Code workspace settings
├── assets/                 # Static assets
├── src/
│   └── main.py             # Main Streamlit application
├── venv/                   # Python virtual environment (not committed)
├── .env                    # Database credentials (not committed)
├── .gitignore
├── pyenv.cfg               # Python version config
└── requirements.txt        # Python dependencies
```

---

## 📝 Notes

- Data is cached via `@st.cache_data` — restart the app to refresh after DB changes
- `Marge Moyenne` is an estimate (10% of mean amount), not actual margin data
- `taux_change_eur` column must exist for the risk heatmap to render correctly
- All monetary values are displayed in **MAD** (Moroccan Dirham)

---

*FinanceCore Banking Dashboard — Internal Documentation*
