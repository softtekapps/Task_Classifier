import streamlit as st
import os
import pandas as pd

# Constants
UPLOAD_DIR = "categories"
SAVE_AS = "categories_fixed.xlsx"
REQUIRED_COLUMNS = {"category", "subcategory"}

# Ensure upload folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("📤 Upload Categories File")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Read file
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.lower()  # Normalize to lowercase

        # Validate columns
        if REQUIRED_COLUMNS.issubset(df.columns):
            save_path = os.path.join(UPLOAD_DIR, SAVE_AS)
            df.to_excel(save_path, index=False)
            st.success("✅ File uploaded successfully and saved as 'categories_fixed.xlsx'")
        else:
            st.error("❌ File must contain 'category' and 'subcategory' columns.")
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")

# Show saved file (if it exists and is valid)
saved_path = os.path.join(UPLOAD_DIR, SAVE_AS)
if os.path.exists(saved_path):
    try:
        df = pd.read_excel(saved_path)
        df.columns = df.columns.str.lower()
        if REQUIRED_COLUMNS.issubset(df.columns):
            st.subheader(f"📂 Showing: {SAVE_AS}")
            st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Error loading saved file: {e}")
