import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Assembly Quality Dashboard",
    layout="wide"
)

# -------------------------
# LOAD DATA
# -------------------------
bom_cluster_rate = pd.read_csv("bom_cluster_rate.csv")
cluster_pareto = pd.read_csv("cluster_pareto.csv")
shift_cluster_rate = pd.read_csv("shift_cluster_rate.csv")

# -------------------------
# COLORS (Greaves style)
# -------------------------
PRIMARY_BLUE = "#003A8F"
ACCENT_BLUE = "#1F77B4"
ALERT_RED = "#D62728"
NEUTRAL_GREY = "#6C757D"

# -------------------------
# KPI CALCULATIONS
# -------------------------
total_engines = bom_cluster_rate["Total_Engines"].sum()
total_defects = cluster_pareto["NG_Count"].sum()
ng_per_engine = total_defects / total_engines

assembly_pct = cluster_pareto.loc[
    cluster_pareto["Cluster_Name"] == "Assembly Discipline", "NG_Count"
].values[0] / total_defects

# -------------------------
# HEADER
# -------------------------
st.title("Assembly Quality Intelligence Dashboard")
st.markdown("### Greaves Cotton")

# -------------------------
# KPI SECTION
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Engines", f"{total_engines}")
col2.metric("Total Defects", f"{total_defects}")
col3.metric("NG per Engine", f"{ng_per_engine:.2f}")
col4.metric("Assembly Contribution", f"{assembly_pct*100:.1f}%")

# -------------------------
# FAILURE MODE CHART
# -------------------------
st.subheader("Failure Mode Breakdown")

fig1 = px.bar(
    cluster_pareto,
    x="NG_per_Engine",
    y="Cluster_Name",
    orientation="h",
    color="Cluster_Name",
    color_discrete_map={
        "Assembly Discipline": ALERT_RED
    }
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# BOM PERFORMANCE
# -------------------------
st.subheader("BOM Performance (NG per Engine)")

fig2 = px.bar(
    bom_cluster_rate,
    x="BOM",
    y="NG_per_Engine",
    color="NG_per_Engine",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# HEATMAP
# -------------------------
st.subheader("BOM vs Failure Mode")

heatmap_data = bom_cluster_rate.pivot(
    index="BOM",
    columns="Cluster_Name",
    values="NG_per_Engine"
)

fig3 = px.imshow(
    heatmap_data,
    text_auto=True,
    color_continuous_scale="Reds"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# SHIFT ANALYSIS
# -------------------------
st.subheader("Shift Performance")

fig4 = px.bar(
    shift_cluster_rate,
    x="Shift",
    y="NG_per_Engine",
    color="Cluster_Name",
    barmode="group"
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------
# INSIGHTS (RULE ENGINE)
# -------------------------
st.subheader("Key Insights")

insights = []

if assembly_pct > 0.7:
    insights.append("Majority of defects are driven by lack of process control.")

insights.append("Critical fastening defects pose high functional risk.")
insights.append("Model-wise variation indicates process instability.")
insights.append("Shift variation indicates training gaps.")

for i in insights:
    st.markdown(f"- {i}")

# -------------------------
# ACTIONS
# -------------------------
st.subheader("Recommended Actions")

st.markdown("""
**Immediate**
- Enforce assembly checklist
- Audit torque tools

**Short Term**
- Operator training
- Improve SOPs

**Long Term**
- Introduce poka-yoke systems
- Digital validation
""")
