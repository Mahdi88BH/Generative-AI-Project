import cv2
import pytesseract
import os
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

# Configuration du chemin Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_exam(file_path):
    """
    Détecte automatiquement le type de fichier (Image ou PDF) 
    et extrait le texte intégral.
    """
    if not os.path.exists(file_path):
        return "Erreur : Fichier non trouvé sur le serveur."

    ext = os.path.splitext(file_path)[1].lower()

    # --- CAS 1 : LE FICHIER EST UN PDF ---
    if ext == '.pdf':
        print(f"--- [MOTEUR OCR] Traitement PDF détecté ---")
        try:
            # Conversion PDF -> Liste d'images PIL (300 DPI pour la précision)
            # Note: poppler_path est nécessaire si Poppler n'est pas dans ton PATH Windows
            pages = convert_from_path(file_path, 300)
            
            full_text = ""
            for i, page in enumerate(pages):
                print(f"📄 Analyse de la page {i+1}/{len(pages)}...")
                # Conversion Image PIL -> Array NumPy (OpenCV)
                img_frame = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                
                # Extraction avec ta logique de nettoyage
                page_text = clean_and_extract(img_frame)
                full_text += f"\n--- CONTENU PAGE {i+1} ---\n{page_text}\n"
            
            return full_text.strip()
        except Exception as e:
            return f"Erreur lors de la lecture du PDF : {str(e)}"

    # --- CAS 2 : LE FICHIER EST UNE IMAGE ---
    else:
        img = cv2.imread(file_path)
        if img is None:
            return "Erreur : Format d'image non supporté ou corrompu."
        return clean_and_extract(img)

def clean_and_extract(img):
    """
    Logique de nettoyage super puissante pour maximiser la précision de Tesseract.
    """
    # 1. Mise à l'échelle (Upscaling) pour les petits textes
    height, width = img.shape[:2]
    if width < 1500:
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # 2. Prétraitement (Grayscale -> Noise Removal -> Threshold)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Correction de l'illumination (optionnel mais puissant pour les photos)
    # gray = cv2.detailEnhance(gray, sigma_s=10, sigma_r=0.15) 

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    processed = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # 3. OCR avec moteur LSTM
    custom_config = r'--oem 3 --psm 3'
    try:
        text = pytesseract.image_to_string(processed, lang='fra+eng', config=custom_config)
    except:
        text = pytesseract.image_to_string(processed, lang='eng', config=custom_config)
    
    return text.strip()