from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os

# Load environment variables
load_dotenv()

# Category and subcategory dictionary
categories = {
    "Hardware": ["Desktops/Laptops", "Mobile Devices", "Printers and Scanners"],
    "Software": ["Operating Systems", "Applications", "Email"],
    "Network": ["Connectivity", "Security"],
    "Accounts and Access": ["User Accounts", "Email Accounts", "File and Resource Access"],
    "Services": ["Printing Services", "Database Services", "Web Services"],
    "General": ["Training and Guidance", "Policy and Procedure Enquiries"]
}

# Function to get LLM response
def get_llm_response(ticket_description):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

    prompt_template = """
    You are an expert at classifying IT support tickets.
    Based on the following ticket description, identify the most appropriate category and subcategory from the lists provided.

    Ticket Description: "{ticket_description}"

    Categories:
    {categories}

    Subcategories:
    {subcategories}

    Provide the answer in the following format:
    Category: <category>
    Subcategory: <subcategory>
    """

    prompt = PromptTemplate(
        input_variables=["ticket_description", "categories", "subcategories"],
        template=prompt_template
    )

    category_list = "\n".join([f"- {c}" for c in categories.keys()])
    subcategory_list = "\n".join([f"- {s}" for subs in categories.values() for s in subs])

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({
        "ticket_description": ticket_description,
        "categories": category_list,
        "subcategories": subcategory_list
    })

    return response

# Streamlit UI
st.title("🛠️ IT Support Ticket Classifier")

ticket_description = st.text_area("Enter the ticket description:")

if st.button("Classify Ticket"):
    if ticket_description:
        with st.spinner("Classifying..."):
            response = get_llm_response(ticket_description)

            # Parse response
            category = ""
            subcategory = ""
            for line in response.splitlines():
                if line.lower().startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                elif line.lower().startswith("subcategory:"):
                    subcategory = line.split(":", 1)[1].strip()

            # Display as a table
            df = pd.DataFrame([{"Category": category, "Subcategory": subcategory}])
            st.table(df)
    else:
        st.warning("Please enter a ticket description.")
