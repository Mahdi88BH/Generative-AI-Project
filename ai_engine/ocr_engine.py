import cv2
import pytesseract
import os

# Configuration du chemin Tesseract (indispensable après formatage)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_exam(image_path):
    """
    Extrait le texte d'une image avec prétraitement OpenCV pour maximiser la précision.
    """
    # 1. Vérification de l'existence du fichier
    if not os.path.exists(image_path):
        print(f"❌ Erreur : Fichier introuvable -> {image_path}")
        return "Erreur : Image non trouvée sur le serveur."

    # 2. Lecture de l'image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Erreur : Impossible de charger l'image (format invalide ou corrompu).")
        return "Erreur : Lecture de l'image impossible."

    # 3. Prétraitement pour l'OCR
    # Conversion en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Réduction du bruit (Flou gaussien léger pour nettoyer les grains de la photo)
    denoised = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Binarisation d'Otsu (rend le texte noir sur fond blanc pur)
    processed = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # 4. Extraction du texte
    # lang='fra+eng' pour gérer les examens bilingues
    # --psm 3 : Mode de segmentation automatique (idéal pour les documents structurés)
    try:
        text = pytesseract.image_to_string(
            processed, 
            lang='fra+eng', 
            config='--psm 3 --oem 3'
        )
        
        # Nettoyage des espaces inutiles
        final_text = text.strip()
        
        if not final_text:
            return "Avertissement : Aucun texte détecté sur l'image."
            
        return final_text

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de Tesseract : {str(e)}")
        return f"Erreur OCR : {str(e)}"

# Bloc de test rapide (optionnel)
if __name__ == "__main__":
    test_path = "test_image.png"
    if os.path.exists(test_path):
        print("Résultat du test OCR :")
        print(extract_text_from_exam(test_path))