import os
import cv2
import pytesseract
import uvicorn
from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.server.sse import SseServerTransport

# CONFIGURATION TESSERACT
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. Création du serveur MCP Core
mcp_server = Server("Nexus-OCR-Engine")

# 2. Logique de l'outil OCR
@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name != "vision_ocr_tool":
        raise ValueError(f"Outil inconnu : {name}")

    image_path = arguments.get("image_path")
    print(f"--- [MCP SERVER] Traitement : {image_path} ---")

    if not os.path.exists(image_path):
        return "Erreur : Fichier introuvable."

    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Erreur : Image corrompue."

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        text = pytesseract.image_to_string(processed, lang='fra+eng', config='--psm 3')
        return text.strip() or "Aucun texte détecté."

    except Exception as e:
        return f"Erreur OCR : {str(e)}"

# 3. Initialisation FastAPI et Transport SSE
app = FastAPI()

# Correction ici : Le transport prend l'URL de base en premier argument
sse_transport = SseServerTransport("/messages")

@app.get("/sse")
async def sse_endpoint(request: Request):
    """Gère la connexion flux (stream) pour MCP."""
    async with sse_transport.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await mcp_server.run(read, write, mcp_server.create_initialization_options())

@app.post("/messages")
async def messages_endpoint(request: Request):
    """Gère les messages entrants du protocole."""
    await sse_transport.handle_post_message(request.scope, request.receive, request._send)

# --- ROUTE DE COMPATIBILITÉ DIRECTE (Pour ton agent.py avec httpx) ---
@app.post("/tools/vision_ocr_tool")
async def manual_ocr_call(payload: dict):
    args = payload.get("arguments", {})
    result = await handle_call_tool("vision_ocr_tool", args)
    return {"content": result}

if __name__ == "__main__":
    print("--- [MCP SERVER] Démarrage sur http://127.0.0.1:8002 ---")
    uvicorn.run(app, host="127.0.0.1", port=8002)