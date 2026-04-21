from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import os
import uvicorn
import time
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Nexus Engine AI - Interactive Core")

TEMP_DIR = "temp_exams"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/v1/solve")
async def solve_exam(
    file: UploadFile = File(None),           # Optionnel pour le mode Chat
    user_context: str = Form(""),            # Message de l'utilisateur
    existing_solution: str = Form("")        # La solution actuelle en base (pour modif)
):
    raw_text = ""
    temp_path = None

    try:
        # --- CAS 1 : NOUVEL ENVOI (Image ou PDF) ---
        if file:
            safe_filename = f"{int(time.time())}_{os.path.basename(file.filename)}"
            temp_path = os.path.abspath(os.path.join(TEMP_DIR, safe_filename))
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extraction OCR
            raw_text = extract_text_from_exam(temp_path)
            
            if not raw_text or len(raw_text.strip()) < 5:
                return {"status": "error", "solution": "Contenu illisible."}
            
            print(f"--- [NEXUS] Nouveau Scan OCR effectué ---")

        # --- CAS 2 : MODE CHAT (Interaction seule) ---
        else:
            raw_text = "MODE_CHAT" # L'agent saura qu'il doit utiliser existing_solution
            print(f"--- [NEXUS] Interaction Chat détectée ---")

        # --- APPEL À L'AGENT AGENTIQUE ---
        # On passe toutes les données : l'agent décidera du nœud à utiliser
        inputs = {
            "raw_text": raw_text,
            "user_context": user_context,
            "solution": existing_solution
        }
        
        result = exam_agent.invoke(inputs)
        
        return {
            "status": "success",
            "subject": result.get("subject_inferred", "Général"),
            "solution": result.get("solution", "Erreur de génération.")
        }

    except Exception as e:
        print(f"❌ ERREUR MOTEUR : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    print("\n🚀 NEXUS ENGINE V3.2 : ONLINE | Ready for Chat & Vision")
    uvicorn.run(app, host="127.0.0.1", port=8001)