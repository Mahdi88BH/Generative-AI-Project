import os
import httpx
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

load_dotenv()

# --- 1. ÉTAT DE L'AGENT ---
class AgentState(TypedDict):
    mode: str
    image_path: Optional[str]
    enonce_path: Optional[str]
    copie_paths: Optional[List[str]]
    raw_text: str
    enonce_text: str
    copie_text: str
    solution: str
    rapport_correction: str

# --- 2. INITIALISATION DU CERVEAU (LLAMA 3.3 70B) ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.1, # Basse température pour plus de rigueur mathématique
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. UTILITAIRE VISION (MCP CLIENT) ---
def call_ocr(path: str) -> str:
    """Communique avec le serveur MCP Vision sur le port 8002."""
    if not path or not os.path.exists(path):
        return ""
    try:
        with httpx.Client() as client:
            response = client.post(
                "http://127.0.0.1:8002/tools/vision_ocr_tool", 
                json={"arguments": {"image_path": os.path.abspath(path)}},
                timeout=60.0
            )
            content = response.json().get("content", "")
            return content if content else "[OCR: Aucun texte détecté]"
    except Exception as e:
        print(f"⚠️ Erreur MCP sur {path}: {e}")
        return f"[Erreur OCR: {str(e)}]"

# --- 4. NŒUDS DU GRAPH ---

def extraction_node(state: AgentState):
    """Extrait le texte de tous les documents selon le mode choisi."""
    print(f"--- [AGENT] Extraction OCR (Mode: {state['mode']}) ---")
    
    if state["mode"] == "solve":
        text = call_ocr(state["image_path"])
        return {"raw_text": text}
    else:
        # Mode Grade : On lit l'épreuve et toutes les pages de la copie
        e_text = call_ocr(state["enonce_path"])
        
        full_copie_text = ""
        for i, path in enumerate(state["copie_paths"] or []):
            page_text = call_ocr(path)
            full_copie_text += f"\n--- PAGE {i+1} ---\n{page_text}"
            
        return {
            "enonce_text": e_text,
            "copie_text": full_copie_text
        }

def solver_node(state: AgentState):
    """Nœud Étudiant : Résolution pure de l'épreuve."""
    print("--- [AGENT] Génération de la solution académique ---")
    
    if not state.get("raw_text") or "[Erreur OCR]" in state["raw_text"]:
        return {"solution": "❌ Impossible de lire l'énoncé. Vérifiez la qualité de l'image."}

    prompt = (
        "Tu es un expert académique de haut niveau. Résous l'énoncé suivant étape par étape.\n"
        "Règles :\n"
        "1. Utilise Markdown pour la structure.\n"
        "2. Utilise LaTeX pour TOUTES les formules mathématiques (ex: $x^2$).\n"
        "3. Sois pédagogique et clair.\n\n"
        f"ÉNONCÉ EXTRAIT :\n{state['raw_text']}"
    )
    res = llm.invoke(prompt)
    return {"solution": res.content}

def grader_node(state: AgentState):
    """Nœud Professeur : Correction comparative sans corrigé type."""
    print("--- [AGENT] Évaluation Experte Multi-Pages ---")
    
    if not state.get("enonce_text") or not state.get("copie_text"):
        return {"rapport_correction": "❌ Données insuffisantes pour la correction."}

    prompt = (
        "Tu es un Professeur Universitaire expert. Ta mission est de corriger la copie d'un étudiant "
        "en te basant uniquement sur l'ÉPREUVE fournie. Tu dois toi-même résoudre les exercices "
        "pour évaluer l'étudiant.\n\n"
        "--- DOCUMENTS ---\n"
        f"1. ÉPREUVE (ÉNONCÉ) : {state['enonce_text']}\n"
        f"2. COPIE DE L'ÉTUDIANT : {state['copie_text']}\n\n"
        "MISSION :\n"
        "A. Pour chaque question, donne la RÉPONSE ACADÉMIQUE ATTENDUE.\n"
        "B. Analyse la RÉPONSE DE L'ÉTUDIANT.\n"
        "C. Si faux, explique précisément : 'POURQUOI VOTRE RÉPONSE N'EST PAS CORRECTE'.\n"
        "D. Attribue une note partielle.\n\n"
        "--- STRUCTURE DU RAPPORT ---\n"
        "# 🎓 RAPPORT DE CORRECTION EXPERT\n"
        "## 📊 Note Globale : [Note]/20\n\n"
        "### 🔍 Analyse Détaillée par Question\n"
        "### 💡 Conseils de Progression"
    )
    res = llm.invoke(prompt)
    return {"rapport_correction": res.content}

# --- 5. LOGIQUE DE ROUTAGE ---
def router(state: AgentState):
    return "solver" if state["mode"] == "solve" else "grader"

# --- 6. CONSTRUCTION DU GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("extraction", extraction_node)
workflow.add_node("solver", solver_node)
workflow.add_node("grader", grader_node)

workflow.set_entry_point("extraction")

workflow.add_conditional_edges(
    "extraction",
    router,
    {"solver": "solver", "grader": "grader"}
)

workflow.add_edge("solver", END)
workflow.add_edge("grader", END)

exam_agent = workflow.compile()