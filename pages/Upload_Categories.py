import streamlit as st
import os
import pandas as pd
import tiktoken # Import tiktoken

# --- Constants ---
UPLOAD_DIR = "categories"
SAVE_AS = "categories_fixed.xlsx"
REQUIRED_COLUMNS = {"category", "subcategory"}
# List of columns for which to calculate and display token counts
COLUMNS_TO_COUNT_TOKENS = ["category", "subcategory", "examples"] # Added 'examples' back assuming it's the description-like column

# Ensure upload folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Token Counting Function ---
@st.cache_data # Cache the tokenizer for performance
def get_encoder(encoding_name="cl100k_base"):
    """Returns the tiktoken encoder for a given encoding name."""
    try:
        return tiktoken.get_encoding(encoding_name)
    except Exception as e:
        st.error(f"Error loading tiktoken encoder '{encoding_name}': {e}. Please ensure tiktoken is installed and the encoding name is correct.")
        return None # Return None if encoder can't be loaded

def count_tokens(text, encoder):
    """Counts tokens using a tiktoken encoder."""
    if encoder is None: # If encoder failed to load, return 0
        return 0
    if pd.isna(text): # Handle NaN or None values gracefully
        return 0
    return len(encoder.encode(str(text))) # Ensure text is string for encoding

# --- Streamlit App ---
st.title("📤 Upload Categories File")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Read file
        df = pd.read_excel(uploaded_file)
        # Normalize to lowercase AND strip whitespace for all column names
        df.columns = df.columns.str.lower().str.strip()

        # Validate columns
        if REQUIRED_COLUMNS.issubset(df.columns):
            save_path = os.path.join(UPLOAD_DIR, SAVE_AS)
            df.to_excel(save_path, index=False)
            st.success("✅ File uploaded successfully and saved as 'categories_fixed.xlsx'")
        else:
            missing_cols = REQUIRED_COLUMNS - set(df.columns)
            st.error(f"❌ File must contain 'category' and 'subcategory' columns. Missing: {', '.join(missing_cols)}")
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")

# Show saved file (if it exists and is valid)
saved_path = os.path.join(UPLOAD_DIR, SAVE_AS)
if os.path.exists(saved_path):
    try:
        df = pd.read_excel(saved_path)
        df.columns = df.columns.str.lower().str.strip() # Normalize columns for the saved file as well

        if REQUIRED_COLUMNS.issubset(df.columns):
            st.subheader(f"📂 Showing: {SAVE_AS}")
            st.dataframe(df) # Display the original DataFrame first

            # --- Display Total Counts for Category and Subcategory Combinations ---
            st.subheader("📊 Combined Category-Subcategory Count")

            # Create a combined string for category and subcategory
            # Ensure they are strings before combining to handle potential non-string types
            df['category_subcategory_combined'] = df['category'].astype(str) + " - " + df['subcategory'].astype(str)
            total_unique_combinations = df['category_subcategory_combined'].nunique()

            st.metric("Total Unique Category-Subcategory Combinations", total_unique_combinations)

            # Optional: You can still show individual counts if desired
            if st.checkbox("Show individual category/subcategory counts"):
                col1, col2 = st.columns(2)
                total_categories = df['category'].nunique()
                total_subcategories = df['subcategory'].nunique()
                col1.metric("Total Unique Categories", total_categories)
                col2.metric("Total Unique Subcategories", total_subcategories)


            st.subheader("📊 Token Counts for Specified Columns")

            # Initialize encoder once
            encoder = get_encoder()

            if encoder: # Only proceed if encoder was loaded successfully
                # Create a list to hold columns to display in the token count dataframe
                columns_to_display = []
                # Flag to check if any relevant column was found
                relevant_column_found = False

                for col_name in COLUMNS_TO_COUNT_TOKENS:
                    if col_name in df.columns:
                        relevant_column_found = True
                        # Apply token counting to the current column
                        df[f'{col_name}_tokens'] = df[col_name].apply(lambda x: count_tokens(x, encoder))
                        columns_to_display.extend([col_name, f'{col_name}_tokens'])
                    else:
                        st.info(f"Column '{col_name}' not found in the uploaded file. Skipping token count for it.")

                if relevant_column_found:
                    if st.button("Display All Calculated Token Counts"):
                        st.dataframe(df[columns_to_display])
                else:
                    st.info("No specified columns (category, subcategory, examples) were found in the file to count tokens for.")
            else:
                st.warning("Token counting functionality is disabled due to an encoder loading error.")

    except Exception as e:
        st.error(f"❌ Error loading saved file: {e}")

