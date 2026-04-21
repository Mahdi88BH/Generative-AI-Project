import os
import httpx
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

# --- CONFIGURATION DE L'ÉTAT ---
class AgentState(TypedDict):
    image_path: str   # Chemin de l'image reçu du dossier temp_exams
    raw_text: str     # Texte brut récupéré via le serveur MCP
    cleaned_text: str # Texte corrigé par le LLM
    solution: str     # Solution finale

# --- INITIALISATION LLM (GROQ) ---
# Assure-toi que GROQ_API_KEY est dans ton .env
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- FONCTION AUXILIAIRE : APPEL AU SERVEUR MCP ---
def call_ocr_mcp_server(path: str) -> str:
    """Communique avec le serveur MCP tournant sur le port 8002"""
    try:
        # On utilise httpx pour appeler l'outil exposé par le serveur MCP
        with httpx.Client() as client:
            response = client.post(
                "http://127.0.0.1:8002/tools/vision_ocr_tool", 
                json={"arguments": {"image_path": path}},
                timeout=30.0
            )
            # On récupère le texte extrait renvoyé par ocr_engine via MCP
            return response.json().get("content", "")
    except Exception as e:
        print(f"⚠️ Erreur de connexion MCP: {e}")
        return f"Erreur de communication avec le serveur OCR : {str(e)}"

# --- NŒUD 1 : CLEANER (OCR + REFORMULATION) ---
def clean_text_node(state: AgentState):
    print("--- [AGENT] Demande d'extraction OCR via MCP... ---")
    
    # 1. On récupère le texte brut depuis le serveur MCP
    extracted_text = call_ocr_mcp_server(state["image_path"])
    
    # 2. On demande au LLM de nettoyer ce texte
    prompt = (
        "Tu es un expert en correction d'OCR. Voici un texte brut extrait d'un examen. "
        "Corrige les erreurs de lecture (fautes de frappe, caractères spéciaux), "
        "ne réponds pas aux questions, liste-les juste clairement.\n\n"
        f"TEXTE BRUT : {extracted_text}"
    )
    
    response = llm.invoke(prompt)
    return {
        "cleaned_text": response.content, 
        "raw_text": extracted_text
    }

# --- NŒUD 2 : SOLVER (RÉSOLUTION PÉDAGOGIQUE) ---
def solve_exam_node(state: AgentState):
    print("--- [AGENT] Résolution de l'examen... ---")
    
    prompt = (
        "Tu es un professeur assistant. Résous les questions d'examen suivantes de manière "
        "claire, étape par étape, en utilisant un ton pédagogique et un format Markdown élégant.\n\n"
        f"QUESTIONS : {state['cleaned_text']}"
    )
    
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- CONSTRUCTION DU WORKFLOW ---
workflow = StateGraph(AgentState)

workflow.add_node("cleaner", clean_text_node)
workflow.add_node("solver", solve_exam_node)

workflow.set_entry_point("cleaner")
workflow.add_edge("cleaner", "solver")
workflow.add_edge("solver", END)

# Compilation de l'agent prêt à être utilisé par main.py
exam_agent = workflow.compile()