import cv2
import pytesseract
import os

# Configuration du chemin Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_exam(image_path):
    if not os.path.exists(image_path):
        return "Erreur : Image non trouvée sur le serveur."

    # 1. Chargement de l'image
    img = cv2.imread(image_path)
    if img is None:
        return "Erreur : Impossible de lire l'image (Format corrompu ?)."

    # 2. Prétraitement pour améliorer la précision
    # Redimensionnement si l'image est trop petite (améliore l'OCR sur les petits textes)
    height, width = img.shape[:2]
    if width < 1000:
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Passage en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Suppression du bruit (Flou Gaussien léger)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Seuillage adaptatif d'Otsu
    processed = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # 3. Extraction avec configuration spécifique
    # --psm 3 : Analyse automatique de la mise en page (Standard)
    # --oem 3 : Utilise le moteur LSTM (le plus précis)
    custom_config = r'--oem 3 --psm 3'
    
    try:
        # On tente le bilingue, si échec on replie sur l'anglais seul
        text = pytesseract.image_to_string(processed, lang='fra+eng', config=custom_config)
    except:
        text = pytesseract.image_to_string(processed, lang='eng', config=custom_config)
    
    return text.strip()