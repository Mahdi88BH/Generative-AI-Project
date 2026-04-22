import os
from mcp.server.fastmcp import FastMCP
from ocr_engine import extract_text_from_exam


mcp = FastMCP(
    "Nexus-Vision-Server",
    dependencies=["pytesseract", "opencv-python", "pymupdf", "pdf2image", "pillow"]
)


@mcp.tool()
def read_document(file_path: str) -> str:
    """
    Analyse un document (Image ou PDF) et en extrait le contenu textuel.
    Supporte les documents numériques et les scans grâce à un moteur hybride.
    
    Args:
        file_path: Chemin absolu vers le fichier à analyser.
    """
    print(f"--- [MCP SERVER] Appel de l'outil Vision pour : {file_path} ---")
    
    try:
        # On appelle ta fonction existante dans ocr_engine.py
        text = extract_text_from_exam(file_path)
        
        if not text or len(text.strip()) == 0:
            return "⚠️ Le document a été lu mais aucun texte n'a pu être extrait."
            
        return text
        
    except Exception as e:
        return f"❌ Erreur critique lors de l'exécution du Tool Vision : {str(e)}"

# 3. Lancement du serveur
if __name__ == "__main__":
    # Le serveur peut tourner en mode Stdio (standard pour MCP)
    mcp.run()