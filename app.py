import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import cv2
import os
from src.preprocessing import preprocess_image_bgr
from src.ocr_engine import ocr_image_from_pil
from src.text_extraction import find_target_line_from_text
from src.utils import save_json

st.set_page_config(page_title="Waybill OCR - _1_ line extractor", layout="wide")

st.title("Waybill OCR — Extract line containing pattern `_1_`")

uploaded = st.file_uploader("Upload waybill image(s)", type=['png','jpg','jpeg'])
if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Uploaded image", use_column_width=True)

    if st.button("Run OCR"):
        # convert to BGR for OpenCV preprocessing
        img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        preproc, angle = preprocess_image_bgr(img_bgr)
        st.subheader("Preprocessed (deskewed & thresholded)")
        st.image(preproc, channels="GRAY", use_column_width=True)

        pil_pre = Image.fromarray(preproc).convert("RGB")
        raw_text, data = ocr_image_from_pil(pil_pre)
        st.subheader("Full OCR Text")
        st.text_area("OCR output", raw_text, height=200)

        target_line = find_target_line_from_text(raw_text)
        st.subheader("Extracted target line")
        st.write(target_line)

        # annotate visually: highlight boxes with '1' or '_' tokens
        draw = ImageDraw.Draw(pil_pre)
        n = len(data.get('level', []))
        for i in range(n):
            txt = data['text'][i].strip()
            conf = data['conf'][i]
            if not txt: continue
            if '1' in txt or '_' in txt:
                left, top, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                draw.rectangle([left, top, left+w, top+h], outline=(255,0,0), width=3)
        st.image(pil_pre, use_column_width=True)

        # save result JSON
        out_name = f"ocr_result_{os.path.splitext(uploaded.name)[0]}.json"
        result = {"target_line": target_line, "raw_text": raw_text}
        save_json(result, out_name)
        st.success(f"Saved JSON result to `{out_name}`")
