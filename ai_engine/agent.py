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

# --- 3. NŒUD 1 : L'ANALYSTE (FUSION OCR + CONTEXTE) ---
def analyze_and_clean_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 1 : Analyse contextuelle ---")
    
    prompt = f"""Tu es une IA experte en reconstruction de documents académiques.
Voici un texte brut extrait par OCR qui contient des erreurs.

CONTEXTE FOURNI PAR L'UTILISATEUR :
{state.get('user_context', 'Pas de contexte fourni.')}

MISSION :
1. Identifie précisément la matière en croisant l'OCR et le contexte utilisateur.
2. Reconstruis l'énoncé de manière fidèle et structurée.
3. Utilise des emojis discrets pour structurer l'énoncé (ex: 📝, 🔢, 💡).

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

# --- 4. NŒUD 2 : LE MAÎTRE (RÉSOLUTION OPTIMISÉE + EMOJIS) ---
def solve_exam_node(state: AgentState):
    print(f"--- [NEXUS CORE] Phase 2 : Résolution ({state['subject_inferred']}) ---")
    
    prompt = f"""Tu es un professeur expert en {state['subject_inferred']}.
Ton but est de fournir un corrigé d'une qualité exceptionnelle et visuellement agréable.

MISSION :
- Résous l'énoncé de manière magistrale avec un ton pédagogique.
- Utilise des emojis pour rendre la lecture fluide (ex: ✅ pour les réponses, ⚙️ pour les calculs, 📚 pour la théorie, 🚀 pour les conclusions).
- Utilise impérativement Markdown (titres #, gras **).
- MATHÉMATIQUES : Utilise \( ... \) pour les formules en ligne et \[ ... \] pour les blocs isolés. C'est CRUCIAL pour le rendu.
- Ne fais aucune introduction ni conclusion conversationnelle.

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