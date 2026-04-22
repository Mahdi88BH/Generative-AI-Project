import os
import time
import sys
from mcp.server.fastmcp import FastMCP
from ocr_engine import extract_text_from_exam

# 1. Initialisation du serveur FastMCP
# On définit le nom du serveur qui apparaîtra dans les logs de l'agent
mcp = FastMCP("Nexus-Vision-Server")

@mcp.tool()
def read_document(file_path: str) -> str:
    """
    Outil de vision : Analyse un document (Image ou PDF) et extrait le texte.
    Utilisé par l'agent pour numériser les énoncés et les copies.
    """
    # --- LOGS VISUELS POUR LA DÉMO ---
    print(f"\n" + "🔔" * 20)
    print(f"🚀 [MCP CALL] Outil : read_document")
    print(f"📂 FICHIER : {os.path.basename(file_path)}")
    print("🔔" * 20)
    
    start_time = time.time()
    
    try:
        # Appel du moteur hybride défini dans ocr_engine.py
        text = extract_text_from_exam(file_path)
        
        duration = round(time.time() - start_time, 2)
        
        if not text or len(text.strip()) == 0:
            print(f"⚠️ [MCP] Document lu mais vide ({duration}s)")
            return "Le document est vide ou illisible."
            
        print(f"✅ [MCP] Extraction réussie : {len(text)} caractères")
        print(f"🕒 Temps : {duration}s")
        print("-" * 40)
        
        return text
        
    except Exception as e:
        print(f"❌ [MCP ERROR] : {str(e)}")
        return f"Erreur lors du traitement du document : {str(e)}"

if __name__ == "__main__":
    # --- CONFIGURATION DU SERVEUR ---
  
    print(" NEXUS MCP VISION CORE ")
    print(" Statut : EN ATTENTE ")
    print(" Transport : SSE (Network) ")
    print(" Port : 8010 ")
  

 
    sys.argv = ["mcp_server.py", "run", "--transport", "sse", "--port", "8010"]
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nArrêt du serveur MCP...")