from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import os
import uvicorn
import time
import asyncio
# L'OCR est maintenant géré par l'agent via MCP, donc on n'importe plus extract_text ici
from agent import exam_agent

app = FastAPI(title="Nexus Engine AI - Core Multi-Agents")

# Dossier temporaire pour stocker les images/PDF avant analyse MCP
TEMP_DIR = os.path.abspath("temp_exams")
os.makedirs(TEMP_DIR, exist_ok=True)

def save_temp_file(upload_file: UploadFile):
    """Sauvegarde le fichier et retourne le chemin ABSOLU pour le serveur MCP."""
    ext = os.path.splitext(upload_file.filename)[1]
    safe_filename = f"nexus_{int(time.time() * 1000)}{ext}"
    temp_path = os.path.join(TEMP_DIR, safe_filename)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return os.path.abspath(temp_path)

@app.post("/api/v1/solve")
async def solve_exam(
    file: UploadFile = File(None),           # Énoncé
    student_copy: UploadFile = File(None),   # Copie élève
    user_context: str = Form(""),
    existing_solution: str = Form("")
):
    paths_to_clean = []
    path_enonce = "CHAT_MODE"
    path_student = ""

    try:
        # --- 1. STOCKAGE DES FICHIERS ---
        # On ne fait plus d'OCR ici. On prépare les chemins pour l'Agent.
        if file and file.filename:
            path_enonce = save_temp_file(file)
            paths_to_clean.append(path_enonce)
            print(f"--- [NEXUS] Fichier énoncé prêt : {path_enonce} ---")

        if student_copy and student_copy.filename:
            path_student = save_temp_file(student_copy)
            paths_to_clean.append(path_student)
            print(f"--- [NEXUS] Fichier copie élève prêt : {path_student} ---")

        # --- 2. INVOCATION DE L'AGENT ---
        # On utilise asyncio.to_thread pour ne pas bloquer l'API pendant le travail de l'IA
        inputs = {
            "raw_text": path_enonce,
            "student_text": path_student,
            "user_context": user_context,
            "solution": existing_solution
        }
        
        print(f"--- [NEXUS] Lancement de l'Agent LangGraph ---")
        result = await asyncio.to_thread(exam_agent.invoke, inputs)
        
        return {
            "status": "success",
            "subject": result.get("subject_inferred", "Général"),
            "solution": result.get("solution", "L'agent n'a pas pu formuler de réponse.")
        }

    except Exception as e:
        print(f"❌ ERREUR SYSTÈME : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Nexus Engine Error: {str(e)}")
    
    finally:
        # --- 3. NETTOYAGE SÉCURISÉ ---
        # On attend 1 seconde pour laisser le temps au moteur OCR de libérer les fichiers
        await asyncio.sleep(1)
        for p in paths_to_clean:
            if os.path.exists(p):
                try:
                    os.remove(p)
                    print(f"--- [NEXUS] Nettoyage : {os.path.basename(p)} supprimé ---")
                except Exception as e:
                    print(f"⚠️ Erreur nettoyage : {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")