# 💰 Finance Dashboard

A Streamlit-based financial analytics dashboard connected to a PostgreSQL database. It provides executive-level KPIs and risk analysis across transactions, clients, products, and branches.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Pages](#pages)
- [Filters](#filters)

---

## Features

- **Executive Overview** — KPI cards for total credit, debit, net balance, and unique client count
- **Monthly Trend Chart** — Line chart comparing credit vs. debit over time
- **Branch Performance** — Bar chart of credit volume per agency
- **Product Breakdown** — Bar chart of revenue by product
- **Client Segmentation** — Pie chart showing distribution across client segments
- **Risk Analysis** — Correlation heatmap, credit score scatter plot, and a top-10 risky clients table
- **CSV Export** — Download the filtered dataset at any time

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | [Streamlit](https://streamlit.io/) |
| Charts | [Plotly Express](https://plotly.com/python/plotly-express/) |
| Data | [Pandas](https://pandas.pydata.org/) |
| Database | PostgreSQL via [SQLAlchemy](https://www.sqlalchemy.org/) |
| Config | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## Project Structure

```
DASH/
├── assets/
│   └── Dashboard.png       # Dashboard preview image
├── src/
│   └── main.py             # Main Streamlit application
├── venv/                   # Virtual environment (not committed)
├── .env                    # Environment variables (not committed)
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Database Schema

The app reads from five tables and joins them into a single flat DataFrame:

| Table | Key Columns |
|-------|-------------|
| `transactions` | `client_id`, `produit_id`, `agence_id`, `montant`, `type_operation`, `date_transaction`, `taux_change_eur` |
| `client` | `client_id`, `segment_id`, `score_credit_client` |
| `segment` | `segment_id`, `segment_client` |
| `produit` | `produit_id`, `produit` |
| `agence` | `agence_id`, `agence` |

---

## Setup & Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-org/DASH.git
cd DASH
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**`requirements.txt` should include:**

```
streamlit
pandas
plotly
sqlalchemy
psycopg2-binary
python-dotenv
```

---

## Environment Variables

Create a `.env` file at the project root with the following keys:

```env
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
```

> **Never commit your `.env` file.** Add it to `.gitignore`.

---

## Running the App

```bash
streamlit run src/main.py
```

The app will be available at `http://localhost:8501` by default.

---

## Pages

### 📊 Executive

An overview of financial performance with four KPI metrics at the top:

- **Credit** — Total incoming transaction volume
- **Debit** — Total outgoing transaction volume
- **Net** — Credit minus Debit
- **Clients** — Number of unique clients in the filtered dataset

Followed by four charts:

1. Monthly credit vs. debit line chart
2. Client segment distribution pie chart
3. Credit volume by branch (bar chart)
4. Credit volume by product (bar chart)

### ⚠️ Risks

A deeper look at financial risk:

1. **Correlation Heatmap** — Relationships between `score_credit_client`, `montant`, and `taux_change_eur`
2. **Scatter Plot** — Credit score vs. transaction amount, colored by segment
3. **Top 10 Risky Clients** — Clients with the lowest average credit scores

---

## Filters

All charts and metrics respond to the sidebar filters in real time:

| Filter | Type | Description |
|--------|------|-------------|
| **Agence** | Multi-select | Filter by one or more branches |
| **Segment** | Multi-select | Filter by client segment |
| **Produit** | Multi-select | Filter by product type |
| **Year** | Range slider | Restrict to a specific year range |
