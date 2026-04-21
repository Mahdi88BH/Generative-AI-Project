import os
import cv2
import pytesseract
import uvicorn
from fastapi import FastAPI
from mcp.server import Server
from mcp.server.fastapi import FastApiServerTransport

# CONFIGURATION TESSERACT
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. Création du serveur MCP Core
mcp_server = Server("Nexus-OCR-Engine")

# 2. Définition de l'outil OCR
@mcp_server.list_tools()
async def handle_list_tools():
    """Liste les outils disponibles pour l'agent."""
    return [
        {
            "name": "vision_ocr_tool",
            "description": "Analyse une image d'examen et extrait le texte brut.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Chemin absolu de l'image"}
                },
                "required": ["image_path"]
            }
        }
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Exécute l'outil demandé par l'agent."""
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

        # Prétraitement
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Extraction
        text = pytesseract.image_to_string(processed, lang='fra+eng', config='--psm 3')
        return text.strip() or "Aucun texte détecté."

    except Exception as e:
        return f"Erreur OCR : {str(e)}"


app = FastAPI()
transport = FastApiServerTransport(mcp_server, app)


@app.post("/tools/vision_ocr_tool")
async def manual_route(payload: dict):
    """Route simplifiée pour ton agent.py actuel (httpx)"""
    args = payload.get("arguments", {})
    result = await handle_call_tool("vision_ocr_tool", args)
    return {"content": result}

if __name__ == "__main__":
    print("--- [MCP SERVER] Démarrage sur http://127.0.0.1:8002 ---")
    uvicorn.run(app, host="127.0.0.1", port=8002)