# ai_engine/mcp_server.py
from mcp.server.fastapi import FastapiServer
import uvicorn
import pytesseract
import os

# CONFIGURATION TESSERACT (Après formatage)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastapiServer("Nexus-OCR-Engine")

@app.tool()
async def vision_ocr_tool(image_path: str) -> str:
    """
    Extrait le texte d'un document d'examen.
    """
    import cv2 # Import local pour éviter les lenteurs
    if not os.path.exists(image_path):
        return "Erreur : Fichier introuvable."
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)