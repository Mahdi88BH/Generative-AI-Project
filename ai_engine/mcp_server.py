import os
import time
from mcp.server.fastmcp import FastMCP
import uvicorn


mcp = FastMCP("Nexus-Vision-Server")


from ocr_engine import extract_text_from_exam

@mcp.tool()
def read_document(file_path: str) -> str:
    """Analyse un document et extrait le texte."""
    print(f"\n[MCP] 📂 Traitement du fichier : {file_path}")
    try:
        text = extract_text_from_exam(file_path)
        print(f"[MCP] ✅ Extraction terminée ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"[MCP] ❌ Erreur : {e}")
        return str(e)

if __name__ == "__main__":
   
    from mcp.server.fastmcp.server import FastMCPServer
    
    print("\n" + "⚡" * 15)
    print(" NEXUS MCP CORE : ONLINE ")
    print(" Mode : SSE / Network ")
    print(" Port : 8010 ")
    print("⚡" * 15 + "\n")

  
    mcp.run(transport="sse", host="127.0.0.1", port=8010)