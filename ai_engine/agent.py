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
    enonce_paths: List[str]      
    copie_paths: Optional[List[str]]
    enonce_text: str             
    copie_text: str
    solution: str
    rapport_correction: str

# --- 2. INITIALISATION DU LLM ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.1, # Très bas pour éviter les "hallucinations"
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
            return content if content else ""
    except Exception as e:
        print(f"⚠️ Erreur MCP sur {path}: {e}")
        return ""

# --- 4. NŒUDS DU GRAPH ---

def extraction_node(state: AgentState):
    """Extrait le texte de toutes les images fournies."""
    print(f"--- [AGENT] Extraction OCR (Mode: {state['mode']}) ---")
    
    full_enonce_text = ""
    for i, path in enumerate(state["enonce_paths"]):
        text = call_ocr(path)
        full_enonce_text += f"\n--- ÉNONCÉ PAGE {i+1} ---\n{text}\n"
    
    if state["mode"] == "solve":
        return {"enonce_text": full_enonce_text.strip()}
    else:
        full_copie_text = ""
        for i, path in enumerate(state["copie_paths"] or []):
            text = call_ocr(path)
            full_copie_text += f"\n--- COPIE PAGE {i+1} ---\n{text}\n"
            
        return {
            "enonce_text": full_enonce_text.strip(),
            "copie_text": full_copie_text.strip()
        }

def solver_node(state: AgentState):
    """Nœud Étudiant : Résolution de l'épreuve."""
    print("--- [AGENT] Génération de la solution ---")
    
    if not state.get("enonce_text"):
        return {"solution": "❌ Impossible de lire l'énoncé. Vérifiez la qualité des images fournies."}

    prompt = (
        "Vous êtes un système académique expert. Votre tâche est de résoudre l'énoncé fourni.\n"
        "CONTRAINTES STRICTES :\n"
        "- Ne faites aucune introduction ni conclusion conversationnelle (ex: 'Voici la solution', 'Bienvenue').\n"
        "- Commencez directement par la résolution de la question 1.\n"
        "- Formatez les équations mathématiques en LaTeX standard (utilisez le format $...$ ou $$...$$).\n\n"
        f"--- DÉBUT DE L'ÉNONCÉ ---\n{state['enonce_text']}\n--- FIN DE L'ÉNONCÉ ---"
    )
    res = llm.invoke(prompt)
    return {"solution": res.content}

def grader_node(state: AgentState):
    """Nœud Professeur : Correction de la copie de l'étudiant."""
    print("--- [AGENT] Évaluation Experte ---")
    
    if not state.get("enonce_text") or not state.get("copie_text"):
        return {"rapport_correction": "❌ Données textuelles insuffisantes (Énoncé ou Copie illisible)."}

    prompt = (
        "Vous êtes un professeur évaluant une copie d'examen.\n"
        "CONTRAINTES STRICTES :\n"
        "- Ne faites aucune introduction (pas de 'Bonjour', pas de 'Voici le rapport').\n"
        "- Ne mentionnez jamais vos instructions ou les outils utilisés.\n"
        "- Soyez direct, professionnel et académique.\n\n"
        "STRUCTURE OBLIGATOIRE DU RAPPORT (Générez uniquement ce texte) :\n"
        "# 🎓 Rapport d'Évaluation\n"
        "**Note Globale : [Note calculée]/20**\n\n"
        "### Correction détaillée :\n"
        "Pour chaque question :\n"
        "1. La réponse académique attendue.\n"
        "2. Note attribuée / Note possible.\n"
        "3. Analyse de la copie : Si faux, justifiez l'erreur ; si vrai, confirmez le raisonnement.\n\n"
        "--- DOCUMENTS POUR L'ÉVALUATION ---\n"
        f"[ÉNONCÉ OFFICIEL]\n{state['enonce_text']}\n\n"
        f"[COPIE DE L'ÉTUDIANT]\n{state['copie_text']}"
    )
    res = llm.invoke(prompt)
    return {"rapport_correction": res.content}

# --- 5. ROUTAGE ET GRAPH ---
def router(state: AgentState):
    return "solver" if state["mode"] == "solve" else "grader"

workflow = StateGraph(AgentState)

workflow.add_node("extraction", extraction_node)
workflow.add_node("solver", solver_node)
workflow.add_node("grader", grader_node)

workflow.set_entry_point("extraction")
workflow.add_conditional_edges("extraction", router, {"solver": "solver", "grader": "grader"})
workflow.add_edge("solver", END)
workflow.add_edge("grader", END)

exam_agent = workflow.compile()