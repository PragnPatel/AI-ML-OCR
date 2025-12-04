import cv2
import numpy as np
from src.utils import to_gray, resize_if_large

def preprocess_image_bgr(img_bgr, target_max_dim=1600):
    """
    Input: BGR image (numpy array)
    Output: preprocessed grayscale image (numpy array) ready for OCR
    Steps:
      - convert to gray
      - resize (if small)
      - denoise (median)
      - adaptive threshold
      - morphological close
      - deskew
    """
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = img_gray.shape
    scale = target_max_dim / max(h, w) if max(h, w) < target_max_dim else 1.0
    if scale != 1.0:
        img_gray = cv2.resize(img_gray, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_CUBIC)

    img_blur = cv2.medianBlur(img_gray, 3)
    img_thr = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 25, 12)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    img_morph = cv2.morphologyEx(img_thr, cv2.MORPH_CLOSE, kernel, iterations=1)

    # deskew
    coords = np.column_stack(np.where(img_morph < 255))
    angle = 0.0
    if coords.shape[0] > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h2, w2) = img_morph.shape
        M = cv2.getRotationMatrix2D((w2//2, h2//2), angle, 1.0)
        img_morph = cv2.warpAffine(img_morph, M, (w2, h2), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return img_morph, angle


def preprocess_image(image):
    """
    Preprocess image for best OCR accuracy.
    Steps:
      - resize if large
      - grayscale
      - denoise
      - threshold
    """
    img = resize_if_large(image)

    gray = to_gray(img)

    # Denoising
    den = cv2.fastNlMeansDenoising(gray, h=20)

    # Adaptive Threshold (best for varying labels)
    th = cv2.adaptiveThreshold(
        den, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
    )

    return th


def preprocess_image(image):
    # Convert to gray
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, h=15)

    # Sharpen
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        sharp, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )

    return thresh

def auto_rotate(image):
    """
    Try 0, 90, 180, 270 degrees and select orientation with max text length.
    """
    from src.ocr_engine import OCREngine
    ocr = OCREngine()

    rotations = [0, 90, 180, 270]
    best_img = image
    best_score = 0

    for angle in rotations:
        # Rotate
        rot_img = rotate(image, angle)
        lines = ocr.run_ocr(rot_img)
        score = sum(len(line) for line in lines)

        if score > best_score:
            best_score = score
            best_img = rot_img

    return best_img


def rotate(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
    return cv2.warpAffine(img, M, (w, h))