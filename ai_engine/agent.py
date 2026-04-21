import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# --- 1. ÉTAT DE L'AGENT ---
class AgentState(TypedDict):
    raw_text: str
    user_context: str
    subject_inferred: str 
    cleaned_text: str
    solution: str # Contient la version actuelle de la correction

# --- 2. INITIALISATION GROQ ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. NŒUD 1 : L'ANALYSTE (FUSION OCR + CONTEXTE) ---
def analyze_and_clean_node(state: AgentState):
    print("--- [NEXUS CORE] Phase 1 : Analyse & Reconstruction ---")
    prompt = f"""Tu es une IA experte en documents académiques.
CONTEXTE UTILISATEUR : {state.get('user_context', 'N/A')}

MISSION :
1. Identifie la matière et corrige l'OCR ci-dessous.
2. Utilise des emojis pour structurer (📝, 🔢).
3. Ne réponds que sous le format imposé.

FORMAT :
[DOMAINE] : (Matière)
[ÉNONCÉ] : (Texte corrigé)

OCR : {state['raw_text']}"""
    
    response = llm.invoke(prompt)
    content = response.content
    domain, cleaned = "Inconnu", content
    if "[DOMAINE]" in content and "[ÉNONCÉ]" in content:
        parts = content.split("[ÉNONCÉ]")
        domain = parts[0].replace("[DOMAINE]", "").replace(":", "").strip()
        cleaned = parts[1].strip()
    return {"subject_inferred": domain, "cleaned_text": cleaned}

# --- 4. NŒUD 2 : LE MAÎTRE (RÉSOLUTION INITIALE) ---
def solve_exam_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 2 : Première Résolution ({state['subject_inferred']}) ---")
    prompt = f"""Tu es un professeur expert en {state['subject_inferred']}.
Résous cet énoncé avec pédagogie, Markdown, Emojis et LaTeX (\(...\) ou \[...\]).
Pas d'intro ni de conclusion.

ÉNONCÉ : {state['cleaned_text']}"""
    
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 5. NŒUD 3 : LE CHAT (AMÉLIORATION CONTINUE) ---
def chat_feedback_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 3 : Interaction & Correction ---")
    prompt = f"""Tu es le professeur expert. L'utilisateur souhaite modifier ou préciser la correction actuelle.

ÉNONCÉ DE RÉFÉRENCE : 
{state['cleaned_text']}

CORRECTION ACTUELLE À MODIFIER : 
{state['solution']}

DEMANDE DE L'UTILISATEUR : 
{state['user_context']}

MISSION :
- Applique strictement les corrections demandées (ex: refaire l'exercice 1, simplifier, etc.).
- Garde le formatage LaTeX (\(...\) et \[...\]), le Markdown et les Emojis.
- Renvoie la NOUVELLE VERSION COMPLÈTE de la correction.
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 6. LOGIQUE DE ROUTAGE ---
def router(state: AgentState):
    # Si 'solution' contient déjà du texte, on passe en mode discussion
    if state.get("solution") and len(state["solution"]) > 10:
        return "chat_feedback"
    return "analyzer"

# --- 7. CONSTRUCTION DU GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("analyzer", analyze_and_clean_node)
workflow.add_node("solver", solve_exam_node)
workflow.add_node("chat_feedback", chat_feedback_node)

# Entrée conditionnelle : Nouveau scan ou Suite de discussion ?
workflow.set_conditional_entry_point(
    router,
    {
        "analyzer": "analyzer",
        "chat_feedback": "chat_feedback"
    }
)

workflow.add_edge("analyzer", "solver")
workflow.add_edge("solver", END)
workflow.add_edge("chat_feedback", END)

exam_agent = workflow.compile()