import os
import httpx
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

load_dotenv()

# --- 1. CONFIGURATION DE L'ÉTAT (AGENT STATE) ---
class AgentState(TypedDict):
    mode: str               # "solve" ou "grade"
    # Chemins des fichiers
    image_path: Optional[str]      # Utilisé en mode solve
    enonce_path: Optional[str]     # Utilisé en mode grade
    corrige_path: Optional[str]    # Utilisé en mode grade
    copie_paths: Optional[List[str]] # Liste de chemins (PDF ou images)
    # Textes extraits
    raw_text: str           # Texte énoncé (mode solve)
    enonce_text: str        # Texte énoncé (mode grade)
    corrige_text: str       # Texte corrigé type
    copie_text: str         # Texte complet de la copie étudiant
    # Résultats finaux
    solution: str           # Résultat mode solve
    rapport_correction: str # Résultat mode grade

# --- 2. INITIALISATION LLM ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. UTILITAIRE OCR via MCP ---
def call_ocr(path: str) -> str:
    if not path or not os.path.exists(path):
        return ""
    try:
        with httpx.Client() as client:
            response = client.post(
                "http://127.0.0.1:8002/tools/vision_ocr_tool", 
                json={"arguments": {"image_path": path}},
                timeout=60.0
            )
            return response.json().get("content", "")
    except Exception as e:
        return f"[Erreur OCR]: {str(e)}"

# --- 4. NŒUDS DU GRAPH ---

def extraction_node(state: AgentState):
    """Nœud de vision : Extrait le texte de tous les documents fournis."""
    print(f"--- [AGENT] Extraction OCR (Mode: {state['mode']}) ---")
    
    if state["mode"] == "solve":
        text = call_ocr(state["image_path"])
        return {"raw_text": text}
    else:
        # Mode Grade : On extrait l'énoncé, le corrigé et TOUTES les pages de la copie
        e_text = call_ocr(state["enonce_path"])
        c_text = call_ocr(state["corrige_path"])
        
        full_copie_text = ""
        for i, path in enumerate(state["copie_paths"]):
            page_text = call_ocr(path)
            full_copie_text += f"\n--- PAGE {i+1} ---\n{page_text}"
            
        return {
            "enonce_text": e_text,
            "corrige_text": c_text,
            "copie_text": full_copie_text
        }

def solver_node(state: AgentState):
    """Nœud Étudiant : Résout l'énoncé."""
    print("--- [AGENT] Génération de la solution type ---")
    prompt = (
        "Tu es un expert académique. Résous cet énoncé d'examen de manière pédagogique. "
        "Utilise le format Markdown et LaTeX pour les formules mathématiques.\n\n"
        f"ÉNONCÉ EXTRAIT :\n{state['raw_text']}"
    )
    res = llm.invoke(prompt)
    return {"solution": res.content}

def grader_node(state: AgentState):
    print("--- [AGENT] Évaluation Académique Multidisciplinaire ---")
    prompt = (
        "Tu es un Professeur Universitaire expert dans la discipline concernée par l'épreuve "
        "(Droit, Mathématiques, Philosophie, Sciences, etc.).\n\n"
        f"--- ÉPREUVE (ÉNONCÉ) ---\n{state['enonce_text']}\n\n"
        f"--- COPIE DE L'ÉTUDIANT ---\n{state['copie_text']}\n\n"
        "MISSION :\n"
        "1. Analyse l'épreuve et identifie les attentes académiques.\n"
        "2. Évalue la copie de l'étudiant avec rigueur et objectivité.\n"
        "3. Produis un rapport structuré en Markdown :\n"
        "   - Analyse de la pertinence des réponses.\n"
        "   - Identification des erreurs ou lacunes.\n"
        "   - Note détaillée par question et Note Globale sur 20.\n"
        "   - Conseil pédagogique pour l'étudiant."
    )
    res = llm.invoke(prompt)
    return {"rapport_correction": res.content}

# --- 5. LOGIQUE DE ROUTAGE ---

def router(state: AgentState):
    """Décide quel chemin prendre dans le graph."""
    return "solver" if state["mode"] == "solve" else "grader"

# --- 6. CONSTRUCTION DU GRAPH ---

workflow = StateGraph(AgentState)

# Ajout des nœuds
workflow.add_node("extraction", extraction_node)
workflow.add_node("solver", solver_node)
workflow.add_node("grader", grader_node)

# Définition des connexions
workflow.set_entry_point("extraction")

# Branchement conditionnel après l'extraction
workflow.add_conditional_edges(
    "extraction",
    router,
    {
        "solver": "solver",
        "grader": "grader"
    }
)

workflow.add_edge("solver", END)
workflow.add_edge("grader", END)

# Compilation
exam_agent = workflow.compile()