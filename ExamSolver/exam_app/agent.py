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