# import streamlit as st
# import os
# import pandas as pd
# import tiktoken # Import tiktoken

# # --- Constants ---
# UPLOAD_DIR = "categories"
# SAVE_AS = "categories_fixed.xlsx"
# REQUIRED_COLUMNS = {"category", "subcategory"}
# DESCRIPTION_COLUMN = "examples " # New constant for the description column

# # Ensure upload folder exists
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # --- Token Counting Function ---
# @st.cache_data # Cache the tokenizer for performance
# def get_encoder(encoding_name="cl100k_base"):
#     """Returns the tiktoken encoder for a given encoding name."""
#     return tiktoken.get_encoding(encoding_name)

# def count_tokens(text, encoder):
#     """Counts tokens using a tiktoken encoder."""
#     if pd.isna(text): # Handle NaN or None values gracefully
#         return 0
#     return len(encoder.encode(str(text))) # Ensure text is string for encoding

# # --- Streamlit App ---
# st.title("📤 Upload Categories File")

# uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# if uploaded_file:
#     try:
#         # Read file
#         df = pd.read_excel(uploaded_file)
#         df.columns = df.columns.str.lower()  # Normalize to lowercase

#         # Validate columns
#         if REQUIRED_COLUMNS.issubset(df.columns):
#             save_path = os.path.join(UPLOAD_DIR, SAVE_AS)
#             df.to_excel(save_path, index=False)
#             st.success("✅ File uploaded successfully and saved as 'categories_fixed.xlsx'")
#         else:
#             st.error("❌ File must contain 'category' and 'subcategory' columns.")
#     except Exception as e:
#         st.error(f"❌ Error reading Excel file: {e}")

# # Show saved file (if it exists and is valid)
# saved_path = os.path.join(UPLOAD_DIR, SAVE_AS)
# if os.path.exists(saved_path):
#     try:
#         df = pd.read_excel(saved_path)
#         df.columns = df.columns.str.lower()
#         print(df.columns)  # Debugging line to check columns

#         if REQUIRED_COLUMNS.issubset(df.columns):
#             st.subheader(f"📂 Showing: {SAVE_AS}")
#             st.dataframe(df) # Display the original DataFrame first

#             # --- New: Token Count Button and Display ---
#             if DESCRIPTION_COLUMN in df.columns:
#                 if st.button(f"Display Token Counts for '{DESCRIPTION_COLUMN}'"):
#                     st.info(f"Counting tokens using '{get_encoder().name}' encoding (typically for GPT-3.5/GPT-4 models).")

#                     # Get the encoder once
#                     encoder = get_encoder()

#                     # Apply token counting to the description column
#                     # Use .apply() for efficient row-wise operation
#                     df[f'{DESCRIPTION_COLUMN}_tokens'] = df[DESCRIPTION_COLUMN].apply(lambda x: count_tokens(x, encoder))

#                     st.subheader(f"📊 {DESCRIPTION_COLUMN} with Token Counts")
#                     st.dataframe(df[[DESCRIPTION_COLUMN, f'{DESCRIPTION_COLUMN}_tokens']])
#             else:
#                 st.info(f"No '{DESCRIPTION_COLUMN}' column found to count tokens.")

#     except Exception as e:
#         st.error(f"❌ Error loading saved file: {e}")
