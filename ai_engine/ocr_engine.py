import httpx
import os

def extract_text_from_exam(image_path: str) -> str:
    """
    Interface unifiée pour extraire le texte d'une image.
    Cette fonction agit comme un client pour le serveur MCP Vision (Port 8002).
    """
    if not image_path or not os.path.exists(image_path):
        return "Erreur : Chemin d'image invalide ou introuvable."

    url_mcp = "http://127.0.0.1:8002/tools/vision_ocr_tool"
    
    try:
        # Appel au microservice de vision (MCP)
        with httpx.Client() as client:
            response = client.post(
                url_mcp,
                json={"arguments": {"image_path": os.path.abspath(image_path)}},
                timeout=45.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "Aucun texte renvoyé par le moteur de vision.")
            else:
                return f"Erreur MCP (Status {response.status_code}): {response.text}"
                
    except Exception as e:
        return f"Échec de connexion au serveur de vision : {str(e)}"

# --- TEST ISOLÉ (Optionnel) ---
if __name__ == "__main__":
    # Permet de tester l'OCR rapidement sans lancer tout le système
    test_img = "test.jpg"
    if os.path.exists(test_img):
        print(f"Test OCR sur {test_img}...")
        print("-" * 30)
        print(extract_text_from_exam(test_img))
    else:
        print("Placez un fichier 'test.jpg' pour tester cette brique isolément.")