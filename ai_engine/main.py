from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import os
import uvicorn
import time
import asyncio
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Nexus Engine AI - Interactive Core")

TEMP_DIR = "temp_exams"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/v1/solve")
async def solve_exam(
    file: UploadFile = File(None),           
    user_context: str = Form(""),            
    existing_solution: str = Form("")        
):
    raw_text = ""
    temp_path = None

    try:
        # --- CAS 1 : NOUVEL ENVOI (Image ou PDF) ---
        if file and file.filename:
            # Génération d'un nom sécurisé pour éviter les conflits
            ext = os.path.splitext(file.filename)[1]
            safe_filename = f"nexus_{int(time.time())}{ext}"
            temp_path = os.path.join(TEMP_DIR, safe_filename)
            
            # Sauvegarde asynchrone du fichier
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            print(f"--- [NEXUS] Fichier reçu : {file.filename} ---")
            print("\n" + "🚀" * 15)
            print("--- [DEBUG] TEXTE EXTRAIT PAR L'OCR ---")
            if raw_text:
                print(raw_text[:1000]) # On affiche les 1000 premiers caractères
            else:
                print("⚠️ ATTENTION : L'EXTRACTION EST VIDE !")
            print("🚀" * 15 + "\n")
            # Extraction via le moteur hybride (Direct PDF ou OCR)
            # On utilise run_in_executor si l'OCR prend du temps pour ne pas bloquer l'event loop
            loop = asyncio.get_event_loop()
            raw_text = await loop.run_in_executor(None, extract_text_from_exam, temp_path)
            
            if not raw_text or len(raw_text.strip()) < 2:
                return {"status": "error", "solution": "Le document semble vide ou illisible."}

        # --- CAS 2 : MODE CHAT (Interaction seule) ---
        else:
            # On passe une chaîne identifiable pour que l'agent sache qu'il n'y a pas d'OCR
            raw_text = "CHAT_INTERACTION_ONLY"
            print(f"--- [NEXUS] Requête de Chat reçue ---")

        # --- EXÉCUTION DE L'AGENT ---
        inputs = {
            "raw_text": raw_text,
            "user_context": user_context,
            "solution": existing_solution
        }
        
        # L'agent LangGraph gère le routage interne (Analyzer ou Chat_Feedback)
        result = exam_agent.invoke(inputs)
        
        return {
            "status": "success",
            "subject": result.get("subject_inferred", "Général"),
            "solution": result.get("solution", "L'agent n'a pas pu formuler de réponse.")
        }

    except Exception as e:
        print(f"❌ ERREUR CRITIQUE : {str(e)}")
        # On ne renvoie pas l'erreur brute en prod, mais utile pour ton debug
        raise HTTPException(status_code=500, detail=f"Nexus Engine Error: {str(e)}")
    
    finally:
        # Nettoyage automatique du fichier temporaire
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"⚠️ Nettoyage échoué : {e}")

if __name__ == "__main__":
    # Paramètres Uvicorn optimisés
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")