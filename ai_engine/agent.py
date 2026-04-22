import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# --- 1. ÉTAT DE L'AGENT MIS À JOUR ---
class AgentState(TypedDict):
    raw_text: str           # Texte de l'énoncé (OCR/Direct)
    student_text: str       # Texte de la copie élève (Optionnel)
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
    raw = state.get('raw_text', '')
    context = state.get('user_context', 'N/A')

    prompt = fr"""Tu es une IA experte en reconstruction de documents académiques.
CONTEXTE UTILISATEUR : {context}

MISSION :
1. Identifie le domaine précis de l'examen.
2. Reconstruis l'énoncé de manière fidèle et lisible avec des emojis (📝, 🔢).
3. Si des barèmes ([2 pts], etc.) sont visibles, assure-toi de les inclure clairement.

FORMAT DE RÉPONSE :
[DOMAINE] : (Matière)
[ÉNONCÉ] :
(Texte corrigé)

CONTENU :
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

    return {"subject_inferred": domain, "cleaned_text": cleaned}

# --- 4. NŒUD 2 : LE MAÎTRE (LOGIQUE DOUBLE : RÉSOLUTION OU NOTATION) ---
def solve_exam_node(state: AgentState):
    subject = state.get('subject_inferred', 'Général')
    enonce = state.get('cleaned_text', 'N/A')
    copie_eleve = state.get('student_text', '')

    # --- CAS A : MODE PROFESSEUR / CORRECTEUR (Si une copie est fournie) ---
    if copie_eleve and len(copie_eleve.strip()) > 10:
        print(f"--- [NEXUS CORE] Phase 2 : Évaluation & Notation ---")
        prompt = fr"""Tu es un professeur expert en {subject}. 
Compare la COPIE DE L'ÉLÈVE par rapport à l'ÉNONCÉ.

MISSION :
1. Analyse chaque réponse de l'élève par rapport à l'énoncé.
2. Attribue une note pour chaque question en suivant le barème de l'énoncé (sinon répartis 20 points équitablement).
3. Justifie chaque point retiré et propose la correction adéquate.
4. Calcule la NOTE FINALE sur 20.

CONSIGNES :
- Utilise LaTeX \( ... \) et \[ ... \] pour les calculs.
- Utilise Markdown et Emojis (🎓, 🎯, ❌, ✅).

ÉNONCÉ :
{enonce}

COPIE DE L'ÉLÈVE :
{copie_eleve}
"""
    
    # --- CAS B : MODE RÉSOLUTION CLASSIQUE (Seul l'énoncé est fourni) ---
    else:
        print(f"--- [NEXUS CORE] Phase 2 : Résolution Magistrale ---")
        prompt = fr"""Tu es un professeur expert en {subject}.
Résous cet examen de manière complète et pédagogique.

CONSIGNES :
- Pédagogie avec emojis (✅, ⚙️, 📚, 🚀).
- MATHS : Utilise \( ... \) et \[ ... \].
- STRUCTURE : Markdown clair avec titres.

ÉNONCÉ :
{enonce}
"""

    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 5. NŒUD 3 : LE CHAT ---
def chat_feedback_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 3 : Interaction Chat ---")
    prompt = fr"""Tu es le professeur expert. L'utilisateur souhaite modifier ta dernière réponse (Correction ou Note).

DEMANDE : {state.get('user_context', 'Révision')}
RÉPONSE PRÉCÉDENTE : {state.get('solution', 'N/A')}

MISSION :
- Mets à jour la réponse en fonction de la demande.
- Préserve le formatage LaTeX et le style pédagogique.
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 6. LOGIQUE DE ROUTAGE ---
def route_request(state: AgentState):
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