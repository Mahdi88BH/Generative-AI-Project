import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import pytesseract

# --- CONFIGURATION TESSERACT (TRÈS IMPORTANT SUR WINDOWS) ---
# Si Tesseract n'est pas dans les variables d'environnement de votre PC,
# décommentez la ligne ci-dessous et mettez le bon chemin :
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI(title="Nexus Vision - MCP Server")

class OCRRequest(BaseModel):
    arguments: dict

@app.post("/tools/vision_ocr_tool")
async def vision_ocr_tool(request: OCRRequest):
    # Récupération du chemin envoyé par agent.py
    image_path = request.arguments.get("image_path")
    
    if not image_path:
        raise HTTPException(status_code=400, detail="Le paramètre 'image_path' est manquant.")
        
    if not os.path.exists(image_path):
        print(f"❌ [MCP VISION] Erreur : Fichier introuvable -> {image_path}")
        return {"content": ""} # Retourne vide pour que l'agent signale l'erreur proprement
        
    file_name = os.path.basename(image_path)
    print(f"--- [MCP VISION] Extraction en cours : {file_name} ---")
    
    try:
        # 1. Ouverture de l'image
        img = Image.open(image_path)
        
        # 2. Extraction du texte (lang='fra+eng' pour le vocabulaire technique/mathématique)
        # Assurez-vous d'avoir téléchargé les données de langue pour Tesseract
        extracted_text = pytesseract.image_to_string(img, lang='fra+eng')
        
        # 3. Nettoyage de base pour éviter d'envoyer des chaînes vides illisibles
        cleaned_text = extracted_text.strip()
        
        if not cleaned_text:
            print(f"⚠️ [MCP VISION] Attention : Aucun texte détecté sur {file_name}")
            return {"content": "[OCR: L'image semble vide ou illisible]"}
            
        print(f"✔ [MCP VISION] Succès : {len(cleaned_text)} caractères extraits.")
        return {"content": cleaned_text}
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [MCP VISION] Crash sur {file_name} : {error_msg}")
        return {"content": f"[Erreur interne OCR : {error_msg}]"}

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" 👁️  NEXUS VISION CORE ONLINE (Tesseract OCR) ")
    print(" 📡 Port d'écoute : 8002")
    print("="*50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8002)