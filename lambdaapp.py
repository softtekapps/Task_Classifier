# app.py

from fastapi import FastAPI
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from mangum import Mangum  # for AWS Lambda
import os
from dotenv import load_dotenv

load_dotenv()

# Dummy fixed categories for demo
category_map = """
Hardware -> Laptop/Desktop Issues: Slow performance, blue screen
Software -> Application Issues: App crashes, login failure
Network -> VPN Issues: VPN not connecting
Access Management -> Password Reset: Forgot password, locked account
"""

# Prompt Template
prompt_template = PromptTemplate(
    input_variables=["ticket_description", "category_map"],
    template="""
You are an expert IT ticket classifier.

Given a ticket description and the known categories, classify it.

Categories and Examples:
{category_map}

Ticket Description: {ticket_description}

Respond in this format:
Category: <category>
"""
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
chain: RunnableSequence = prompt_template | llm

app = FastAPI()
handler = Mangum(app)  # for AWS Lambda

class TicketRequest(BaseModel):
    description: str

@app.post("/classify")
async def classify_ticket(req: TicketRequest):
    response = chain.invoke({
        "ticket_description": req.description,
        "category_map": category_map
    })
    return {"category": response}
