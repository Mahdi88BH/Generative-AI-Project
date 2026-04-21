import os
import shutil
import time
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from agent import exam_agent

app = FastAPI(title="Nexus AI - Demo Mode")

# Style Terminal
G = "\033[92m" # Green
C = "\033[96m" # Cyan
Y = "\033[93m" # Yellow
R = "\033[0m"  # Reset
B = "\033[1m"  # Bold

def anim(msg, t=1.5):
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
    temp_path = os.path.abspath(os.path.join("temp_exams", file.filename))
    
    try:
        anim("IO-BUFFER: Écriture du flux binaire")
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        anim("AGENTS: Activation de la boucle LangGraph")
        start = time.time()
        result = exam_agent.invoke({"image_path": temp_path})
        dt = round(time.time() - start, 2)
        
        print(f"{G}{B}✅ ANALYSE TERMINÉE ({dt}s){R}")
        print(f"{C}--- OCR Extrait ---{R}\n{result.get('raw_text')[:100]}...")
        
        return {
            "status": "success",
            "ocr_extracted": result.get("raw_text"),
            "solution": result.get("solution")
        }
    except Exception as e:
        print(f"{Y}❌ CRASH CYCLE: {e}{R}")
        raise HTTPException(500, detail=str(e))
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

if __name__ == "__main__":
    print(f"{G}{B}NEXUS CORE ONLINE - PORT 8001{R}")
    uvicorn.run(app, host="127.0.0.1", port=8001)