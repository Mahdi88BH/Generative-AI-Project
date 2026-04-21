import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# --- 1. ÉTAT DE L'AGENT ---
class AgentState(TypedDict):
    raw_text: str
    user_context: str            # Nouveau : Message envoyé par l'utilisateur
    subject_inferred: str 
    cleaned_text: str
    solution: str

# --- 2. INITIALISATION GROQ ---
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. NŒUD 1 : L'ANALYSTE (FUSION OCR + CONTEXTE) ---
def analyze_and_clean_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 1 : Analyse contextuelle ---")
    print(f"Note utilisateur : {state.get('user_context', 'Aucune')}")
    
    prompt = f"""Tu es une IA experte en reconstruction de documents.
Voici un texte brut extrait par OCR qui contient des erreurs.

CONTEXTE FOURNI PAR L'UTILISATEUR :
{state.get('user_context', 'Pas de contexte fourni.')}

MISSION :
1. En utilisant le contexte utilisateur ET le texte brut, identifie précisément la matière.
2. Reconstruis l'énoncé de l'examen de manière fidèle. Le contexte utilisateur doit t'aider à corriger les mots que l'OCR a mal interprétés (ex: si l'utilisateur dit 'Big Data', corrige 'MPN' en 'MDX').
3. Ne réponds rien d'autre que le format imposé.

FORMAT DE RÉPONSE :
[DOMAINE] : (La matière)
[ÉNONCÉ] :
(Le texte corrigé)

TEXTE OCR BRUT :
{state['raw_text']}
"""
    response = llm.invoke(prompt)
    content = response.content
    
    domain = "Inconnu"
    cleaned = content
    if "[DOMAINE]" in content and "[ÉNONCÉ]" in content:
        parts = content.split("[ÉNONCÉ]")
        domain = parts[0].replace("[DOMAINE]", "").replace(":", "").strip()
        cleaned = parts[1].strip()

    return {"subject_inferred": domain, "cleaned_text": cleaned}

# --- 4. NŒUD 2 : LE MAÎTRE (RÉSOLUTION OPTIMISÉE) ---
def solve_exam_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 2 : Résolution ({state['subject_inferred']}) ---")
    
    prompt = f"""Tu es un professeur expert en {state['subject_inferred']}.
L'utilisateur a précisé ce contexte supplémentaire : {state.get('user_context', 'N/A')}.

MISSION :
- Résous l'énoncé de manière magistrale.
- Utilise impérativement Markdown pour la structure (titres, listes).
- Utilise LaTeX pour TOUTES les formules mathématiques ou variables ($...$).
- Ne fais aucune introduction ni conclusion.

ÉNONCÉ :
{state['cleaned_text']}
"""
    response = llm.invoke(prompt)
    return {"solution": response.content}

# --- 5. CONSTRUCTION ---
workflow = StateGraph(AgentState)

workflow.add_node("analyzer", analyze_and_clean_node)
workflow.add_node("solver", solve_exam_node)

workflow.set_entry_point("analyzer")
workflow.add_edge("analyzer", "solver")
workflow.add_edge("solver", END)

exam_agent = workflow.compile()