import pandas as pd
import numpy as np
from rapidfuzz import fuzz

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
# RECONCILIATION
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
# FUZZY MATCHING
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
# EXCEL HIGHLIGHT
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
if __name__ == "__main__":
    # 1. Load the Data
    # Replace these filenames with the actual names of your uploaded files
    file_a_path = "dataset_A.xlsx" 
    file_b_path = "dataset_B.xlsx"
    
    df_a_raw = pd.read_excel(file_a_path)
    df_b_raw = pd.read_excel(file_b_path)

    # 2. Standardize Dates (CRITICAL for the merge to work)
    # This strips away weird time formats and forces standard dates
    df_a_raw["Reference Document Date"] = pd.to_datetime(df_a_raw["Reference Document Date"]).dt.date
    df_b_raw["Reference Document Date"] = pd.to_datetime(df_b_raw["Reference Document Date"]).dt.date

    # 3. Preprocess both files
    df_a_clean = preprocess(df_a_raw)
    df_b_clean = preprocess(df_b_raw)

    # 4. Run Reconciliation
    final_reconciliation = reconcile(df_a_clean, df_b_clean)

    # 5. Run Fuzzy Matching on the "Missing" records
    missing_in_a = final_reconciliation[final_reconciliation["Status"] == "MISSING IN A"].copy()
    missing_in_b = final_reconciliation[final_reconciliation["Status"] == "MISSING IN B"].copy()
    
    # We rename columns temporarily so the fuzzy matcher can read them correctly
    missing_in_a.rename(columns={"Reference_B": "Reference", "doc_norm": "doc_norm"}, inplace=True)
    missing_in_b.rename(columns={"Reference_A": "Reference", "doc_norm": "doc_norm"}, inplace=True)

    if not missing_in_a.empty and not missing_in_b.empty:
        print("Running Fuzzy Match on unmatched records...")
        fuzzy_results = fuzzy_match(missing_in_a, missing_in_b, threshold=85)
        print("Fuzzy Match Results:")
        print(fuzzy_results)
        
        # Optional: Save fuzzy matches to a separate CSV/Excel if needed
        # fuzzy_results.to_excel("fuzzy_matches.xlsx", index=False)

    # 6. Export the Highlighted Excel
    output_filename = "Reconciliation_Results.xlsx"
    highlight_excel(final_reconciliation, output_filename)
    print(f"Reconciliation complete! File saved as: {output_filename}")
