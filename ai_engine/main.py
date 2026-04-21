from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uvicorn
import time
from ocr_engine import extract_text_from_exam
from agent import exam_agent

app = FastAPI(title="Nexus Engine AI - Simple Solver")

TEMP_DIR = "temp_exams"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/v1/solve")
async def solve_exam(file: UploadFile = File(...)):
    # Nettoyage du nom de fichier pour éviter les erreurs de chemin Windows
    safe_filename = f"{int(time.time())}_{os.path.basename(file.filename)}"
    temp_path = os.path.abspath(os.path.join(TEMP_DIR, safe_filename))
    
    try:
        # 1. SAUVEGARDE DU FICHIER REÇU
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. EXTRACTION OCR (Via ton moteur Tesseract/EasyOCR)
        raw_text = extract_text_from_exam(temp_path)
        
        print(f"\n--- [ÉCOSYSTÈME NEXUS : STEP 1 OCR] ---")
        if not raw_text or len(raw_text.strip()) < 5:
            print("❌ Erreur: Texte extrait trop court ou vide.")
            return {
                "status": "error", 
                "solution": "L'image est illisible ou ne contient aucun texte exploitable."
            }
        print(f"Aperçu du texte : {raw_text[:70]}...")
        
        # 3. APPEL À L'AGENT LANGGRAPH (GROQ CLOUD)
        print(f"--- [ÉCOSYSTÈME NEXUS : STEP 2 AGENT] ---")
        # On passe le dictionnaire d'entrée correspondant à AgentState
        inputs = {"raw_text": raw_text}
        
        # Invoke lance tout le workflow : cleaner -> solver
        result = exam_agent.invoke(inputs)
        
        # Récupération sécurisée du résultat final
        # LangGraph renvoie le dictionnaire d'état complet mis à jour
        solution_finale = result.get("solution")
        
        if not solution_finale:
            print(f"❌ Erreur Structure : Clés reçues -> {result.keys()}")
            return {
                "status": "partial_success",
                "ocr_extracted": raw_text,
                "solution": "L'analyse a réussi mais la mise en forme de la solution a échoué."
            }

        print(f"✅ Résolution terminée avec succès via Groq.")
        return {
            "status": "success",
            "ocr_extracted": raw_text,
            "solution": solution_finale
        }

    except Exception as e:
        print(f"❌ ERREUR CRITIQUE MOTEUR : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")
    
    finally:
        # Nettoyage systématique du fichier temporaire
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

if __name__ == "__main__":
    print("--- 🚀 NEXUS ENGINE V3 (GROQ MODE) READY ON PORT 8001 ---")
    uvicorn.run(app, host="127.0.0.1", port=8001)