import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# --- 1. ÉTAT DE L'AGENT ---
# Ajout d'une mémoire contextuelle : "subject_inferred"
class AgentState(TypedDict):
    raw_text: str
    subject_inferred: str 
    cleaned_text: str
    solution: str

# --- 2. INITIALISATION DU MOTEUR (GROQ) ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1, # Température basse pour une précision académique maximale
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. NŒUD 1 : L'ANALYSTE (AUTO-DÉTECTION & NETTOYAGE) ---
def analyze_and_clean_node(state: AgentState):
    print("--- [NEXUS CORE] Phase 1 : Analyse Cognitive & Nettoyage ---")
    
    prompt = f"""Tu es une IA experte en reconstruction de documents académiques endommagés.
Voici un texte brut extrait par OCR (reconnaissance optique), qui contient des erreurs de lecture.

MISSION :
1. Analyse le texte et déduis de manière 100% autonome le domaine académique précis (Mathématiques, Base de données, Physique, etc.).
2. Utilise la logique de ce domaine pour corriger toutes les hallucinations de l'OCR (ex: corrige 'MPN' en 'MDX' si c'est du Big Data, 'S' en '5' si c'est des maths).
3. Reconstruis l'énoncé de manière claire et académique.

FORMAT DE RÉPONSE OBLIGATOIRE (Ne réponds rien d'autre) :
[DOMAINE] : (Indique ici la matière en 3 mots maximum)
[ÉNONCÉ] :
(Le texte de l'examen parfaitement corrigé)

TEXTE OCR BRUT :
{state['raw_text']}
"""
    response = llm.invoke(prompt)
    content = response.content
    
    # Extraction intelligente du domaine et du texte
    domain = "Matière non identifiée"
    cleaned = content
    
    if "[DOMAINE]" in content and "[ÉNONCÉ]" in content:
        parts = content.split("[ÉNONCÉ]")
        domain = parts[0].replace("[DOMAINE]", "").replace(":", "").strip()
        cleaned = parts[1].strip()

    return {"subject_inferred": domain, "cleaned_text": cleaned}

# --- 4. NŒUD 2 : LE MAÎTRE (RÉSOLUTION CONTEXTUELLE) ---
def solve_exam_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 2 : Résolution Experte ({state['subject_inferred']}) ---")
    
    # Le prompt s'adapte dynamiquement grâce à la variable {state['subject_inferred']}
    prompt = f"""Tu es un professeur d'université de rang A, expert mondial en {state['subject_inferred']}.
On te confie cet examen officiel à résoudre. Ton but est de fournir le corrigé type parfait (Note visée : 20/20).

CONSIGNES STRICTES :
- Agis de manière 100% directe. Ne fais AUCUNE phrase d'introduction du type "Voici la solution".
- Résous chaque question étape par étape avec une pédagogie absolue.
- Justifie chaque réponse, explique la logique derrière tes calculs ou ton code.
- Pour TOUTE formule mathématique, équation ou variable, utilise impérativement le format LaTeX (ex: $x = 2$, $$y = mx + b$$).

ÉNONCÉ À RÉSOUDRE :
{state['cleaned_text']}
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 5. CONSTRUCTION DU GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("analyzer", analyze_and_clean_node)
workflow.add_node("solver", solve_exam_node)

workflow.set_entry_point("analyzer")
workflow.add_edge("analyzer", "solver")
workflow.add_edge("solver", END)

exam_agent = workflow.compile()