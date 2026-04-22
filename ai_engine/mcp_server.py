import os
import time
from mcp.server.fastmcp import FastMCP
from ocr_engine import extract_text_from_exam

# Initialisation
mcp = FastMCP(
    "Nexus-Vision-Server",
    dependencies=["pytesseract", "opencv-python", "pymupdf", "pdf2image", "pillow"]
)

@mcp.tool()
def read_document(file_path: str) -> str:
    """
    Analyse un document et extrait le texte via le protocole MCP.
    """
    # --- INDICE VISUEL : DÉBUT D'APPEL ---
    print("\n" + "🔔" * 20)
    print(f"🚀 [MCP PROTOCOL] TOOL CALL: read_document")
    print(f"📂 SOURCE: {file_path}")
    print("🔔" * 20)
    
    start_time = time.time()
    
    try:
        # Exécution de l'OCR
        print("⚙️  Exécution du moteur hybride (OCR/Direct)...")
        text = extract_text_from_exam(file_path)
        
        # Calcul du temps pour le log
        duration = round(time.time() - start_time, 2)
        
        if not text or len(text.strip()) == 0:
            print(f"⚠️  FIN D'APPEL : Document vide ({duration}s)")
            return "⚠️ Le document a été lu mais aucun texte n'a pu être extrait."
            
        # --- INDICE VISUEL : RÉUSSITE ---
        print(f"✅  EXTRACTION RÉUSSIE : {len(text)} caractères trouvés")
        print(f"🕒  TEMPS DE TRAITEMENT : {duration} secondes")
        print("🌐 [MCP PROTOCOL] Transmission des données vers l'agent...")
        print("="*40 + "\n")
        
        return text
        
    except Exception as e:
        print(f"❌ [MCP ERROR] : {str(e)}")
        return f"❌ Erreur critique lors de l'exécution du Tool Vision : {str(e)}"

if __name__ == "__main__":
  
    print(" NEXUS MCP SERVER : MODE RÉSEAU ACTIVÉ ")
    print(" Protocole : SSE (HTTP) ")
    print(" Port : 8010 ")
 
  
    mcp.run(transport="sse", port=8010)