# ai_engine/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uvicorn

# Imports de tes fichiers locaux
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Engine AI Exam Solver")

@app.post("/api/v1/solve")
async def solve_exam(file: UploadFile = File(...)):
    # 1. Sauvegarde temporaire du fichier entrant
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Exécution de l'OCR (Vision)
        raw_text = extract_text_from_exam(temp_path)
        
        if not raw_text or len(raw_text.strip()) < 5:
            return {"status": "error", "message": "Texte insuffisant détecté sur l'image."}

        # 3. Exécution du Graphe d'Agents (Reasoning)
        # On appelle le graphe LangGraph compilé dans agent.py
        inputs = {"raw_text": raw_text}
        result = exam_agent.invoke(inputs)
        
        return {
            "status": "success",
            "ocr_extracted": raw_text,
            "solution": result.get("solution", "Erreur de génération de solution")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage systématique du fichier temporaire
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)