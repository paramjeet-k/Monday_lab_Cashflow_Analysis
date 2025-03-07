import streamlit as st
import numpy_financial as npf
import numpy as np
import matplotlib.pyplot as plt

# Streamlit app title
st.title("Mining Project Financial Evaluation")

# Sidebar inputs
st.sidebar.header("User Inputs")

mine_life = st.sidebar.slider("Mine Life (years)", 5, 30, 15)
annual_production = st.sidebar.number_input("Annual Production (tons)", value=2_000_000, step=100_000)
coal_price = st.sidebar.number_input("Coal Price (₹/ton)", value=50, step=1)
capital_expenditure = st.sidebar.number_input("CAPEX (₹)", value=200_000_000, step=10_000_000)
operating_cost_per_ton = st.sidebar.number_input("OPEX per Ton (₹)", value=25, step=1)
discount_rate = st.sidebar.slider("Discount Rate (%)", 1, 20, 10) / 100
tax_rate = st.sidebar.slider("Tax Rate (%)", 0, 50, 15) / 100
salvage_value = st.sidebar.number_input("Salvage Value (₹)", value=20_000_000, step=1_000_000)
inflation_rate = st.sidebar.slider("Inflation Rate (%)", 0, 10, 2) / 100
ramp_up_years = st.sidebar.slider("Ramp-up Years", 1, 5, 3)
production_growth_rate = st.sidebar.slider("Production Growth Rate (%)", 0, 10, 3) / 100

# Initialize variables
years = np.arange(0, mine_life + 1)
production = np.zeros(mine_life + 1)

# Simulating production ramp-up and growth
for t in range(1, mine_life + 1):
    if t <= ramp_up_years:
        production[t] = annual_production * (t / ramp_up_years)
    else:
        production[t] = production[t-1] * (1 + production_growth_rate)

# Inflation-adjusted price and cost
coal_prices = coal_price * (1 + inflation_rate) ** years
operating_costs = operating_cost_per_ton * (1 + inflation_rate) ** years

# Revenue, Cost, and Profit Calculations
revenue = production * coal_prices
opex = production * operating_costs
royalty = 0.05 * revenue  # Assuming 5% royalty on revenue
gross_profit = revenue - opex - royalty
tax = gross_profit * tax_rate
net_profit = gross_profit - tax

# Cash Flow Projection with Salvage Value
cash_flows = np.zeros(mine_life + 1)
cash_flows[0] = -capital_expenditure  # Initial CAPEX
cash_flows[1:mine_life + 1] = net_profit[1:mine_life + 1]  # Recurring yearly profits
cash_flows[mine_life] += salvage_value  # Adding salvage value at end of mine life

# Cumulative Cash Flow
cumulative_cash_flows = np.cumsum(cash_flows)

# NPV, IRR, and PI Calculations
discounted_cash_flows = cash_flows / (1 + discount_rate) ** years
npv = np.sum(discounted_cash_flows)
irr = npf.irr(cash_flows) * 100  # Convert to percentage
pi = np.sum(discounted_cash_flows[1:]) / capital_expenditure

# Payback Period Calculation
payback_period = np.argmax(cumulative_cash_flows >= 0)

# Display key financial metrics
st.header("Key Financial Metrics")
metrics = {
    "Net Present Value (NPV) (M₹)": round(npv / 1e6, 2),
    "Internal Rate of Return (IRR) (%)": round(irr, 2),
    "Profitability Index (PI)": round(pi, 2),
    "Payback Period (Years)": payback_period
}
st.write(metrics)

# Visualization - Cash Flow Trends
st.header("Cumulative Cash Flow Trend")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(years, cumulative_cash_flows / 1e6, marker="o", linestyle="--", label="Cumulative Cash Flow (M₹)")
ax.axhline(0, color='red', linestyle="--", label="Break-even Line")
ax.set_xlabel("Year")
ax.set_ylabel("Cash Flow (M₹)")
ax.set_title("Cumulative Cash Flow Trend")
ax.legend()
ax.grid()
st.pyplot(fig)
