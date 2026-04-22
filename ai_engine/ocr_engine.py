import cv2
import pytesseract
import os
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
from pdf2image import convert_from_path

# Configuration du chemin Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_exam(file_path):
    if not os.path.exists(file_path):
        return "Erreur : Fichier non trouvé."

    ext = os.path.splitext(file_path)[1].lower()

    # --- CAS 1 : LE FICHIER EST UN PDF ---
    if ext == '.pdf':
        print(f"--- [MOTEUR HYBRIDE] Analyse PDF détectée ---")
        full_text = ""
        
        try:
            # 1. TENTATIVE D'EXTRACTION DIRECTE (TEXTE NUMÉRIQUE)
            doc = fitz.open(file_path)
            temp_text = ""
            for page in doc:
                temp_text += page.get_text()
            
            # Si on a extrait suffisamment de texte, on valide cette méthode
            if len(temp_text.strip()) > 50:
                print("✅ Texte numérique détecté (Extraction directe réussie).")
                return temp_text.strip()
            
            # 2. SECOURS OCR (SI LE PDF EST UN SCAN/IMAGE)
            print("⚠️ PDF scanné détecté (Passage au mode Vision/OCR)...")
            pages = convert_from_path(file_path, 300)
            for i, page in enumerate(pages):
                img_frame = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                page_text = clean_and_extract(img_frame)
                full_text += f"\n--- PAGE {i+1} ---\n{page_text}\n"
            
            return full_text.strip()

        except Exception as e:
            return f"Erreur lors de la lecture du PDF : {str(e)}"

    # --- CAS 2 : LE FICHIER EST UNE IMAGE ---
    else:
        img = cv2.imread(file_path)
        if img is None:
            return "Erreur : Format d'image non supporté."
        return clean_and_extract(img)

def clean_and_extract(img):
    """Logique de nettoyage OpenCV + Tesseract"""
    # Upscaling pour la précision
    height, width = img.shape[:2]
    if width < 1500:
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    processed = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    custom_config = r'--oem 3 --psm 3'
    try:
        text = pytesseract.image_to_string(processed, lang='fra+eng', config=custom_config)
    except:
        text = pytesseract.image_to_string(processed, lang='eng', config=custom_config)
    
    return text.strip()