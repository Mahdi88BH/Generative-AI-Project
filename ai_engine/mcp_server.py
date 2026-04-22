import os
import time
from mcp.server.fastmcp import FastMCP
from ocr_engine import extract_text_from_exam


mcp = FastMCP("Nexus-Vision-Server")

@mcp.tool()
def read_document(file_path: str) -> str:
    """Analyse un document et extrait le texte via le protocole MCP."""
    print(f"\n🚀 [MCP CALL] Analyse de : {file_path}")
    start_time = time.time()
    
    try:
        text = extract_text_from_exam(file_path)
        duration = round(time.time() - start_time, 2)
        print(f"✅ Extraction réussie en {duration}s ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return f"Erreur OCR : {str(e)}"

if __name__ == "__main__":
   
    print("\n" + "⚡" * 15)
    print(" NEXUS MCP SERVER : READY ")
    print(" Port : 8010 | Transport : SSE ")
    print("⚡" * 15 + "\n")

    
    import sys
    sys.argv = ["mcp_server.py", "run", "--transport", "sse", "--port", "8010"]
    mcp.run()