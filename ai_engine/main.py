from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uvicorn
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Engine AI Exam Solver - Debug Mode")

TEMP_DIR = "temp_exams"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/v1/solve")
async def solve_exam(file: UploadFile = File(...)):
    safe_filename = os.path.basename(file.filename)
    temp_path = os.path.join(TEMP_DIR, safe_filename)
    
    try:
        # 1. Sauvegarde
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. OCR avec LOG
        raw_text = extract_text_from_exam(temp_path)
        print(f"\n--- [STEP 1: OCR] ---")
        print(f"Texte extrait (50 p. car.): {raw_text[:50]}...")
        
        if not raw_text or len(raw_text.strip()) < 5:
            print("❌ Erreur: OCR vide ou trop court.")
            return {"status": "error", "solution": "L'image est illisible ou ne contient pas de texte."}

        # 3. AGENT avec LOG DE STRUCTURE
        print(f"--- [STEP 2: AGENT INVOKE] ---")
        inputs = {"raw_text": raw_text}
        result = exam_agent.invoke(inputs)
        
        # LOG CRITIQUE : Affiche la structure exacte reçue de LangGraph
        print(f"Structure du dictionnaire reçu : {result.keys()}")
        print(f"Contenu complet du résultat : {result}")

        # Extraction sécurisée : On teste plusieurs clés au cas où
        solution = result.get("solution") or result.get("solver", {}).get("solution")
        
        if not solution:
            print("❌ Erreur: L'agent a répondu mais la clé 'solution' est introuvable.")
            solution = "L'IA a traité la demande mais n'a pas pu formater la réponse."

        return {
            "status": "success",
            "ocr_extracted": raw_text,
            "solution": solution
        }

    except Exception as e:
        print(f"❌ ERREUR CRITIQUE : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8001)