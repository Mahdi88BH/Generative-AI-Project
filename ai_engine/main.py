import os
import shutil
import time
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from pdf2image import convert_from_path
from agent import exam_agent

app = FastAPI(title="Nexus AI - Autonome Expert (Solve & Auto-Grade)")

# --- CONFIGURATION STYLE TERMINAL ---
G, C, Y, R, B = "\033[92m", "\033[96m", "\033[93m", "\033[0m", "\033[1m"
TEMP_DIR = "temp_exams"
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin" 
os.makedirs(TEMP_DIR, exist_ok=True)

def anim(msg, t=1.0):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end = time.time() + t
    idx = 0
    while time.time() < end:
        sys.stdout.write(f"\r{C}{chars[idx % len(chars)]} {msg}...{R}")
        sys.stdout.flush()
        time.sleep(0.1)
        idx += 1
    sys.stdout.write(f"\r{G}✔ {msg} OK{R}\n")

def save_file(upload_file):
    """Extraction sécurisée du nom et sauvegarde locale."""
    if not upload_file: return None
    pure_name = os.path.basename(upload_file.filename)
    path = os.path.abspath(os.path.join(TEMP_DIR, pure_name))
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return path

def handle_pdf(path, paths_to_clean):
    """Éclate un PDF en plusieurs images JPEG pour l'OCR."""
    images = []
    if path and path.lower().endswith(".pdf"):
        anim("PDF-CONVERTER: Segmentation des pages étudiant")
        pages = convert_from_path(path, poppler_path=POPPLER_PATH)
        for i, page in enumerate(pages):
            p_path = os.path.join(TEMP_DIR, f"tmp_copie_p{i}_{int(time.time())}.jpg")
            page.save(p_path, "JPEG")
            images.append(p_path)
            paths_to_clean.append(p_path)
    elif path:
        images = [path]
    return images

@app.post("/api/v1/process")
async def process_exam(
    enonce: UploadFile = File(...), 
    copie: UploadFile = File(None)  # Optionnel : déclenche le mode Professeur
):
    print(f"\n{B}{Y}⚡ RÉCEPTION DU FLUX ACADÉMIQUE NEXUS{R}")
    start_total = time.time()
    paths_to_clean = []

    try:
        # 1. Sauvegarde de l'épreuve (Enoncé)
        path_enonce = save_file(enonce)
        paths_to_clean.append(path_enonce)

        # 2. LOGIQUE DÉCISIONNELLE
        if copie is None:
            # --- MODE ÉTUDIANT : GÉNÉRATION DE RÉSOLUTION ---
            print(f"{B}{C}🎯 MODE DÉTECTÉ : RÉSOLUTION ACADÉMIQUE{R}")
            anim("AGENTS: Résolution de l'épreuve par l'IA expert")
            
            result = exam_agent.invoke({"image_path": path_enonce, "mode": "solve"})
            
            dt = round(time.time() - start_total, 2)
            print(f"{G}{B}✅ SOLUTION GÉNÉRÉE ({dt}s){R}")
            
            return {
                "status": "success",
                "mode": "student_solve",
                "solution": result.get("solution")
            }

        else:
            # --- MODE PROFESSEUR : AUTO-GRADING (Sans besoin de corrigé type) ---
            print(f"{B}{Y}🎓 MODE DÉTECTÉ : CORRECTION EXPERT (Auto-Grader){R}")
            
            path_copie = save_file(copie)
            paths_to_clean.append(path_copie)

            # Conversion si PDF étudiant
            copie_images = handle_pdf(path_copie, paths_to_clean)

            anim(f"AGENTS: Analyse comparative de {len(copie_images)} page(s)")
            
            # L'IA résoudra l'épreuve elle-même pour noter la copie
            result = exam_agent.invoke({
                "enonce_path": path_enonce,
                "copie_paths": copie_images,
                "mode": "grade"
            })
            
            dt = round(time.time() - start_total, 2)
            print(f"{G}{B}✅ RAPPORT ET NOTE GÉNÉRÉS ({dt}s){R}")

            return {
                "status": "success",
                "mode": "professor_grade",
                "rapport": result.get("rapport_correction")
            }

    except Exception as e:
        print(f"{Y}❌ ERREUR SYSTÈME: {str(e)}{R}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage des fichiers temporaires (épreuve + copies + pages PDF)
        for p in paths_to_clean:
            if p and os.path.exists(p):
                try: os.remove(p)
                except: pass

if __name__ == "__main__":
    print(f"{G}{B}--- NEXUS ENGINE V3.0 : PRÊT POUR TOUTES DISCIPLINES ---{R}")
    uvicorn.run(app, host="127.0.0.1", port=8001)