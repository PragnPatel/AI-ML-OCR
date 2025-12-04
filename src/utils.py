import json
import cv2
import numpy as np

def save_json(obj, fname):
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_image(path: str):
    """
    Loads an image in BGR format using OpenCV.
    """
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Image not found: {path}")
    return img


def to_gray(image):
    """
    Convert BGR to grayscale.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)



def resize_if_large(img, max_dim=1600):
    """
    Resizes image if width/height are too large.
    """
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return img

def rotate_if_needed(image):
    """
    Tries multiple rotations: 0°, 90°, 180°, 270°
    Returns image with maximum OCR text detected.
    """
    rotations = [
        ("0", image),
        ("90", cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)),
        ("180", cv2.rotate(image, cv2.ROTATE_180)),
        ("270", cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)),
    ]

    return [img for _, img in rotations]