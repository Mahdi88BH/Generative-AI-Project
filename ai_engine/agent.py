import os
import httpx
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

# Chargement impératif des variables d'environnement (.env)
load_dotenv()

# --- CONFIGURATION DE L'ÉTAT ---
class AgentState(TypedDict):
    image_path: str   # Reçu de main.py
    raw_text: str     # Rempli après l'appel MCP
    cleaned_text: str # Rempli après le passage au LLM (nœud 1)
    solution: str     # Rempli à la fin (nœud 2)

# --- INITIALISATION LLM (GROQ) ---
# llama-3.3-70b est idéal pour la correction d'OCR complexe
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- FONCTION AUXILIAIRE : APPEL AU SERVEUR MCP ---
def call_ocr_mcp_server(path: str) -> str:
    """Communique avec le serveur MCP tournant sur le port 8002"""
    try:
        with httpx.Client() as client:
            response = client.post(
                "http://127.0.0.1:8002/tools/vision_ocr_tool", 
                json={"arguments": {"image_path": path}},
                timeout=30.0
            )
            # Récupération sécurisée du contenu renvoyé par le serveur MCP
            data = response.json()
            return data.get("content", "Erreur : Contenu MCP vide.")
    except Exception as e:
        print(f"⚠️ Erreur de connexion MCP: {e}")
        return f"Erreur de communication avec le serveur OCR : {str(e)}"

# --- NŒUD 1 : CLEANER (OCR + REFORMULATION) ---
def clean_text_node(state: AgentState):
    print("--- [AGENT] Début du nœud CLEANER ---")
    
    # SÉCURITÉ : On récupère image_path avec .get() pour éviter le crash 'KeyError'
    img_path = state.get("image_path")
    
    if not img_path:
        print("❌ Erreur : 'image_path' est manquant dans l'état.")
        return {"raw_text": "Erreur : Pas de chemin d'image.", "cleaned_text": "Erreur"}

    # 1. Appel du serveur MCP pour obtenir le texte brut
    print(f"--- [AGENT] Appel MCP pour : {img_path} ---")
    extracted_text = call_ocr_mcp_server(img_path)
    
    # 2. Nettoyage du texte par le LLM
    prompt = (
        "Tu es un expert en correction d'OCR. Voici un texte brut extrait d'un examen. "
        "1. Corrige les erreurs de lecture et de ponctuation. "
        "2. Reformule les phrases si nécessaire pour qu'elles soient lisibles. "
        "3. Liste clairement les questions posées sans y répondre.\n\n"
        f"TEXTE BRUT : {extracted_text}"
    )
    
    response = llm.invoke(prompt)
    
    # Mise à jour de l'état
    return {
        "cleaned_text": response.content, 
        "raw_text": extracted_text
    }

# --- NŒUD 2 : SOLVER (RÉSOLUTION PÉDAGOGIQUE) ---
def solve_exam_node(state: AgentState):
    print("--- [AGENT] Début du nœud SOLVER ---")
    
    # On récupère le texte déjà nettoyé au nœud précédent
    cleaned = state.get("cleaned_text", "Pas de texte à résoudre.")
    
    prompt = (
        "Tu es un professeur assistant. Résous les questions d'examen suivantes de manière "
        "claire, étape par étape, en utilisant un ton pédagogique et un format Markdown élégant.\n\n"
        f"QUESTIONS : {cleaned}"
    )
    
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- CONSTRUCTION DU GRAPH ---
workflow = StateGraph(AgentState)

# Ajout des nœuds
workflow.add_node("cleaner", clean_text_node)
workflow.add_node("solver", solve_exam_node)

# Définition des flux
workflow.set_entry_point("cleaner")
workflow.add_edge("cleaner", "solver")
workflow.add_edge("solver", END)

# Compilation finale
exam_agent = workflow.compile()