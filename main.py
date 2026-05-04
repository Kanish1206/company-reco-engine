import pandas as pd
import numpy as np
from rapidfuzz import fuzz
import streamlit as st

# =========================
# CONFIG
# =========================
TOLERANCE = 5

# =========================
# NORMALIZATION FUNCTION
# =========================
def normalize_doc(series):
    return (
        series.fillna("")
        .astype(str)
        .str.upper()
        .str.replace(r"\s+", "", regex=True)
        .str.replace(r"[^A-Z0-9]", "", regex=True)
        .str.replace("O", "0")
        .str.replace("I", "1")
    )

# =========================
# PREPROCESS
# =========================
def preprocess(df):
    df["doc_norm"] = normalize_doc(df["Reference"])

    return df.groupby(
        ["Reference", "doc_norm", "Reference Document Date"],
        as_index=False
    ).agg({
        "Vendor": "first",
        "Vendor Name": "first",
        "Posting Date": "first",
        "Document No": "first",
        "Debit Amount": "sum",
        "Credit Amount": "sum"
    })

# =========================
# ORIGINAL RECONCILIATION (UNCHANGED LOGIC)
# =========================
def reconcile(df_a, df_b):
    merged = df_a.merge(
        df_b,
        on=["doc_norm", "Reference Document Date"],
        how="outer",
        suffixes=("_A", "_B"),
        indicator=True
    )

    merged["Debit Amount_A"] = merged["Debit Amount_A"].fillna(0)
    merged["Credit Amount_A"] = merged["Credit Amount_A"].fillna(0)
    merged["Debit Amount_B"] = merged["Debit Amount_B"].fillna(0)
    merged["Credit Amount_B"] = merged["Credit Amount_B"].fillna(0)

    merged["Diff_A_vs_B"] = merged["Debit Amount_A"] - merged["Credit Amount_B"]
    merged["Diff_B_vs_A"] = merged["Credit Amount_A"] - merged["Debit Amount_B"]

    merged["Net_Diff"] = abs(merged["Diff_A_vs_B"])

    conditions = [
        (merged["_merge"] == "both") & (merged["Net_Diff"] <= TOLERANCE),
        (merged["_merge"] == "both") & (merged["Net_Diff"] > TOLERANCE),
        (merged["_merge"] == "left_only"),
        (merged["_merge"] == "right_only"),
    ]

    choices = [
        "MATCHED",
        "AMOUNT MISMATCH",
        "MISSING IN B",
        "MISSING IN A",
    ]

    merged["Status"] = np.select(conditions, choices, default="CHECK")

    return merged

# =========================
# 🔥 FUZZY MATCHING (ADDED)
# =========================
def fuzzy_match(df_a, df_b, threshold=85):
    matches = []

    for i, row_a in df_a.iterrows():
        best_score = 0
        best_match = None

        for j, row_b in df_b.iterrows():
            score = fuzz.ratio(row_a["doc_norm"], row_b["doc_norm"])

            if score > best_score:
                best_score = score
                best_match = row_b

        if best_score >= threshold:
            matches.append({
                "Reference_A": row_a["Reference"],
                "Reference_B": best_match["Reference"],
                "Score": best_score
            })

    return pd.DataFrame(matches)

# =========================
# 🎨 EXCEL HIGHLIGHTING (ADDED)
# =========================
def highlight_excel(df, output_file):
    def highlight_status(row):
        if row["Status"] == "MATCHED":
            return ["background-color: lightgreen"] * len(row)
        elif row["Status"] == "AMOUNT MISMATCH":
            return ["background-color: orange"] * len(row)
        elif "MISSING" in row["Status"]:
            return ["background-color: red"] * len(row)
        else:
            return [""] * len(row)

    styled = df.style.apply(highlight_status, axis=1)

    styled.to_excel(output_file, engine="openpyxl", index=False)

# =========================
# 📊 SUMMARY
# =========================
def generate_summary(df):
    return df["Status"].value_counts()

# =========================
# 🌐 STREAMLIT UI (ADDED)
# =========================
def run_streamlit():
    st.title("💼 Intercompany Reconciliation Tool")

    file_a = st.file_uploader("Upload Company A File", type=["xlsx"])
    file_b = st.file_uploader("Upload Company B File", type=["xlsx"])

    if file_a and file_b:
        df_a = pd.read_excel(file_a)
        df_b = pd.read_excel(file_b)

        st.write("Preprocessing...")
        df_a_clean = preprocess(df_a)
        df_b_clean = preprocess(df_b)

        st.write("Reconciling...")
        result = reconcile(df_a_clean, df_b_clean)

        st.write("### 🔍 Summary")
        st.write(generate_summary(result))

        st.write("### 📄 Preview")
        st.dataframe(result.head(50))

        # Fuzzy matches
        st.write("### 🤖 Fuzzy Matches")
        fuzzy_df = fuzzy_match(df_a_clean, df_b_clean)
        st.dataframe(fuzzy_df.head(20))

        # Save Excel
        output_file = "reconciliation_output.xlsx"
        highlight_excel(result, output_file)

        with open(output_file, "rb") as f:
            st.download_button(
                label="📥 Download Excel Report",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# =========================
# MAIN (CLI MODE)
# =========================
def main():
    print("Run using Streamlit:")
    print("👉 streamlit run your_script.py")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_streamlit()