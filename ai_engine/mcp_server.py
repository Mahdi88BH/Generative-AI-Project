# mcp_server.py
from mcp.server.fastmcp import FastMCP
from ocr_engine import extract_text_from_exam # Ta fonction existante

mcp = FastMCP("Nexus-OCR")

@mcp.tool()
def read_document(file_path: str) -> str:

    return extract_text_from_exam(file_path)

if __name__ == "__main__":
    mcp.run()