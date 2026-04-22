from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import os
import uvicorn
import time
import asyncio
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Nexus Engine AI - Auto-Grader Core")

TEMP_DIR = "temp_exams"
os.makedirs(TEMP_DIR, exist_ok=True)

# Fonction utilitaire pour sauvegarder les fichiers entrants
def save_temp_file(upload_file: UploadFile):
    ext = os.path.splitext(upload_file.filename)[1]
    safe_filename = f"nexus_{int(time.time() * 1000)}{ext}"
    temp_path = os.path.join(TEMP_DIR, safe_filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return temp_path

@app.post("/api/v1/solve")
async def solve_exam(
    file: UploadFile = File(None),           # Énoncé (Exam)
    student_copy: UploadFile = File(None),   # Copie de l'élève (Correction)
    user_context: str = Form(""),
    existing_solution: str = Form("")
):
    raw_text_enonce = ""
    raw_text_student = ""
    paths_to_clean = []

    try:
        loop = asyncio.get_event_loop()

        # --- 1. TRAITEMENT DE L'ÉNONCÉ ---
        if file and file.filename:
            path = save_temp_file(file)
            paths_to_clean.append(path)
            print(f"--- [NEXUS] Énoncé reçu : {file.filename} ---")
            raw_text_enonce = await loop.run_in_executor(None, extract_text_from_exam, path)

        # --- 2. TRAITEMENT DE LA COPIE ÉLÈVE ---
        if student_copy and student_copy.filename:
            path_student = save_temp_file(student_copy)
            paths_to_clean.append(path_student)
            print(f"--- [NEXUS] Copie élève reçue : {student_copy.filename} ---")
            raw_text_student = await loop.run_in_executor(None, extract_text_from_exam, path_student)

        # --- GESTION DES CAS VIDES ---
        if not file and not student_copy:
            raw_text_enonce = "CHAT_INTERACTION_ONLY"
            print(f"--- [NEXUS] Mode Chat uniquement ---")

        # --- DEBUG CONSOLE ---
        print("\n" + "🔍" * 15)
        print(f"OCR Énoncé : {len(raw_text_enonce)} chars")
        print(f"OCR Copie   : {len(raw_text_student)} chars")
        print("🔍" * 15 + "\n")

        # --- PRÉPARATION DES ENTRÉES POUR L'AGENT ---
        inputs = {
            "raw_text": raw_text_enonce,
            "student_text": raw_text_student, # Transmis à l'agent pour le mode notation
            "user_context": user_context,
            "solution": existing_solution
        }
        
        # Exécution de l'intelligence artificielle
        result = exam_agent.invoke(inputs)
        
        return {
            "status": "success",
            "subject": result.get("subject_inferred", "Général"),
            "solution": result.get("solution", "L'agent n'a pas pu formuler de réponse.")
        }

    except Exception as e:
        print(f"❌ ERREUR CRITIQUE : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Nexus Engine Error: {str(e)}")
    
    finally:
        # Nettoyage de TOUS les fichiers temporaires créés
        for p in paths_to_clean:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")