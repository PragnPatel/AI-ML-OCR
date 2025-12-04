from PIL import Image
import pytesseract
import easyocr
import numpy as np
import cv2


class OCREngine:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def load_image(self, path):
        img = cv2.imread(path)
        if img is None:
            raise ValueError("Could not load image")
        return img

    def run_ocr(self, image):
        """
        Returns full detected text lines, not characters.
        """
        results = self.reader.readtext(
            image,
            detail=1,    # keep boxes, text, confidence
            paragraph=True
        )

        lines = []
        for det in results:
            _, text, conf = det
            if len(text.strip()) > 0:
                lines.append(text)

        return lines


# def ocr_image_from_pil(pil_img, lang='eng', config='--psm 6'):
#     """
#     Returns:
#       - raw_text: full OCR text as string
#       - data: dict from pytesseract.image_to_data
#     """
#     raw_text = pytesseract.image_to_string(pil_img, lang=lang, config=config)
#     data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
#     # normalize confidences (float to int)
#     for i, c in enumerate(data.get('conf', [])):
#         try:
#             data['conf'][i] = int(float(c))
#         except:
#             data['conf'][i] = -1
#     return raw_text, data


# def run_ocr(image):
#     """
#     Simple OCR wrapper that returns plain text.
#     """
#     text = pytesseract.image_to_string(image)
#     return text


# def run_ocr_with_confidence(image):
#     """
#     OCR with output confidence (for rotation selection).
#     """
#     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#     data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

#     extracted_text = []
#     confidences = []

#     n = len(data["text"])
#     for i in range(n):
#         word = data["text"][i].strip()
#         conf = data["conf"][i]

#         if word:
#             extracted_text.append(word)

#         if conf != "-1":
#             confidences.append(float(conf))

#     text = " ".join(extracted_text)
#     avg_conf = sum(confidences) / len(confidences) if confidences else 0

#     return text, avg_conf

