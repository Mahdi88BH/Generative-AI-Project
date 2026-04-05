# ai_engine/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from .ocr_engine import extract_text_from_exam
from .agent import exam_agent

app = FastAPI(title="AI Exam Solver Engine")

@app.post("/api/v1/solve")
async def solve_exam(file: UploadFile = File(...)):
    # 1. Sauvegarde temporaire du fichier reçu de Django
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Pipeline Vision (OCR)
        raw_text = extract_text_from_exam(temp_filename)
        
        # 3. Pipeline Agentic (LangGraph)
        inputs = {"raw_text": raw_text}
        result = exam_agent.invoke(inputs)
        
        return {
            "status": "success",
            "ocr_text": raw_text,
            "solution": result["solution"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Nettoyage du fichier temporaire
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)