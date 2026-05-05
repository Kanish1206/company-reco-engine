import streamlit as st
import pandas as pd
import time
from backend import preprocess, reconcile, fuzzy_match, highlight_excel

# =========================
# 🎨 ADVANCED CUSTOM UI & ANIMATIONS
# =========================
st.set_page_config(page_title="Intercompany Reconciliation", page_icon="⚡", layout="wide")

st.markdown("""
<style>
/* Global Background & Font */
.stApp {
    background-color: #f4f7f6;
    font-family: 'Inter', sans-serif;
}

/* Staggered Fade-In & Slide-Up Animations */
@keyframes slideUpFade {
    0% { opacity: 0; transform: translateY(30px); }
    100% { opacity: 1; transform: translateY(0); }
}

.main .block-container > div {
    animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
}

/* Staggering the main containers */
.main .block-container > div:nth-child(1) { animation-delay: 0.1s; }
.main .block-container > div:nth-child(2) { animation-delay: 0.2s; }
.main .block-container > div:nth-child(3) { animation-delay: 0.3s; }
.main .block-container > div:nth-child(4) { animation-delay: 0.4s; }
.main .block-container > div:nth-child(5) { animation-delay: 0.5s; }

/* Animated Shimmer Gradient Header */
@keyframes gradientShimmer {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
h1 {
    background: linear-gradient(270deg, #1E3A8A, #3B82F6, #06B6D4, #1E3A8A);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShimmer 4s ease infinite;
    font-weight: 900 !important;
    letter-spacing: -1px;
}

/* Glassmorphism Metric Cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.5);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    border-left: 5px solid #3B82F6;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
[data-testid="stMetric"]:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 15px 35px 0 rgba(31, 38, 135, 0.15);
    border-left: 5px solid #06B6D4;
}

/* Sleek Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: #ffffff;
    padding: 10px 10px 0 10px;
    border-radius: 12px 12px 0 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0px 0px;
    padding: 10px 20px;
    transition: all 0.3s ease;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #eff6ff;
    color: #1d4ed8;
    border-bottom: 3px solid #3B82F6;
}

/* Pulsing Animated Download Button */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
    70% { box-shadow: 0 0 0 15px rgba(59, 130, 246, 0); }
    100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}
.stDownloadButton button {
    background: linear-gradient(135deg, #2563EB 0%, #06B6D4 100%);
    color: white;
    border-radius: 30px;
    border: none;
    padding: 12px 30px;
    font-size: 16px;
    font-weight: 700;
    animation: pulseGlow 2s infinite;
    transition: transform 0.3s ease;
}
.stDownloadButton button:hover {
    transform: translateY(-2px) scale(1.05);
    color: white;
}
</style>
""", unsafe_allow_html=True)


# =========================
# STREAMLIT UI (ENTERPRISE VERSION)
# =========================
def run_streamlit():

    # Header Section
    st.title("⚡ Recon-X Dashboard")
    st.markdown("##### *Smart Matching • Audit Ready*")
    st.write("---")

    # Configuration & Uploads Area (Sidebar Removed completely)
    st.markdown("### ⚙️ Configuration & Uploads")
    
    # Threshold slider is now safely defined in the main flow
    threshold = st.slider("Fuzzy Matching Threshold", 70, 100, 85, help="Higher values require stricter text matches.")
    
    st.markdown("<br>", unsafe_allow_html=True) # Little spacing
    
    upload_col1, upload_col2 = st.columns(2)
    with upload_col1:
        file_a = st.file_uploader("Upload Company A Ledger 📄", type=["xlsx"])
    with upload_col2:
        file_b = st.file_uploader("Upload Company B Ledger 📄", type=["xlsx"])
        
    st.write("---")

    # Main Area Logic
    if not file_a or not file_b:
        # Empty State Welcome Screen
        with st.container():
            st.info("👋 **Welcome to Recon-X!** Please adjust your threshold and upload both Excel files above to initiate the reconciliation engine.")
            st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
        
    else:
        # Simulated Processing Animation with Progress Bar
        progress_text = "🔄 AI Engine Initializing..."
        my_bar = st.progress(0, text=progress_text)
        
        for percent_complete in range(100):
            time.sleep(0.01) # Simulate progress
            if percent_complete == 30:
                my_bar.progress(percent_complete + 1, text="📊 Preprocessing datasets...")
            elif percent_complete == 60:
                my_bar.progress(percent_complete + 1, text="🧠 Executing reconciliation algorithms...")
            else:
                my_bar.progress(percent_complete + 1)
                
        my_bar.empty() # Clear progress bar when done

        with st.spinner("Finalizing results..."):
            df_a = pd.read_excel(file_a)
            df_b = pd.read_excel(file_b)

            # Call backend logic
            df_a_clean = preprocess(df_a)
            df_b_clean = preprocess(df_b)
            result = reconcile(df_a_clean, df_b_clean)

        st.toast("Reconciliation Engine Complete!", icon="🚀")

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
            st.dataframe(result, use_container_width=True, height=450)

        # Issues Only
        with tab2:
            st.markdown("### Unmatched & Discrepancy Records")
            issues = result[result["Status"] != "MATCHED"]
            if issues.empty:
                st.success("✨ **Perfect Match!** No issues found in the datasets.")
            else:
                st.dataframe(issues, use_container_width=True, height=450)

        # Fuzzy Matches
        with tab3:
            st.markdown(f"### Fuzzy Matches (Threshold: **{threshold}%**)")
            fuzzy_df = fuzzy_match(df_a_clean, df_b_clean, threshold)
            if fuzzy_df.empty:
                st.info(f"No fuzzy matches found at the {threshold}% threshold.")
            else:
                st.dataframe(fuzzy_df, use_container_width=True, height=450)

        st.write("---")

        # =========================
        # 📥 DOWNLOAD
        # =========================
        st.markdown("### Export Intelligence Report")
        output_file = "reconciliation_output.xlsx"
        
        # Format excel via backend
        highlight_excel(result, output_file)

        with open(output_file, "rb") as f:
            st.download_button(
                label="⬇️ Download Styled Excel Report",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_streamlit()
