import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# ---------- Setup ----------
st.set_page_config(page_title="🎫 IT Ticket Classifier", layout="centered")
st.title("🎫 IT Support Ticket Classifier")
load_dotenv()

# ---------- Constants ----------
CATEGORY_FILE = "categories_fixed.xlsx"

# ---------- Step 1: Handle Missing Excel Upload ----------
if not os.path.exists(CATEGORY_FILE):
    st.warning("⚠️ 'categories_fixed.xlsx' not found. Please upload it to proceed.")
    uploaded_file = st.file_uploader("📁 Upload Category & Subcategory Excel File", type=["xlsx"])
    if uploaded_file is not None:
        with open(CATEGORY_FILE, "wb") as f:
            f.write(uploaded_file.read())
        st.success("✅ File uploaded. Please reload the app manually (Ctrl + R).")
    st.stop()

# ---------- Step 2: Load Category/Subcategory Data ----------
try:
    df = pd.read_excel(CATEGORY_FILE)
    if "Category" not in df.columns or "Subcategory" not in df.columns:
        st.error("❌ Excel must have 'Category' and 'Subcategory' columns.")
        st.stop()
    category_str = "\n".join(sorted(df["Category"].unique()))
    subcategory_str = "\n".join([f"{row['Category']} - {row['Subcategory']}" for _, row in df.iterrows()])
except Exception as e:
    st.error(f"❌ Failed to read the Excel file. Error: {e}")
    st.stop()

# ---------- Step 3: Setup LLM Chain ----------
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

system_message = f"""You are an expert at classifying IT support tickets.
Classify each ticket into one of the following categories and subcategories.

Categories:
{category_str}

Subcategories:
{subcategory_str}

Respond in this format:
Category: <category>
Subcategory: <subcategory>
Use only the provided values.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{ticket_description}")
])

chat_history = StreamlitChatMessageHistory(key="ticket_chat")
chain = RunnableWithMessageHistory(
    prompt | llm,
    lambda session_id: chat_history,
    input_messages_key="ticket_description",
    history_messages_key="history"
)

# ---------- Step 4: User Input ----------
ticket_description = st.text_area("📝 Enter Ticket Description")

if st.button("🔍 Classify"):
    if ticket_description.strip():
        with st.spinner("Classifying..."):
            try:
                response = chain.invoke(
                    {"ticket_description": ticket_description},
                    config={"configurable": {"session_id": "ticket_session"}}
                )
                 # Extract tokens
                usage = response.usage_metadata
                input_tokens = usage.get("input_tokens", "N/A")
                output_tokens = usage.get("output_tokens", "N/A")
                content = getattr(response, "content", str(response))

                # Extract result
                category, subcategory = "", ""
                for line in content.splitlines():
                    if line.lower().startswith("category:"):
                        category = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("subcategory:"):
                        subcategory = line.split(":", 1)[1].strip()

                st.success("✅ Classification Complete")
                st.table(pd.DataFrame([{"Category": category, "Subcategory": subcategory}]))
                st.markdown(f"**Input Tokens:** {input_tokens}")
                st.markdown(f"**Output Tokens:** {output_tokens}")
            except Exception as e:
                st.error(f"❌ Classification failed: {e}")
    else:
        st.warning("Please enter a ticket description.")

st.markdown("---")

# ---------- Step 5: Bottom-Left Navigation Button ----------
st.markdown(
    """
    <style>
    .fixed-bottom-left {
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
    }
    </style>
    <div class="fixed-bottom-left">
        <form action="?page=Upload_Categories" method="get">
            <button style="padding: 0.5em 1em; font-size: 14px;">📁 Manage Categories</button>
        </form>
    </div>
    """,
    unsafe_allow_html=True
)
