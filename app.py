import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Page Configuration & US Commercial Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="FeedMillPro USA | Commercial Formulation & Margin Engine",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #0F172A; }
    .sub-header { font-size: 1.1rem; color: #475569; margin-bottom: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: Operational Controls (US Standards)
# ---------------------------------------------------------
st.sidebar.title("FeedMillPro USA")
st.sidebar.caption("Commercial Feedmill Analytics (US Edition)")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Mill Batch Parameters")
batch_size_tons = st.sidebar.number_input("Target Batch Weight (Short Tons)", min_value=1.0, max_value=100.0, value=5.0, step=0.5)
bag_weight_lbs = st.sidebar.number_input("Finished Bag Weight (lbs)", min_value=10.0, max_value=100.0, value=50.0, step=5.0)

# Unit Conversions
batch_size_lbs = batch_size_tons * 2000.0

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Pricing & Overheads")
target_selling_price_per_ton = st.sidebar.number_input("Target Selling Price / Ton ($)", min_value=0.0, value=480.0, step=10.0)
packaging_cost_per_bag = st.sidebar.number_input("Bagging & Tagging Cost / Bag ($)", min_value=0.0, value=0.75, step=0.05)
milling_power_labor_per_ton = st.sidebar.number_input("Grinding, Mixing & Direct Overhead / Ton ($)", min_value=0.0, value=18.00, step=1.00)
shrinkage_loss_percent = st.sidebar.slider("Operational Moisture / Shrinkage Loss (%)", min_value=0.0, max_value=5.0, value=1.0, step=0.1)

# ---------------------------------------------------------
# Main Interface: Formulation Matrix
# ---------------------------------------------------------
st.markdown('<div class="main-header">🌽 FeedMillPro USA: Least-Cost & Batch Margin Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Commercial unit economics, nutritional tracking, and batch profitability suite for US feed producers.</div>', unsafe_allow_html=True)

# Default US Ingredient Library
if "formulation_data" not in st.session_state:
    st.session_state.formulation_data = pd.DataFrame({
        "Ingredient": ["Yellow Dent Corn #2", "Soybean Meal (48% CP)", "Distillers Dried Grains (DDGS)", "Wheat Middlings", "Limestone (Feed Grade)", "Monocalcium Phosphate", "L-Lysine HCl", "DL-Methionine", "Trace Mineral & Vitamin Premix"],
        "Inclusion Rate (lbs)": [5800.0, 2600.0, 800.0, 400.0, 180.0, 120.0, 40.0, 20.0, 40.0],
        "Cost per Ton ($)": [185.0, 410.0, 210.0, 160.0, 45.0, 820.0, 1450.0, 2800.0, 3200.0],
        "Est. Crude Protein (%)": [8.5, 48.0, 27.0, 16.0, 0.0, 0.0, 98.8, 99.0, 0.0]
    })

st.subheader("📋 US Ingredient Matrix & Formulation Inputs")

edited_df = st.data_editor(
    st.session_state.formulation_data,
    num_rows="dynamic",
    column_config={
        "Ingredient": st.column_config.TextColumn("Raw Material", required=True),
        "Inclusion Rate (lbs)": st.column_config.NumberColumn("Inclusion Rate (lbs)", min_value=0.0, step=10.0, format="%.1f"),
        "Cost per Ton ($)": st.column_config.NumberColumn("Raw Cost / Ton ($)", min_value=0.0, step=5.0, format="$%.2f"),
        "Est. Crude Protein (%)": st.column_config.NumberColumn("Crude Protein (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%")
    },
    use_container_width=True
)

# ---------------------------------------------------------
# Calculations Engine
# ---------------------------------------------------------
edited_df["Cost per lb ($)"] = edited_df["Cost per Ton ($)"] / 2000.0
edited_df["Total Material Cost ($)"] = edited_df["Inclusion Rate (lbs)"] * edited_df["Cost per lb ($)"]
edited_df["Protein Contribution (lbs)"] = (edited_df["Inclusion Rate (lbs)"] * edited_df["Est. Crude Protein (%)"]) / 100.0

total_inclusion_lbs = edited_df["Inclusion Rate (lbs)"].sum()
total_raw_material_cost = edited_df["Total Material Cost ($)"].sum()
total_protein_lbs = edited_df["Protein Contribution (lbs)"].sum()

# Shrinkage & Yield
effective_yield_lbs = total_inclusion_lbs * (1.0 - (shrinkage_loss_percent / 100.0))
effective_yield_tons = effective_yield_lbs / 2000.0
estimated_cp_percentage = (total_protein_lbs / total_inclusion_lbs * 100.0) if total_inclusion_lbs > 0 else 0.0

bags_produced = effective_yield_lbs / bag_weight_lbs if bag_weight_lbs > 0 else 0.0
packaging_total = bags_produced * packaging_cost_per_bag

raw_cost_per_ton = (total_raw_material_cost / effective_yield_tons) if effective_yield_tons > 0 else 0.0
total_cost_per_ton = raw_cost_per_ton + milling_power_labor_per_ton + (packaging_total / effective_yield_tons if effective_yield_tons > 0 else 0)
total_cost_per_bag = total_cost_per_ton / (2000.0 / bag_weight_lbs)

target_selling_price_per_bag = target_selling_price_per_ton / (2000.0 / bag_weight_lbs)
total_revenue = effective_yield_tons * target_selling_price_per_ton
total_production_cost = effective_yield_tons * total_cost_per_ton
gross_profit = total_revenue - total_production_cost
profit_margin = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

st.markdown("---")

# ---------------------------------------------------------
# Executive KPI Dashboard
# ---------------------------------------------------------
st.subheader("📊 Executive Financial & Technical Summary (US Standards)")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Effective Yield", f"{effective_yield_tons:,.2f} Short Tons", f"{bags_produced:,.0f} Bags ({bag_weight_lbs:.0f}lbs)")
kpi2.metric("Crude Protein (CP)", f"{estimated_cp_percentage:.2f}%", "Est. Formulation")
kpi3.metric("Production Cost / Ton", f"${total_cost_per_ton:,.2f}", f"${total_cost_per_bag:,.2f} / Bag")
kpi4.metric("Selling Price / Ton", f"${target_selling_price_per_ton:,.2f}", f"${target_selling_price_per_bag:,.2f} / Bag")
kpi5.metric("Gross Profit Margin", f"{profit_margin:.1f}%", f"${gross_profit:,.2f} Net Profit")

st.markdown("---")

# ---------------------------------------------------------
# Visual Analytics
# ---------------------------------------------------------
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("💡 Cost Driver Analysis")
    edited_df["Cost Share (%)"] = (edited_df["Total Material Cost ($)"] / total_raw_material_cost * 100.0).round(1) if total_raw_material_cost > 0 else 0
    st.dataframe(
        edited_df[["Ingredient", "Inclusion Rate (lbs)", "Cost per Ton ($)", "Total Material Cost ($)", "Cost Share (%)"]].sort_values(by="Total Material Cost ($)", ascending=False),
        use_container_width=True
    )

with col_right:
    st.subheader("📈 Cost per Ton Breakdown ($)")
    cost_structure = pd.DataFrame({
        "Component": ["Raw Materials", "Grinding & Power", "Bagging & Tagging"],
        "Amount ($)": [raw_cost_per_ton, milling_power_labor_per_ton, (packaging_total / effective_yield_tons if effective_yield_tons > 0 else 0)]
    })
    st.bar_chart(cost_structure.set_index("Component"))

# ---------------------------------------------------------
# Commercial Export Suite
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📄 Commercial Export Suite")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    csv_buffer = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Formulation Matrix (CSV)",
        data=csv_buffer,
        file_name="feedmillpro_us_formulation_sheet.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp2:
    summary_text = f"""FEEDMILLPRO USA - EXECUTIVE BATCH AUDIT REPORT
==================================================
Batch Target: {batch_size_tons:,.2f} Short Tons ({batch_size_lbs:,.0f} lbs)
Effective Yield: {effective_yield_tons:,.2f} Short Tons ({bags_produced:,.0f} Bags @ {bag_weight_lbs:.0f} lbs/bag)
Estimated Crude Protein (CP): {estimated_cp_percentage:.2f}%
Moisture/Shrinkage Loss Allowance: {shrinkage_loss_percent}%

UNIT COST ANALYSIS (USD):
- Raw Ingredient Cost / Ton: ${raw_cost_per_ton:,.2f}
- Milling, Power & Direct Labor / Ton: ${milling_power_labor_per_ton:,.2f}
- Packaging, Sacks & Tagging / Ton: ${(packaging_total / effective_yield_tons if effective_yield_tons > 0 else 0):,.2f}
--------------------------------------------------
TOTAL PRODUCTION COST / SHORT TON: ${total_cost_per_ton:,.2f}
TOTAL COST PER {bag_weight_lbs:.0f}lb BAG: ${total_cost_per_bag:,.2f}

PROFITABILITY & MARGINS:
- Target Selling Price / Short Ton: ${target_selling_price_per_ton:,.2f}
- Target Selling Price / Bag: ${target_selling_price_per_bag:,.2f}
- Gross Margin / Short Ton: ${(target_selling_price_per_ton - total_cost_per_ton):,.2f}
- Total Batch Profit: ${gross_profit:,.2f}
- Gross Margin Percentage: {profit_margin:.2f}%
==================================================
Generated via FeedMillPro USA Suite
"""
    st.download_button(
        label="📄 Download US Executive Batch Audit (TXT)",
        data=summary_text,
        file_name="feedmillpro_us_batch_audit.txt",
        mime="text/plain",
        use_container_width=True
    )
