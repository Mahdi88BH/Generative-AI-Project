# ai_engine/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uvicorn
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Engine AI Exam Solver")

# --- Configuration du dossier temporaire ---
TEMP_DIR = "temp_exams"

# On s'assure que le dossier existe au démarrage
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)
    print(f"✅ Dossier '{TEMP_DIR}' prêt.")

@app.post("/api/v1/solve")
async def solve_exam(file: UploadFile = File(...)):
    # --- LA CORRECTION EST ICI ---
    # os.path.basename extrait uniquement 'image.png' même si Django envoie 'exams/image.png'
    safe_filename = os.path.basename(file.filename)
    temp_path = os.path.join(TEMP_DIR, safe_filename)
    
    try:
        # 1. Sauvegarde sécurisée du fichier
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Exécution de l'OCR
        raw_text = extract_text_from_exam(temp_path)
        
        if not raw_text or len(raw_text.strip()) < 5:
            return {"status": "error", "message": "Texte insuffisant détecté."}

        # 3. Exécution de l'Agent IA
        inputs = {"raw_text": raw_text}
        result = exam_agent.invoke(inputs)
        
        return {
            "status": "success",
            "ocr_extracted": raw_text,
            "solution": result.get("solution", "Erreur de génération")
        }

    except Exception as e:
        # On log l'erreur exacte dans la console FastAPI pour le debug
        print(f"❌ Erreur Interne Serveur : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage automatique : on ne laisse aucune trace sur le disque
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"⚠️ Impossible de supprimer le fichier temporaire : {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)