import pytest
from PIL import Image
from src.preprocessing import preprocess_image_bgr
from src.ocr_engine import ocr_image_from_pil
from src.text_extraction import find_target_line_from_text
import cv2

def test_pipeline_on_sample():
    img_path = "tests/sample1.png"  # put one sample here for test
    img_bgr = cv2.imread(img_path)
    preproc, angle = preprocess_image_bgr(img_bgr)
    pil = Image.fromarray(preproc).convert("RGB")
    raw_text, _ = ocr_image_from_pil(pil)
    t = find_target_line_from_text(raw_text)
    assert t is not None


