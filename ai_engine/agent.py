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
    raw_text: str           
    student_text: str       
    user_context: str       
    subject_inferred: str   
    cleaned_text: str       
    solution: str           

# --- 2. CONFIGURATION DE L'OUTIL ---
def ocr_tool_func(path: str):
    if path and os.path.exists(path):
        print(f"📡 [AGENT TOOL] Analyse Vision via tool 'read_document' : {os.path.basename(path)}")
        return extract_text_from_exam(path)
    return path

ocr_tool = Tool(
    name="read_document",
    func=ocr_tool_func,
    description="Extrait le texte d'un document académique (PDF ou Image) à partir d'un chemin local."
)

# --- 3. INITIALISATION GROQ (Température basse pour la précision technique) ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1, 
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 4. NŒUD 1 : L'ANALYSTE (Reconstruction de Données) ---
def analyze_and_clean_node(state: AgentState):
    print("\n--- [NEXUS CORE] Phase 1 : Reconstruction Cognitive Haute Précision ---")
    
    path_enonce = state.get('raw_text', '')
    path_student = state.get('student_text', '')
    
    enonce_raw = ocr_tool.run(path_enonce)
    student_raw = ocr_tool.run(path_student) if path_student else ""

    context = state.get('user_context', 'N/A')

    # PROMPT ULTRA-PUISSANT : RECONSTRUCTION
    prompt = fr"""
AGIS EN TANT QU'EXPERT EN NUMÉRISATION ACADÉMIQUE ET RECONSTRUCTION DE DONNÉES.
CONTEXTE : {context}

MISSION : Transformer le flux OCR brut en un énoncé d'examen parfaitement structuré.

DIRECTIVES DE QUALITÉ :
1. CORRECTION TECHNIQUE : Rectifie les erreurs d'OCR sur les symboles scientifiques (ex: 'm/s2' -> 'm/s²').
2. STRUCTURE : Hiérarchise avec Markdown (#, ##). Inclus les barèmes **[pts]** s'ils existent.
3. MATHS : Formate TOUT en LaTeX strict : \( ... \) pour le texte et \[ ... \] pour les blocs isolés.

FORMAT DE SORTIE IMPÉRATIF :
[DOMAINE] : (Matière précise)
[ÉNONCÉ] :
# 📝 (Titre reconstruit)
(Description fluide du sujet)
---
(Questions numérotées)

CONTENU OCR :
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

# --- 5. NŒUD 2 : LE MAÎTRE (Résolution Magistrale ou Correction Chirurgicale) ---
def solve_exam_node(state: AgentState):
    subject = state.get('subject_inferred', 'Général')
    enonce = state.get('cleaned_text', 'N/A')
    copie_eleve = state.get('student_text', '')

    # --- CAS A : MODE CORRECTEUR DE CONCOURS (Notation) ---
    if copie_eleve and len(copie_eleve.strip()) > 10:
        print(f"--- [NEXUS CORE] Phase 2 : Évaluation Professeur (Mode Expert) ---")
        prompt = fr"""
AGIS EN TANT QUE CORRECTEUR OFFICIEL DE CONCOURS NATIONAL EN {subject}.
MISSION : Évaluer la COPIE avec une rigueur absolue par rapport à l'ÉNONCÉ.

PROTOCOLE D'ÉVALUATION :
1. ANALYSE CRITIQUE : Vérifie les hypothèses, la justesse des calculs et la présence des unités.
2. FEEDBACK STRUCTURÉ : Pour chaque question :
   - ✅ Ce qui est acquis.
   - ❌ Erreurs de raisonnement ou de calcul (avec explication).
3. BILAN : Tableau synthétique (Points forts / Points à améliorer).
4. VERDICT : Note finale sur 20 calculée selon le barème.

STYLE : LaTeX \( ... \) impératif pour les sciences. Emojis (🎓, 🎯, ✅, ❌).

ÉNONCÉ :
{enonce}

COPIE ÉLÈVE :
{copie_eleve}
"""
    
    # --- CAS B : MODE MAÎTRE DE CONFÉRENCE (Résolution) ---
    else:
        print(f"--- [NEXUS CORE] Phase 2 : Résolution Magistrale ---")
        prompt = fr"""
AGIS EN TANT QUE MAÎTRE DE CONFÉRENCE ÉMÉRITE EN {subject}.
MISSION : Résoudre l'examen avec une clarté et une rigueur pédagogique exceptionnelle.

PROTOCOLE DE RÉSOLUTION :
1. RAPPEL THÉORIQUE : Cite les lois utilisées (ex: "D'après la loi de...").
2. DÉMONSTRATION : Résolution littérale d'abord, puis application numérique avec unités.
3. VISUEL : Utilise Markdown pour la clarté. LaTeX \[ ... \] pour les formules clés.

ÉNONCÉ :
{enonce}
"""

    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 6. NŒUD 3 : LE CHAT (Affinement Interactif) ---
def chat_feedback_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 3 : Interaction Expert-User ---")
    prompt = fr"""
Tu es le Professeur Expert. L'utilisateur souhaite affiner ta réponse précédente.

DEMANDE : {state.get('user_context', 'Révision')}
RÉPONSE PRÉCÉDENTE : {state.get('solution', 'N/A')}

MISSION : Ajuste ta réponse en maintenant la rigueur scientifique, le formatage LaTeX et la courtoisie pédagogique.
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 7. ROUTAGE ET CONSTRUCTION ---
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