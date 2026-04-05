import cv2
import pytesseract
import os


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_exam(image_path):
   
    if not os.path.exists(image_path):
        return "Erreur : Image non trouvée sur le serveur."

    
    img = cv2.imread(image_path)
    
   
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
   
    
    processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    
    
    text = pytesseract.image_to_string(processed, lang='fra+eng', config='--psm 3')
    
    return text.strip()