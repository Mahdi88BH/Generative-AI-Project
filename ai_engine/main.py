import os
import shutil
import time
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from agent import exam_agent

app = FastAPI(title="Nexus AI - Demo Mode")

# Couleurs Terminal
G, C, Y, R, B = "\033[92m", "\033[96m", "\033[93m", "\033[0m", "\033[1m"

# --- CONFIGURATION DOSSIER ---
TEMP_DIR = "temp_exams"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

def anim(msg, t=1.2):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end = time.time() + t
    idx = 0
    while time.time() < end:
        sys.stdout.write(f"\r{C}{chars[idx % len(chars)]} {msg}...{R}")
        sys.stdout.flush()
        time.sleep(0.1)
        idx += 1
    sys.stdout.write(f"\r{G}✔ {msg} OK{R}\n")

@app.post("/api/v1/solve")
async def solve_exam(file: UploadFile = File(...)):
    print(f"\n{B}{Y}⚡ INITIALISATION DU CYCLE NEXUS{R}")
    
    # --- LA CORRECTION EST ICI ---
    # os.path.basename retire "exams/" du nom pour ne garder que "image.jpg"
    pure_filename = os.path.basename(file.filename) 
    temp_path = os.path.abspath(os.path.join(TEMP_DIR, pure_filename))
    
    print(f"{C}DEBUG: Cible locale -> {temp_path}{R}")

    try:
        anim("IO-BUFFER: Écriture du flux binaire")
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        anim("AGENTS: Activation de la boucle LangGraph")
        start = time.time()
        
        # Transmission à l'agent
        result = exam_agent.invoke({"image_path": temp_path})
        
        dt = round(time.time() - start, 2)
        print(f"{G}{B}✅ ANALYSE TERMINÉE ({dt}s){R}")
        
        return {
            "status": "success",
            "ocr_extracted": result.get("raw_text"),
            "solution": result.get("solution")
        }

    except Exception as e:
        print(f"{Y}❌ CRASH CYCLE: {str(e)}{R}")
        # On renvoie l'erreur propre à Django
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage systématique
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

if __name__ == "__main__":
    print(f"{G}{B}NEXUS CORE ONLINE - PORT 8001{R}")
    uvicorn.run(app, host="127.0.0.1", port=8001)