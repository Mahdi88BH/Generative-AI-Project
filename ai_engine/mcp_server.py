import os
import cv2
import pytesseract
import uvicorn
from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.server.sse import SseServerTransport

# CONFIGURATION TESSERACT
# Assure-toi que ce chemin est correct après ton formatage
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. Création du serveur MCP
mcp_server = Server("Nexus-Vision-Engine")

# 2. L'outil de vision (OCR)
@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name != "vision_ocr_tool":
        raise ValueError(f"Outil inconnu : {name}")

    image_path = arguments.get("image_path")
    
    # Log de suivi pour la démo
    print(f"--- [MCP VISION] Traitement en cours : {os.path.basename(image_path)} ---")

    if not os.path.exists(image_path):
        return "Erreur : Fichier introuvable sur le disque."

    try:
        # Lecture de l'image
        img = cv2.imread(image_path)
        if img is None:
            return "Erreur : Impossible de lire l'image (format corrompu)."

        # --- PIPELINE DE PRÉ-TRAITEMENT (Optimisé pour l'OCR) ---
        # 1. Conversion en niveaux de gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Réduction du bruit (Denoising)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # 3. Binarisation adaptative (Seuillage pour texte noir sur blanc)
        processed = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # 4. Extraction Tesseract
        # Langues : français + anglais / PSM 3 : Analyse automatique complète
        text = pytesseract.image_to_string(processed, lang='fra+eng', config='--psm 3')
        
        result = text.strip()
        return result if result else "Aucun texte détecté sur cette page."

    except Exception as e:
        print(f"❌ Erreur Vision : {str(e)}")
        return f"Erreur OCR interne : {str(e)}"

# 3. Transport et API FastAPI
app = FastAPI()
sse_transport = SseServerTransport("/messages")

@app.get("/sse")
async def sse_endpoint(request: Request):
    async with sse_transport.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await mcp_server.run(read, write, mcp_server.create_initialization_options())

@app.post("/messages")
async def messages_endpoint(request: Request):
    await sse_transport.handle_post_message(request.scope, request.receive, request._send)

# --- ROUTE DE COMPATIBILITÉ DIRECTE ---
@app.post("/tools/vision_ocr_tool")
async def manual_ocr_call(payload: dict):
    args = payload.get("arguments", {})
    result = await handle_call_tool("vision_ocr_tool", args)
    return {"content": result}

if __name__ == "__main__":
    print("--- [MCP SERVER] VISION CORE ONLINE (Port 8002) ---")
    uvicorn.run(app, host="127.0.0.1", port=8002)