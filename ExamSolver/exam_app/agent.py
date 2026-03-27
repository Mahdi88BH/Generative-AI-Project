import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOllama



class AgentState(TypedDict):
    raw_text: str
    cleaned_text: str
    solution: str

llm = ChatOllama(
    model="phi3",  
    temperature=0.2,
)
def clean_text_node(state: AgentState):
    prompt = (
        "Tu es un expert en correction d'OCR. Voici un texte brut extrait d'un examen. "
        "Corrige les erreurs de lecture, reformule les phrases si nécessaire et liste "
        "clairement les questions posées.\n\n"
        f"TEXTE BRUT : {state['raw_text']}"
    )
    response = llm.invoke(prompt)
    return {"cleaned_text": response.content}
