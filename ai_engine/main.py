import os
import shutil
import time
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from pdf2image import convert_from_path
from agent import exam_agent

app = FastAPI(title="Nexus AI - Professor Mode (Auto-Grader)")

# Couleurs Terminal
G, C, Y, R, B = "\033[92m", "\033[96m", "\033[93m", "\033[0m", "\033[1m"

TEMP_DIR = "temp_exams"
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin" # À AJUSTER SELON TON PC
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
    """Sauvegarde sécurisée et renvoie le chemin absolu."""
    fname = os.path.basename(upload_file.filename)
    path = os.path.abspath(os.path.join(TEMP_DIR, fname))
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return path

@app.post("/api/v1/grade")
async def grade_exam(
    enonce: UploadFile = File(...), 
    corrige: UploadFile = File(...), 
    copie: UploadFile = File(...)
):
    print(f"\n{B}{Y}⚡ PROTOCOLE DE CORRECTION AUTOMATISÉE ACTIVÉ{R}")
    start_total = time.time()
    paths_to_clean = []

    try:
        # 1. SAUVEGARDE DES FICHIERS DE RÉFÉRENCE
        path_enonce = save_file(enonce)
        path_corrige = save_file(corrige)
        path_copie = save_file(copie)
        paths_to_clean.extend([path_enonce, path_corrige, path_copie])

        # 2. GESTION DU MULTI-PAGES (SI PDF)
        copie_images = []
        if path_copie.lower().endswith(".pdf"):
            anim("PDF-ENGINE: Conversion des pages de la copie")
            pages = convert_from_path(path_copie, poppler_path=POPPLER_PATH)
            for i, page in enumerate(pages):
                p_path = os.path.join(TEMP_DIR, f"page_{i}.jpg")
                page.save(p_path, "JPEG")
                copie_images.append(p_path)
                paths_to_clean.append(p_path)
        else:
            copie_images = [path_copie]

        # 3. LANCEMENT DE LA BOUCLE AGENTIC
        # On passe les chemins à l'agent (il appellera le MCP autant de fois que nécessaire)
        anim(f"AGENTS: Analyse de {len(copie_images)} page(s) étudiant")
        
        inputs = {
            "enonce_path": path_enonce,
            "corrige_path": path_corrige,
            "copie_paths": copie_images  # Liste de chemins
        }
        
        result = exam_agent.invoke(inputs)
        
        dt = round(time.time() - start_total, 2)
        print(f"{G}{B}✅ RAPPORT GÉNÉRÉ EN {dt}s{R}")

        return {
            "status": "success",
            "rapport": result.get("rapport_correction"),
            "note_finale": result.get("note_finale")
        }

    except Exception as e:
        print(f"{Y}❌ ERREUR SYSTÈME: {str(e)}{R}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyage de tous les fichiers temporaires
        for p in paths_to_clean:
            if os.path.exists(p): os.remove(p)

if __name__ == "__main__":
    print(f"{G}{B}NEXUS GRADER CORE ONLINE - PORT 8001{R}")
    uvicorn.run(app, host="127.0.0.1", port=8001)