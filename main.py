import streamlit as st
import pandas as pd
from backend import preprocess, reconcile, fuzzy_match, highlight_excel

# =========================
# 🎨 CUSTOM UI STYLING
# =========================
st.set_page_config(page_title="Intercompany Reconciliation", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
h1 {
    color: #1f4e79;
}
.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# =========================
# STREAMLIT UI (PRO VERSION)
# =========================
def run_streamlit():

    st.title("💼 Intercompany Reconciliation Dashboard")
    st.caption("Smart Matching | Automated Analysis | Audit Ready")

    # Sidebar
    st.sidebar.header("⚙️ Settings")
    
    # I uncommented this because it is required for the fuzzy_match function later!
    threshold = st.sidebar.slider("Fuzzy Matching Threshold", 70, 100, 85)

    file_a = st.sidebar.file_uploader("Upload Company A File", type=["xlsx"])
    file_b = st.sidebar.file_uploader("Upload Company B File", type=["xlsx"])

    if file_a and file_b:

        df_a = pd.read_excel(file_a)
        df_b = pd.read_excel(file_b)

        # Call backend logic
        df_a_clean = preprocess(df_a)
        df_b_clean = preprocess(df_b)
        result = reconcile(df_a_clean, df_b_clean)

        # =========================
        # 📊 KPI METRICS
        # =========================
        summary = result["Status"].value_counts()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("✅ Matched", int(summary.get("MATCHED", 0)))
        col2.metric("⚠️ Mismatch", int(summary.get("AMOUNT MISMATCH", 0)))
        col3.metric("❌ Missing A", int(summary.get("MISSING IN A", 0)))
        col4.metric("❌ Missing B", int(summary.get("MISSING IN B", 0)))

        st.divider()

        # =========================
        # 📑 TABS
        # =========================
        tab1, tab2, tab3 = st.tabs(["📄 Full Data", "❌ Issues", "🤖 Fuzzy Matches"])

        # Full Data
        with tab1:
            st.dataframe(result, use_container_width=True)

        # Issues Only
        with tab2:
            issues = result[result["Status"] != "MATCHED"]
            st.dataframe(issues, use_container_width=True)

        # Fuzzy Matches
        with tab3:
            fuzzy_df = fuzzy_match(df_a_clean, df_b_clean, threshold)
            st.dataframe(fuzzy_df, use_container_width=True)

        # =========================
        # 📥 DOWNLOAD
        # =========================
        output_file = "reconciliation_output.xlsx"
        
        # Format excel via backend
        highlight_excel(result, output_file)

        with open(output_file, "rb") as f:
            st.download_button(
                label="📥 Download Styled Excel Report",
                data=f,
                file_name=output_file
            )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_streamlit()
