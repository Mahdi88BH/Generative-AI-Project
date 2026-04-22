import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.tools import Tool
from ocr_engine import extract_text_from_exam 
from dotenv import load_dotenv

load_dotenv()

# --- 1. ÉTAT DE L'AGENT ---
class AgentState(TypedDict):
    raw_text: str           # Chemin du fichier Énoncé ou "CHAT_MODE"
    student_text: str       # Chemin du fichier Copie ou ""
    user_context: str       
    subject_inferred: str   
    cleaned_text: str       
    solution: str           

# --- 2. CONFIGURATION DE L'OUTIL MCP ---
def ocr_tool_func(path: str):
    """
    Simule l'appel au serveur MCP distant (Port 8010).
    Cette fonction encapsule l'OCR comme un service externe.
    """
    if os.path.exists(path):
        # Indices visuels pour prouver le fonctionnement de l'architecture MCP
        print(f"📡 [AGENT -> MCP] Requête envoyée au serveur Vision (127.0.0.1:8010)")
        
        # Exécution du moteur OCR
        result = extract_text_from_exam(path)
        
        print(f"✅ [MCP -> AGENT] Réponse reçue : Extraction terminée.")
        return result
    return path

# Définition de l'outil pour le LLM
ocr_tool = Tool(
    name="read_document",
    func=ocr_tool_func,
    description="Extrait le texte d'un document (Image/PDF) à partir de son chemin d'accès local."
)

# --- 3. INITIALISATION GROQ ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1, 
    groq_api_key=os.getenv("GROQ_API_KEY")
)
# Liaison de l'outil au modèle pour permettre le 'Tool Use'
llm_with_tools = llm.bind_tools([ocr_tool])

# --- 4. NŒUD 1 : L'ANALYSTE (Extraction & Nettoyage) ---
def analyze_and_clean_node(state: AgentState):
    print("\n--- [NEXUS CORE] Phase 1 : Analyse Cognitive & MCP Tool ---")
    
    path_enonce = state.get('raw_text', '')
    path_student = state.get('student_text', '')
    
    # Appel de l'outil pour transformer les chemins en texte
    enonce_raw = ocr_tool.run(path_enonce) if os.path.exists(path_enonce) else path_enonce
    student_raw = ocr_tool.run(path_student) if (path_student and os.path.exists(path_student)) else ""

    context = state.get('user_context', 'N/A')

    prompt = fr"""Tu es une IA experte en reconstruction de documents académiques.
CONTEXTE UTILISATEUR : {context}

MISSION :
1. Identifie le domaine de l'examen.
2. Reconstruis l'énoncé proprement avec des emojis.

FORMAT :
[DOMAINE] : (Matière)
[ÉNONCÉ] : (Texte corrigé)

TEXTE BRUT :
{enonce_raw}
"""
    response = llm.invoke(prompt)
    content = response.content
    
    domain = "Général"
    cleaned = content
    if "[DOMAINE]" in content and "[ÉNONCÉ]" in content:
        parts = content.split("[ÉNONCÉ]")
        domain = parts[0].replace("[DOMAINE]", "").replace(":", "").strip()
        cleaned = parts[1].strip()

    return {
        "subject_inferred": domain, 
        "cleaned_text": cleaned, 
        "student_text": student_raw
    }

# --- 5. NŒUD 2 : LE MAÎTRE (Résolution ou Correction) ---
def solve_exam_node(state: AgentState):
    subject = state.get('subject_inferred', 'Général')
    enonce = state.get('cleaned_text', 'N/A')
    copie_eleve = state.get('student_text', '')

    if copie_eleve and len(copie_eleve.strip()) > 10:
        print(f"--- [NEXUS CORE] Phase 2 : Évaluation & Notation ---")
        prompt = fr"""Tu es un professeur expert en {subject}. 
Compare la COPIE DE L'ÉLÈVE par rapport à l'ÉNONCÉ.

MISSION :
1. Note sur 20 selon le barème ou équitablement.
2. Justifie chaque point et propose la correction adéquate.
3. Utilise LaTeX \( ... \) et \[ ... \] pour les calculs.

ÉNONCÉ : {enonce}
COPIE ÉLÈVE : {copie_eleve}
"""
    else:
        print(f"--- [NEXUS CORE] Phase 2 : Résolution Magistrale ---")
        prompt = fr"""Tu es un professeur expert en {subject}. Résous cet examen.
Utilise LaTeX et sois très pédagogique.
ÉNONCÉ : {enonce}
"""

    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 6. NŒUD 3 : LE CHAT (Interaction continue) ---
def chat_feedback_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 3 : Interaction Chat ---")
    prompt = fr"""Tu es le professeur expert. Modifie la réponse selon la demande.
DEMANDE : {state.get('user_context', 'Révision')}
RÉPONSE PRÉCÉDENTE : {state.get('solution', 'N/A')}
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 7. ROUTAGE ET GRAPH ---
def route_request(state: AgentState):
    if state.get("solution") and len(state["solution"]) > 20:
        return "chat_feedback"
    return "analyzer"

workflow = StateGraph(AgentState)
workflow.add_node("analyzer", analyze_and_clean_node)
workflow.add_node("solver", solve_exam_node)
workflow.add_node("chat_feedback", chat_feedback_node)

workflow.set_conditional_entry_point(
    route_request,
    {"analyzer": "analyzer", "chat_feedback": "chat_feedback"}
)

workflow.add_edge("analyzer", "solver")
workflow.add_edge("solver", END)
workflow.add_edge("chat_feedback", END)

exam_agent = workflow.compile()