from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uvicorn
from agent import exam_agent

app = FastAPI(title="Nexus AI - Exam Solver")

TEMP_DIR = "temp_exams"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/v1/solve")
async def solve_exam(file: UploadFile = File(...)):
    safe_filename = os.path.basename(file.filename)
    # Utilisation du chemin absolu pour éviter les erreurs de lecture du MCP
    temp_path = os.path.abspath(os.path.join(TEMP_DIR, safe_filename))
    
    try:
        # 1. Sauvegarde du fichier pour que le serveur MCP puisse le lire
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"--- [STEP 1: FILE SAVED] --- {temp_path}")

        # 2. APPEL DE L'AGENT : On passe 'image_path' et NON 'raw_text'
        print(f"--- [STEP 2: AGENT INVOKE] ---")
        inputs = {"image_path": temp_path} 
        result = exam_agent.invoke(inputs)
        
        # 3. Extraction sécurisée du résultat
        solution = result.get("solution")
        raw_ocr = result.get("raw_text")

        return {
            "status": "success",
            "ocr_extracted": raw_ocr,
            "solution": solution
        }

    except Exception as e:
        print(f"❌ ERREUR CRITIQUE : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # On attend un peu ou on gère la suppression après le processus
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass # Évite de crash si le fichier est encore utilisé

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)