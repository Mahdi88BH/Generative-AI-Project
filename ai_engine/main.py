import os
import shutil
import time
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from agent import exam_agent

app = FastAPI(title="Nexus AI - Multi-Images Processor")

TEMP_DIR = "temp_exams"
os.makedirs(TEMP_DIR, exist_ok=True)

def save_file(upload_file: UploadFile) -> str:
    pure_name = os.path.basename(upload_file.filename)
    # Ajout d'un timestamp pour éviter les écrasements
    safe_name = f"{int(time.time())}_{pure_name}"
    path = os.path.abspath(os.path.join(TEMP_DIR, safe_name))
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return path

@app.post("/api/v1/process")
async def process_exam(
    enonce: List[UploadFile] = File(...), 
    copie: Optional[List[UploadFile]] = File(None)
):
    start_total = time.time()
    paths_to_clean = []

    try:
        # 1. Sauvegarde des images de l'énoncé
        path_enonces = []
        for file in enonce:
            p = save_file(file)
            path_enonces.append(p)
            paths_to_clean.append(p)

        # 2. LOGIQUE DÉCISIONNELLE
        if not copie:
            # --- MODE RÉSOLUTION ---
            print("🎯 MODE : RÉSOLUTION ACADÉMIQUE")
            result = exam_agent.invoke({
                "mode": "solve",
                "enonce_paths": path_enonces,
                "copie_paths": []
            })
            return {"status": "success", "mode": "solve", "solution": result.get("solution")}

        else:
            # --- MODE CORRECTION ---
            print("🎓 MODE : AUTO-GRADER")
            path_copies = []
            for file in copie:
                p = save_file(file)
                path_copies.append(p)
                paths_to_clean.append(p)

            result = exam_agent.invoke({
                "mode": "grade",
                "enonce_paths": path_enonces,
                "copie_paths": path_copies
            })
            return {"status": "success", "mode": "grade", "rapport": result.get("rapport_correction")}

    except Exception as e:
        print(f"❌ ERREUR SYSTÈME: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage des fichiers temporaires (Important pour ne pas saturer le disque)
        for p in paths_to_clean:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

if __name__ == "__main__":
    print("--- NEXUS ENGINE V3.0 ONLINE ---")
    uvicorn.run(app, host="127.0.0.1", port=8001)