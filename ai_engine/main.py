import os
import shutil
import time
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from pdf2image import convert_from_path
from agent import exam_agent

app = FastAPI(title="Nexus AI - Hybrid Processor (Solve & Grade)")

# --- CONFIGURATION STYLE TERMINAL ---
G, C, Y, R, B = "\033[92m", "\033[96m", "\033[93m", "\033[0m", "\033[1m"
TEMP_DIR = "temp_exams"
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin" # Vérifie ce chemin sur ton PC
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
    """Nettoie le nom du fichier et le sauvegarde localement."""
    if not upload_file: return None
    pure_name = os.path.basename(upload_file.filename)
    path = os.path.abspath(os.path.join(TEMP_DIR, pure_name))
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return path

def handle_pdf(path, paths_to_clean):
    """Convertit un PDF en liste de chemins d'images JPEG."""
    images = []
    if path.lower().endswith(".pdf"):
        anim("PDF-CONVERTER: Extraction des pages")
        pages = convert_from_path(path, poppler_path=POPPLER_PATH)
        for i, page in enumerate(pages):
            p_path = os.path.join(TEMP_DIR, f"tmp_page_{i}_{int(time.time())}.jpg")
            page.save(p_path, "JPEG")
            images.append(p_path)
            paths_to_clean.append(p_path)
    else:
        images = [path]
    return images

@app.post("/api/v1/process")
async def process_exam(
    enonce: UploadFile = File(...), 
    corrige: UploadFile = File(None), 
    copie: UploadFile = File(None)
):
    print(f"\n{B}{Y}⚡ DÉTECTION DU FLUX D'ENTRÉE NEXUS{R}")
    start_total = time.time()
    paths_to_clean = []

    try:
        # 1. Sauvegarde obligatoire de l'énoncé
        path_enonce = save_file(enonce)
        paths_to_clean.append(path_enonce)

        # 2. LOGIQUE DE DÉCISION DU MODE
        if not corrige and not copie:
            # --- MODE A : RÉSOLUTION SIMPLE (Étudiant) ---
            print(f"{B}{C}🎯 MODE DÉTECTÉ : RÉSOLUTION D'ÉNONCÉ{R}")
            anim("AGENTS: Analyse visuelle de l'exercice")
            
            inputs = {
                "image_path": path_enonce, 
                "mode": "solve"
            }
            result = exam_agent.invoke(inputs)
            
            dt = round(time.time() - start_total, 2)
            print(f"{G}{B}✅ SOLUTION GÉNÉRÉE EN {dt}s{R}")
            
            return {
                "status": "success",
                "mode": "student_solve",
                "ocr_extracted": result.get("raw_text"),
                "solution": result.get("solution")
            }

        else:
            # --- MODE B : CORRECTION DE COPIE (Professeur) ---
            print(f"{B}{Y}🎓 MODE DÉTECTÉ : AUTO-GRADER (Correction){R}")
            
            # Sauvegarde des pièces jointes
            path_corrige = save_file(corrige) if corrige else None
            path_copie = save_file(copie) if copie else None
            
            if path_corrige: paths_to_clean.append(path_corrige)
            if path_copie: paths_to_clean.append(path_copie)

            # Gestion spécifique de la copie (Image ou PDF)
            copie_images = handle_pdf(path_copie, paths_to_clean) if path_copie else []

            anim(f"AGENTS: Comparaison multicritères ({len(copie_images)} pages)")
            
            inputs = {
                "enonce_path": path_enonce,
                "corrige_path": path_corrige,
                "copie_paths": copie_images,
                "mode": "grade"
            }
            result = exam_agent.invoke(inputs)
            
            dt = round(time.time() - start_total, 2)
            print(f"{G}{B}✅ RAPPORT DE CORRECTION GÉNÉRÉ EN {dt}s{R}")

            return {
                "status": "success",
                "mode": "professor_grade",
                "rapport": result.get("rapport_correction")
            }

    except Exception as e:
        print(f"{Y}❌ CRASH SYSTÈME: {str(e)}{R}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage automatique des fichiers temporaires
        for p in paths_to_clean:
            if p and os.path.exists(p):
                try: os.remove(p)
                except: pass

if __name__ == "__main__":
    print(f"{G}{B}--- NEXUS HYBRID ENGINE V3.0 ONLINE ---{R}")
    print(f"{C}En attente de requêtes sur http://127.0.0.1:8001{R}")
    uvicorn.run(app, host="127.0.0.1", port=8001)