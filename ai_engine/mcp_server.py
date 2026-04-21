# ai_engine/mcp_server.py
from mcp.server.fastapi import FastapiServer
import uvicorn
import pytesseract
import os
import cv2  # Importé au début pour plus de clarté

# CONFIGURATION TESSERACT (Vérifie bien que le chemin est correct après ton formatage)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialisation du serveur d'outils Nexus
app = FastapiServer("Nexus-OCR-Engine")

@app.tool()
async def vision_ocr_tool(image_path: str) -> str:
    """
    Outil de Vision Avancée : Analyse une image d'examen ou une copie d'étudiant.
    Récupère le texte brut pour traitement par l'agent intelligent.
    Argument : image_path (chemin absolu vers le fichier image).
    """
    print(f"--- [MCP SERVER] Réception d'une demande d'analyse : {image_path} ---")
    
    # 1. Vérification de sécurité
    if not os.path.exists(image_path):
        return "Erreur : Le fichier image spécifié est introuvable sur le serveur."

    try:
        # 2. Chargement de l'image
        img = cv2.imread(image_path)
        if img is None:
            return "Erreur : Impossible de lire l'image. Le format est peut-être corrompu."

        # 3. Prétraitement intelligent (Améliore la précision de Llama 3 en amont)
        # Conversion en gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Binarisation d'Otsu pour séparer le texte du fond (mieux pour les photos mobiles)
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # 4. Extraction via Tesseract
        # On utilise fra+eng pour supporter les documents bilingues
        text = pytesseract.image_to_string(processed, lang='fra+eng', config='--psm 3')
        
        extracted_content = text.strip()
        
        if not extracted_content:
            return "Avertissement : L'image a été lue mais aucun texte n'a été détecté."
            
        return extracted_content

    except Exception as e:
        print(f"--- [MCP SERVER] Erreur Critique : {str(e)} ---")
        return f"Erreur lors du traitement OCR : {str(e)}"

if __name__ == "__main__":
    # Lancement sur le port 8002
    print("--- [MCP SERVER] Démarrage du service Nexus-OCR sur le port 8002 ---")
    uvicorn.run(app, host="127.0.0.1", port=8002)