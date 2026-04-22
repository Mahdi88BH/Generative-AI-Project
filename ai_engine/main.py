from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import os
import uvicorn
import time
import asyncio
# On n'importe plus extract_text_from_exam ici, c'est l'agent qui s'en chargera via MCP
from agent import exam_agent

app = FastAPI(title="Nexus Engine AI - MCP Grader Core")

TEMP_DIR = "temp_exams"
os.makedirs(TEMP_DIR, exist_ok=True)

def save_temp_file(upload_file: UploadFile):
    ext = os.path.splitext(upload_file.filename)[1]
    # On garde un nom fixe ou traçable pour que le serveur MCP y accède
    safe_filename = f"nexus_{int(time.time() * 1000)}{ext}"
    temp_path = os.path.abspath(os.path.join(TEMP_DIR, safe_filename))
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return temp_path

@app.post("/api/v1/solve")
async def solve_exam(
    file: UploadFile = File(None),           
    student_copy: UploadFile = File(None),   
    user_context: str = Form(""),
    existing_solution: str = Form("")
):
    path_enonce = ""
    path_student = ""
    paths_to_clean = []

    try:
        # --- 1. SAUVEGARDE DES FICHIERS (On passe les CHEMINS à l'agent) ---
        if file and file.filename:
            path_enonce = save_temp_file(file)
            paths_to_clean.append(path_enonce)
            print(f"--- [NEXUS MCP] Énoncé enregistré : {path_enonce} ---")

        if student_copy and student_copy.filename:
            path_student = save_temp_file(student_copy)
            paths_to_clean.append(path_student)
            print(f"--- [NEXUS MCP] Copie enregistrée : {path_student} ---")

        # --- 2. PRÉPARATION DES INPUTS ---
        # Au lieu du texte brut, on envoie les chemins de fichiers (ou le message de chat)
        inputs = {
            "raw_text": path_enonce if path_enonce else "CHAT_MODE",
            "student_text": path_student if path_student else "",
            "user_context": user_context,
            "solution": existing_solution
        }
        
        # --- 3. EXÉCUTION DE L'AGENT ---
        # L'agent va détecter si raw_text est un chemin et appeler son outil MCP read_document
        result = await asyncio.to_thread(exam_agent.invoke, inputs)
        
        return {
            "status": "success",
            "subject": result.get("subject_inferred", "Général"),
            "solution": result.get("solution", "L'agent n'a pas pu formuler de réponse.")
        }

    except Exception as e:
        print(f"❌ ERREUR CRITIQUE : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Nexus Engine Error: {str(e)}")
    
    finally:
        # On attend un tout petit peu que l'agent libère les fichiers si nécessaire
        await asyncio.sleep(0.5) 
        for p in paths_to_clean:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")