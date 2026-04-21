from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import os
import uvicorn
import time
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Nexus Engine AI - Contextual Solver")

TEMP_DIR = "temp_exams"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/v1/solve")
async def solve_exam(
    file: UploadFile = File(...), 
    user_context: str = Form("") # On récupère le contexte envoyé par Django
):
    # Nettoyage et préparation du chemin
    safe_filename = f"{int(time.time())}_{os.path.basename(file.filename)}"
    temp_path = os.path.abspath(os.path.join(TEMP_DIR, safe_filename))
    
    try:
        # 1. SAUVEGARDE DE L'IMAGE
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. EXTRACTION OCR
        raw_text = extract_text_from_exam(temp_path)
        
        print(f"\n--- [NEXUS ENGINE] STEP 1 : OCR ---")
        if not raw_text or len(raw_text.strip()) < 5:
            return {
                "status": "error", 
                "solution": "L'image est illisible pour le moteur OCR."
            }
        
        # 3. APPEL À L'AGENT AVEC CONTEXTE
        print(f"--- [NEXUS ENGINE] STEP 2 : AGENT AGENTIQUE ---")
        print(f"Context reçu: {user_context}")
        
        # On prépare le dictionnaire d'entrée pour LangGraph
        # IMPORTANT : Les clés doivent matcher ton AgentState dans agent.py
        inputs = {
            "raw_text": raw_text,
            "user_context": user_context
        }
        
        # Exécution du workflow (Analyzer -> Solver)
        result = exam_agent.invoke(inputs)
        
        solution_finale = result.get("solution")
        domain_detecte = result.get("subject_inferred", "Général")

        if not solution_finale:
            return {
                "status": "error",
                "solution": "L'agent n'a pas pu générer de solution."
            }

        print(f"✅ Succès : Domaine [{domain_detecte}] résolu.")
        
        return {
            "status": "success",
            "ocr_extracted": raw_text,
            "subject": domain_detecte,
            "solution": solution_finale
        }

    except Exception as e:
        print(f"❌ ERREUR MOTEUR : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" 🚀 NEXUS ENGINE V3.2 : ONLINE ")
    print(" 📡 Listening on : http://127.0.0.1:8001")
    print("="*50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8001)