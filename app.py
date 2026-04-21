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
# CUSTOM STYLING
# -------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}
h1, h2, h3 {
    color: #003A8F;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    bom = pd.read_csv("bom_cluster_rate.csv")
    cluster = pd.read_csv("cluster_pareto.csv")
    shift = pd.read_csv("shift_cluster_rate.csv")
    return bom, cluster, shift

bom_cluster_rate, cluster_pareto, shift_cluster_rate = load_data()

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("Filters")

selected_boms = st.sidebar.multiselect(
    "Select BOM",
    options=bom_cluster_rate["BOM"].unique(),
    default=bom_cluster_rate["BOM"].unique()
)

selected_clusters = st.sidebar.multiselect(
    "Select Failure Modes",
    options=cluster_pareto["Cluster_Name"].unique(),
    default=cluster_pareto["Cluster_Name"].unique()
)

# -------------------------
# APPLY FILTERS
# -------------------------
bom_filtered = bom_cluster_rate[
    bom_cluster_rate["BOM"].isin(selected_boms)
]

cluster_filtered = cluster_pareto[
    cluster_pareto["Cluster_Name"].isin(selected_clusters)
]

shift_filtered = shift_cluster_rate[
    shift_cluster_rate["Cluster_Name"].isin(selected_clusters)
]

# -------------------------
# KPI CALCULATIONS
# -------------------------
total_engines = bom_filtered["Total_Engines"].sum()
total_defects = cluster_filtered["NG_Count"].sum()
ng_per_engine = total_defects / total_engines if total_engines else 0

assembly_pct = 0
if "Assembly Discipline" in cluster_filtered["Cluster_Name"].values:
    assembly_pct = cluster_filtered.loc[
        cluster_filtered["Cluster_Name"] == "Assembly Discipline", "NG_Count"
    ].values[0] / total_defects if total_defects else 0

# -------------------------
# HEADER
# -------------------------
st.title("Assembly Quality Intelligence Dashboard")
st.markdown("### Greaves Cotton")

# -------------------------
# TABS
# -------------------------
tab1, tab2 = st.tabs(["Executive View", "Detailed Analysis"])

# =========================
# TAB 1 — EXECUTIVE VIEW
# =========================
with tab1:

    # KPI SECTION
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Engines", f"{total_engines:,}")
    col2.metric("Total Defects", f"{total_defects:,}")
    col3.metric("NG / Engine", f"{ng_per_engine:.2f}")
    col4.metric("Assembly %", f"{assembly_pct*100:.1f}%")

    st.markdown("---")

    # FAILURE MODE
    st.subheader("Failure Mode Breakdown")

    fig1 = px.bar(
        cluster_filtered.sort_values("NG_per_Engine"),
        x="NG_per_Engine",
        y="Cluster_Name",
        orientation="h",
        color="Cluster_Name",
        color_discrete_map={
            "Assembly Discipline": "#D62728",
            "Critical Fastening": "#FF7F0E",
            "Routing & Interface": "#1F77B4",
            "Fitment Precision": "#6C757D"
        },
        text=cluster_filtered["NG_per_Engine"].round(2)
    )

    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

    # TOP BOM ALERT
    if not bom_filtered.empty:
        top_bom = bom_filtered.nlargest(1, "NG_per_Engine")
        st.warning(f"⚠️ Highest Risk BOM: {top_bom['BOM'].values[0]}")

    # INSIGHTS
    st.subheader("Key Insights")

    if assembly_pct > 0.7:
        st.error("🚨 Majority defects driven by Assembly Discipline")

    st.info("⚠️ Critical fastening defects pose functional risk")
    st.warning("⚙️ Model-wise variation indicates process instability")
    st.success("📊 Shift variation indicates training gaps")

    # ACTIONS
    with st.expander("Recommended Actions"):
        st.markdown("### Immediate")
        st.write("- Enforce assembly checklist")
        st.write("- Audit torque tools")

        st.markdown("### Short Term")
        st.write("- Operator training")
        st.write("- Improve SOPs")

        st.markdown("### Long Term")
        st.write("- Introduce poka-yoke systems")
        st.write("- Digital validation")

# =========================
# TAB 2 — DETAILED ANALYSIS
# =========================
with tab2:

    st.subheader("BOM Performance")

    fig2 = px.bar(
        bom_filtered,
        x="BOM",
        y="NG_per_Engine",
        color="NG_per_Engine",
        color_continuous_scale="Reds",
        text=bom_filtered["NG_per_Engine"].round(2)
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("BOM vs Failure Mode Heatmap")

    heatmap_data = bom_filtered.pivot(
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

    st.subheader("Shift Performance")

    fig4 = px.bar(
        shift_filtered,
        x="Shift",
        y="NG_per_Engine",
        color="Cluster_Name",
        barmode="group"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # DOWNLOAD OPTION
    st.download_button(
        "Download Filtered Data",
        bom_filtered.to_csv(index=False),
        "filtered_bom_data.csv"
    )
