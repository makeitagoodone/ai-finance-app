import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# Database connection parameters
DB_HOST = 'ep-noisy-moon-a5gxiq67-pooler.us-east-2.aws.neon.tech'
DB_NAME = 'neondb'
DB_USER = 'neondb_owner'
DB_PASS = 'npg_Z6LXsyMqgb5a'

# Function to establish a connection to the database
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

# Streamlit UI
st.title("Pension Growth Calculator")

# User Inputs
initial_balance = st.number_input("Initial Pension Balance ($)", value=0, step=1000)
annual_contribution = st.number_input("Annual Contribution ($)", value=60000, step=1000)
expected_return = st.slider("Expected Annual Return (%)", min_value=1.0, max_value=12.0, value=7.0, step=0.1) / 100
contribution_years = st.slider("Years Contributing", min_value=1, max_value=50, value=30, step=1)
total_growth_years = st.slider("Total Years for Growth", min_value=contribution_years, max_value=60, value=40, step=1)

# Calculate pension growth
balances = []
balance = initial_balance

# Contribution phase
for year in range(1, contribution_years + 1):
    balance = (balance + annual_contribution) * (1 + expected_return)
    balances.append({"Year": year, "Pension Balance ($)": round(balance, 2), "Phase": "Contribution"})

# Growth phase (no contributions, just growth)
for year in range(contribution_years + 1, total_growth_years + 1):
    balance *= (1 + expected_return)
    balances.append({"Year": year, "Pension Balance ($)": round(balance, 2), "Phase": "Growth"})

# Convert to DataFrame
pension_df = pd.DataFrame(balances)

# Display DataFrame
st.subheader("Pension Growth Over Time")
st.dataframe(pension_df)

# Save to Database
if st.button("Save Calculation"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pension_calculations (
                id SERIAL PRIMARY KEY,
                initial_balance NUMERIC,
                annual_contribution NUMERIC,
                expected_return NUMERIC,
                contribution_years INTEGER,
                total_growth_years INTEGER,
                final_balance NUMERIC,
                calculation_date TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO pension_calculations (
                initial_balance,
                annual_contribution,
                expected_return,
                contribution_years,
                total_growth_years,
                final_balance,
                calculation_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            initial_balance,
            annual_contribution,
            expected_return,
            contribution_years,
            total_growth_years,
            balance,
            datetime.now()
        ))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Calculation saved successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Display Last 10 Entries
st.subheader("Last 10 Saved Calculations")
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT initial_balance, annual_contribution, expected_return,
               contribution_years, total_growth_years, final_balance, calculation_date
        FROM pension_calculations
        ORDER BY calculation_date DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if rows:
        history_df = pd.DataFrame(rows, columns=[
            "Initial Balance ($)", "Annual Contribution ($)", "Expected Return (%)",
            "Contribution Years", "Total Growth Years", "Final Balance ($)", "Date"
        ])
        st.dataframe(history_df)
    else:
        st.info("No calculations saved yet.")
except Exception as e:
    st.error(f"An error occurred: {e}")
