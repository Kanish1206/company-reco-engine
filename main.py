import streamlit as st
import pandas as pd
from backend import preprocess, reconcile, fuzzy_match, highlight_excel

# =========================
# 🎨 CLEAN, PROFESSIONAL ENTERPRISE UI
# =========================
st.set_page_config(page_title="Recon-X Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
/* Global Background & Font */
.stApp {
    background-color: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Clean, Corporate Header */
h1 {
    color: #0f172a;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    margin-bottom: 0rem;
}

/* Crisp Metric Cards */
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    border-top: 4px solid #2563eb;
    transition: box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
[data-testid="stMetricValue"] {
    color: #1e293b;
    font-weight: 700;
}

/* Professional Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #e2e8f0;
}
.stTabs [data-baseweb="tab"] {
    padding: 12px 16px;
    color: #64748b;
    font-weight: 600;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #2563eb;
    border-bottom-color: #2563eb;
}

/* Standardized Buttons */
.stDownloadButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 6px;
    border: none;
    padding: 10px 24px;
    font-weight: 600;
    transition: background-color 0.2s ease;
}
.stDownloadButton button:hover {
    background-color: #1d4ed8;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# =========================
# STREAMLIT LOGIC
# =========================
def run_streamlit():

    # Header Section
    st.title("Recon-X Dashboard")
    st.markdown("##### Enterprise Intercompany Reconciliation Engine")
    st.write("---")

    # Configuration & Uploads Area
    st.markdown("### Configuration & Uploads")
    
    threshold = st.slider(
        "Fuzzy Matching Threshold", 
        min_value=70, 
        max_value=100, 
        value=85, 
        help="Higher values require stricter text matches for unstructured data."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    upload_col1, upload_col2 = st.columns(2)
    with upload_col1:
        file_a = st.file_uploader("Upload Company A Ledger (.xlsx)", type=["xlsx"])
    with upload_col2:
        file_b = st.file_uploader("Upload Company B Ledger (.xlsx)", type=["xlsx"])
        
    st.write("---")

    # Main Area Logic
    if not file_a or not file_b:
        st.info("Upload both Company A and Company B ledgers to initiate reconciliation.")
    else:
        # Removed the fake time.sleep() loading bar. Just do the work.
        with st.spinner("Processing ledgers and executing reconciliation algorithms..."):
            df_a = pd.read_excel(file_a)
            df_b = pd.read_excel(file_b)

            df_a_clean = preprocess(df_a)
            df_b_clean = preprocess(df_b)
            result = reconcile(df_a_clean, df_b_clean)

        st.success("Reconciliation completed successfully.")

        # =========================
        # KPI METRICS
        # =========================
        summary = result["Status"].value_counts()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Matched", int(summary.get("MATCHED", 0)))
        col2.metric("Amount Mismatch", int(summary.get("AMOUNT MISMATCH", 0)))
        col3.metric("Missing in A", int(summary.get("MISSING IN A", 0)))
        col4.metric("Missing in B", int(summary.get("MISSING IN B", 0)))

        st.write("---")

        # =========================
        # DATAFRAME STYLING FUNCTION (FIXED ACCESSIBILITY)
        # =========================
        def highlight_status(row):
            status = str(row.get("Status", ""))
            # Using high-contrast, professional status colors
            if status == "MATCHED":
                return ['background-color: #e6f4ea; color: #1e8e3e; font-weight: 500;'] * len(row)
            elif status == "AMOUNT MISMATCH":
                return ['background-color: #fef7e0; color: #b06000; font-weight: 500;'] * len(row)
            elif "MISSING" in status:
                return ['background-color: #fce8e6; color: #c5221f; font-weight: 500;'] * len(row)
            return [''] * len(row)

        # =========================
        # TABS
        # =========================
        tab1, tab2, tab3 = st.tabs(["Full Data", "Discrepancies", "Fuzzy Matches"])

        with tab1:
            st.markdown("#### Complete Reconciliation Ledger")
            styled_result = result.style.apply(highlight_status, axis=1)
            st.dataframe(styled_result, use_container_width=True, height=450)

        with tab2:
            st.markdown("#### Unmatched & Discrepancy Records")
            issues = result[result["Status"] != "MATCHED"]
            if issues.empty:
                st.success("No discrepancies found. Ledgers are fully reconciled.")
            else:
                styled_issues = issues.style.apply(highlight_status, axis=1)
                st.dataframe(styled_issues, use_container_width=True, height=450)

        with tab3:
            st.markdown(f"#### Fuzzy Matches (Threshold: {threshold}%)")
            fuzzy_df = fuzzy_match(df_a_clean, df_b_clean, threshold)
            if fuzzy_df.empty:
                st.info(f"No fuzzy matches found at the {threshold}% threshold.")
            else:
                st.dataframe(fuzzy_df, use_container_width=True, height=450)

        st.write("---")

        # =========================
        # DOWNLOAD
        # =========================
        st.markdown("### Export Report")
        output_file = "reconciliation_output.xlsx"
        
        highlight_excel(result, output_file)

        with open(output_file, "rb") as f:
            st.download_button(
                label="Download Excel Report",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    run_streamlit()
