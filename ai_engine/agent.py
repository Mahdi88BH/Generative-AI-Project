import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# --- 1. ÉTAT DE L'AGENT ---
class AgentState(TypedDict):
    raw_text: str           # Texte issu de l'OCR (Image ou PDF)
    user_context: str       # Message actuel de l'utilisateur (Context ou Chat)
    subject_inferred: str   # Domaine détecté (Maths, BI, etc.)
    cleaned_text: str       # Énoncé reconstruit proprement
    solution: str           # La dernière version de la correction générée

# --- 2. INITIALISATION DU MOTEUR GROQ ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1, # Précision maximale
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. NŒUD 1 : L'ANALYSTE (DÉTECTION & NETTOYAGE) ---
def analyze_and_clean_node(state: AgentState):
    print("--- [NEXUS CORE] Phase 1 : Analyse Cognitive & Nettoyage ---")
    
    prompt = f"""Tu es une IA experte en reconstruction de documents académiques.
CONTEXTE UTILISATEUR : {state.get('user_context', 'N/A')}

MISSION :
1. Analyse le texte OCR brut et identifie le domaine précis (ex: Informatique Décisionnelle, Algèbre, etc.).
2. Utilise le contexte utilisateur pour corriger les erreurs de lecture de l'OCR.
3. Reconstruis l'énoncé complet avec des emojis discrets pour la structure (📝, 🔢).

FORMAT DE RÉPONSE (OBLIGATOIRE) :
[DOMAINE] : (Matière)
[ÉNONCÉ] :
(Texte corrigé)

TEXTE OCR BRUT :
{state['raw_text']}
"""
    response = llm.invoke(prompt)
    content = response.content
    
    domain = "Général"
    cleaned = content
    if "[DOMAINE]" in content and "[ÉNONCÉ]" in content:
        parts = content.split("[ÉNONCÉ]")
        domain = parts[0].replace("[DOMAINE]", "").replace(":", "").strip()
        cleaned = parts[1].strip()

    return {"subject_inferred": domain, "cleaned_text": cleaned}

# --- 4. NŒUD 2 : LE MAÎTRE (RÉSOLUTION INITIALE) ---
def solve_exam_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 2 : Résolution Experte ({state['subject_inferred']}) ---")
    
    prompt = f"""Tu es un professeur expert en {state['subject_inferred']}.
Résous cet examen de manière magistrale.

CONSIGNES :
- Utilise des emojis pour la pédagogie (✅, ⚙️, 📚, 🚀).
- Utilise impérativement Markdown (titres #, gras **).
- MATHS : Utilise \( ... \) pour les formules en ligne et \[ ... \] pour les blocs.
- Ne fais aucune introduction du type "Voici la solution".

ÉNONCÉ :
{state['cleaned_text']}
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 5. NŒUD 3 : LE CHAT (INTERACTION & FEEDBACK) ---
def chat_feedback_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 3 : Interaction Chat / Correction ---")
    
    prompt = f"""Tu es le professeur expert. L'utilisateur souhaite modifier ou préciser la correction actuelle.

ÉNONCÉ DE RÉFÉRENCE : 
{state['cleaned_text']}

CORRECTION ACTUELLE : 
{state['solution']}

DEMANDE DE L'UTILISATEUR : 
{state['user_context']}

MISSION :
- Modifie la correction selon les instructions précises de l'utilisateur.
- Garde les Emojis, le Markdown et le formatage LaTeX (\(...\) et \[...\]).
- Renvoie la NOUVELLE VERSION COMPLÈTE du corrigé.
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 6. LOGIQUE DE ROUTAGE (DÉCISION) ---
def route_request(state: AgentState):
    # Si une solution existe déjà, on passe en mode discussion/correction
    if state.get("solution") and len(state["solution"]) > 20:
        return "chat_feedback"
    return "analyzer"

# --- 7. CONSTRUCTION DU GRAPH (LANGGRAPH) ---
workflow = StateGraph(AgentState)

workflow.add_node("analyzer", analyze_and_clean_node)
workflow.add_node("solver", solve_exam_node)
workflow.add_node("chat_feedback", chat_feedback_node)

# Point d'entrée intelligent
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