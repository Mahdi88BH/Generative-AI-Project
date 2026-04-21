import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Chargement des variables d'environnement (pour la clé API)
load_dotenv()

class AgentState(TypedDict):
    raw_text: str
    cleaned_text: str
    solution: str

# Initialisation du LLM via Groq Cloud
# Modèle suggéré : llama-3.3-70b-versatile (très performant pour le raisonnement)
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def clean_text_node(state: AgentState):
    print("--- [AGENT] Nettoyage OCR via Groq ---")
    prompt = (
        "Tu es un expert en correction d'OCR. Voici un texte brut extrait d'un examen.\n"
        "TA MISSION :\n"
        "1. Corrige les fautes de lecture et les caractères spéciaux.\n"
        "2. Identifie et structure clairement les questions.\n"
        "3. Ne réponds rien d'autre que le texte propre.\n\n"
        f"TEXTE BRUT : {state['raw_text']}"
    )
    # On utilise .invoke pour appeler l'API Groq
    response = llm.invoke(prompt)
    return {"cleaned_text": response.content}

def solve_exam_node(state: AgentState):
    print("--- [AGENT] Résolution Académique via Groq ---")
    prompt = (
        "Tu es un professeur universitaire expert. Résous cet examen.\n"
        "CONSIGNES STRICTES :\n"
        "- Pas d'introduction ni de conclusion conversationnelle.\n"
        "- Utilise le format Markdown pour la structure.\n"
        "- Utilise LaTeX ($...$) pour toutes les formules mathématiques.\n"
        "- Explique chaque étape du raisonnement.\n\n"
        f"QUESTIONS : {state['cleaned_text']}"
    )
    response = llm.invoke(prompt)
    return {"solution": response.content}

# Construction du Graph
workflow = StateGraph(AgentState)

workflow.add_node("cleaner", clean_text_node)
workflow.add_node("solver", solve_exam_node)

workflow.set_entry_point("cleaner")
workflow.add_edge("cleaner", "solver")
workflow.add_edge("solver", END)

exam_agent = workflow.compile()