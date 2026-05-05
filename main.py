import streamlit as st
import pandas as pd
import time
from backend import preprocess, reconcile, fuzzy_match, highlight_excel

# =========================
# 🎨 CUSTOM UI STYLING & ANIMATIONS
# =========================
st.set_page_config(page_title="Intercompany Reconciliation", page_icon="💼", layout="wide")

st.markdown("""
<style>
/* 1. Smooth Fade-In Animation for the entire app */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}
.main {
    background-color: #F8FAFC;
    animation: fadeIn 0.8s ease-out;
}

/* 2. Modern Gradient Header */
h1 {
    background: -webkit-linear-gradient(45deg, #0F172A, #3B82F6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    padding-bottom: 5px;
}

/* 3. Sleek Metric Cards with Hover Animation */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border-top: 4px solid #3B82F6;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* 4. Styled Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    border-bottom: 2px solid #E2E8F0;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    gap: 10px;
    padding-top: 10px;
    padding-bottom: 10px;
    font-weight: 600;
    transition: color 0.3s ease;
}

/* 5. Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
    box-shadow: 2px 0 5px rgba(0,0,0,0.02);
}

/* 6. Animated Download Button */
.stDownloadButton button {
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 24px;
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
    transition: all 0.3s ease;
}
.stDownloadButton button:hover {
    transform: scale(1.03);
    box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
    color: white;
}
</style>
""", unsafe_allow_html=True)


# =========================
# STREAMLIT UI (ENTERPRISE VERSION)
# =========================
def run_streamlit():

    # Header Section
    st.title("💼 Intercompany Reconciliation Dashboard")
    st.markdown("##### *Smart Matching • Automated Analysis • Audit Ready*")
    st.write("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("Adjust your matching parameters and upload ledgers.")
        
        threshold = st.slider("Fuzzy Matching Threshold", 70, 100, 85, help="Higher values require stricter text matches.")
        
        st.divider()
        st.subheader("📁 Upload Files")
        file_a = st.file_uploader("Upload Company A Ledger", type=["xlsx"])
        file_b = st.file_uploader("Upload Company B Ledger", type=["xlsx"])

    # Main Area Logic
    if not file_a or not file_b:
        # Empty State Welcome Screen
        st.info("👋 **Welcome!** Please upload both Company A and Company B Excel files in the sidebar to begin the reconciliation process.")
        
    else:
        # Simulated Processing Animation (Enterprise Feel)
        with st.spinner("🔄 AI is analyzing and matching your datasets..."):
            df_a = pd.read_excel(file_a)
            df_b = pd.read_excel(file_b)

            # Call backend logic
            df_a_clean = preprocess(df_a)
            df_b_clean = preprocess(df_b)
            result = reconcile(df_a_clean, df_b_clean)
            
            # Brief pause purely for smooth UI transition UX
            time.sleep(0.5) 

        st.toast("✅ Reconciliation Complete!", icon="🎉")

        # =========================
        # 📊 KPI METRICS
        # =========================
        summary = result["Status"].value_counts()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("✅ Matched", int(summary.get("MATCHED", 0)))
        col2.metric("⚠️ Amount Mismatch", int(summary.get("AMOUNT MISMATCH", 0)))
        col3.metric("❌ Missing in A", int(summary.get("MISSING IN A", 0)))
        col4.metric("❌ Missing in B", int(summary.get("MISSING IN B", 0)))

        st.write("---")

        # =========================
        # 📑 TABS
        # =========================
        tab1, tab2, tab3 = st.tabs(["📄 Full Data", "⚠️ Discrepancies", "🤖 Fuzzy Matches"])

        # Full Data
        with tab1:
            st.markdown("### Complete Reconciliation Ledger")
            st.dataframe(result, use_container_width=True, height=400)

        # Issues Only
        with tab2:
            st.markdown("### Unmatched & Discrepancy Records")
            issues = result[result["Status"] != "MATCHED"]
            if issues.empty:
                st.success("No issues found! All records matched perfectly.")
            else:
                st.dataframe(issues, use_container_width=True, height=400)

        # Fuzzy Matches
        with tab3:
            st.markdown(f"### Fuzzy Matches (Threshold: {threshold}%)")
            fuzzy_df = fuzzy_match(df_a_clean, df_b_clean, threshold)
            if fuzzy_df.empty:
                st.info("No fuzzy matches found at the current threshold.")
            else:
                st.dataframe(fuzzy_df, use_container_width=True, height=400)

        st.write("---")

        # =========================
        # 📥 DOWNLOAD
        # =========================
        st.markdown("### Export Results")
        output_file = "reconciliation_output.xlsx"
        
        # Format excel via backend
        highlight_excel(result, output_file)

        with open(output_file, "rb") as f:
            st.download_button(
                label="📥 Download Styled Excel Report",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_streamlit()
