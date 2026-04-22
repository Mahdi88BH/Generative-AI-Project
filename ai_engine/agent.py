import os
from typing import TypedDict
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
    solution: str           

# --- 2. INITIALISATION GROQ ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1, 
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. NŒUD 1 : L'ANALYSTE ---
def analyze_and_clean_node(state: AgentState):
    print("--- [NEXUS CORE] Phase 1 : Analyse Cognitive ---")
    
    # On récupère le texte brut ou on utilise le contexte si l'OCR a échoué
    raw = state.get('raw_text', '')
    context = state.get('user_context', 'N/A')

    prompt = fr"""Tu es une IA experte en reconstruction de documents académiques.
CONTEXTE UTILISATEUR : {context}

MISSION :
1. Analyse le texte fourni et identifie le domaine précis.
2. Reconstruis l'énoncé de manière fidèle et lisible avec des emojis (📝, 🔢).
3. Si le texte semble être du code ou des maths, préserve la syntaxe.

FORMAT DE RÉPONSE :
[DOMAINE] : (Matière)
[ÉNONCÉ] :
(Texte corrigé)

CONTENU À TRAITER :
{raw}
"""
    response = llm.invoke(prompt)
    content = response.content
    
    domain = "Général"
    cleaned = content
    if "[DOMAINE]" in content and "[ÉNONCÉ]" in content:
        parts = content.split("[ÉNONCÉ]")
        domain = parts[0].replace("[DOMAINE]", "").replace(":", "").strip()
        cleaned = parts[1].strip()

    # Crucial : On renvoie subject et cleaned pour alimenter le solver
    return {"subject_inferred": domain, "cleaned_text": cleaned}

# --- 4. NŒUD 2 : LE MAÎTRE ---
def solve_exam_node(state: AgentState):
    subject = state.get('subject_inferred', 'Général')
    print(f"--- [NEXUS CORE] Phase 2 : Résolution ({subject}) ---")
    
    prompt = fr"""Tu es un professeur expert en {subject}.
Résous cet examen de manière magistrale.

CONSIGNES :
- Pédagogie avec emojis (✅, ⚙️, 📚, 🚀).
- MATHS : Utilise \( ... \) et \[ ... \].
- STRUCTURE : Markdown clair avec titres.

ÉNONCÉ :
{state.get('cleaned_text', 'Énoncé non disponible.')}
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 5. NŒUD 3 : LE CHAT (FEEDBACK INTERACTIF) ---
def chat_feedback_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 3 : Interaction Chat ---")
    
    # On récupère tout le contexte précédent pour une modification intelligente
    prompt = fr"""Tu es le professeur expert. L'utilisateur souhaite modifier ta correction précédente.

DEMANDE : {state.get('user_context', 'Révision générale')}

CORRECTION PRÉCÉDENTE : 
{state.get('solution', 'N/A')}

MISSION :
- Applique les changements demandés tout en gardant le formatage LaTeX et Markdown.
- Renvoie la VERSION COMPLÈTE mise à jour.
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 6. LOGIQUE DE ROUTAGE ---
def route_request(state: AgentState):
    # Logique : Si solution existe -> Discussion. Sinon -> Analyse.
    if state.get("solution") and len(state["solution"]) > 20:
        return "chat_feedback"
    return "analyzer"

# --- 7. CONSTRUCTION DU GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("analyzer", analyze_and_clean_node)
workflow.add_node("solver", solve_exam_node)
workflow.add_node("chat_feedback", chat_feedback_node)

workflow.set_conditional_entry_point(
    route_request,
    {
        "analyzer": "analyzer",
        "chat_feedback": "chat_feedback"
    }
)

workflow.add_edge("analyzer", "solver")
workflow.add_edge("solver", END)
workflow.add_edge("chat_feedback", END)

exam_agent = workflow.compile()