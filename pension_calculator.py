import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Streamlit UI
st.title("Pension Growth Calculator")

# User inputs
initial_balance = st.number_input("Initial Pension Balance ($)", value=0, step=1000)
annual_contribution = st.number_input("Annual Contribution ($)", value=60000, step=1000)
expected_return = st.slider("Expected Annual Return (%)", min_value=1.0, max_value=12.0, value=7.0, step=0.1) / 100
years = st.slider("Number of Years", min_value=1, max_value=50, value=30, step=1)

# Calculate pension growth
balances = []
balance = initial_balance

for year in range(1, years + 1):
    balance = (balance + annual_contribution) * (1 + expected_return)  # Compounded growth
    balances.append({"Year": year, "Pension Balance ($)": round(balance, 2)})

# Convert to DataFrame
pension_df = pd.DataFrame(balances)

# Display DataFrame
st.subheader("Pension Growth Over Time")
st.dataframe(pension_df)

# Plot the growth
st.subheader("Pension Balance Over Time")
plt.figure(figsize=(8, 5))
plt.plot(pension_df["Year"], pension_df["Pension Balance ($)"], marker="o", linestyle="-")
plt.xlabel("Years")
plt.ylabel("Pension Balance ($)")
plt.grid(True)
st.pyplot(plt)
