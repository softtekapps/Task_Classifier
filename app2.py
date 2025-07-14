import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory


# Load environment variables
load_dotenv()

# ---------- Fixed Category/Subcategory Data ----------
@st.cache_data
def load_fixed_category_data():
    df = pd.read_excel("categories_fixed.xlsx")  # Your full category/subcategory file
    category_list = "\n".join(sorted(df["Category"].unique()))
    subcategory_list = "\n".join([f"{row['Category']} - {row['Subcategory']}" for _, row in df.iterrows()])
    return df, category_list, subcategory_list

category_df, category_str, subcategory_str = load_fixed_category_data()

# ---------- LLM and Prompt Setup ----------
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

system_message = f"""You are an expert at classifying IT support tickets. 
Classify each incoming ticket into the most appropriate category and subcategory.
Use only the following:

Categories:
{category_str}

Subcategories:
{subcategory_str}

Respond in this format:
Category: <category>
Subcategory: <subcategory>
stricly use the provided categories and subcategories only.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{ticket_description}")
])

# ---------- Memory with Runnable ----------
chat_history = StreamlitChatMessageHistory(key="ticket_chat")
chain = RunnableWithMessageHistory(
    prompt | llm,
    lambda session_id: chat_history,
    input_messages_key="ticket_description",
    history_messages_key="history"
)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="IT Ticket Classifier", layout="centered")
st.title("🎫 IT Support Ticket Classifier")

ticket_description = st.text_area("📝 Enter Ticket Description")

if st.button("🔍 Classify"):
    if ticket_description.strip():
        with st.spinner("Classifying..."):
            response = chain.invoke(
                {"ticket_description": ticket_description},
                config={"configurable": {"session_id": "ticket_session"}}
            )

            # Extract response content
            if hasattr(response, "content"):
                content = response.content
            else:
                content = str(response)

            # Parse and display result
            category, subcategory = "", ""
            for line in content.splitlines():
                if line.lower().startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                elif line.lower().startswith("subcategory:"):
                    subcategory = line.split(":", 1)[1].strip()

            df = pd.DataFrame([{"Category": category, "Subcategory": subcategory}])
            st.success("✅ Classification Complete")
            st.table(df)
    else:
        st.warning("Please enter a ticket description.")

st.markdown("---")
