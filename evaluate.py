import os
import json
from difflib import SequenceMatcher
import cv2
import numpy as np

from src.preprocessing import preprocess_image
from src.ocr_engine import run_ocr, run_ocr_with_confidence
from src.text_extraction import extract_target_line
from src.utils import load_image

SAMPLES_DIR = "samples"
RESULTS_DIR = "results"

os.makedirs(RESULTS_DIR, exist_ok=True)


def extract_expected_text(filename: str) -> str:
    """
    Expected text is derived from file name.
    Example:
        '163233702292313922_1_.jpg' → '163233702292313922_1_'
    """
    name, _ = os.path.splitext(filename)
    return name


def rotate_image(img, angle):
    """
    Rotates image without cropping content.
    """
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    # compute new bounding dimensions
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust rotation matrix to consider new translation
    M[0, 2] += (nW / 2) - center[0]
    M[1, 2] += (nH / 2) - center[1]

    return cv2.warpAffine(img, M, (nW, nH))


def best_rotation_ocr(image):
    """
    Try OCR at multiple angles: 0°, 90°, 180°, 270°.
    Choose the one with highest average confidence score.
    """

    angles = [0, 90, 180, 270]
    best_conf = -1
    best_text = ""
    best_angle = 0

    for angle in angles:
        rotated_img = rotate_image(image, angle)
        ocr_text, avg_conf = run_ocr_with_confidence(rotated_img)

        if avg_conf > best_conf:
            best_conf = avg_conf
            best_text = ocr_text
            best_angle = angle

    return best_text, best_angle, best_conf


def character_accuracy(gt: str, pred: str) -> float:
    if not gt:
        return 1.0 if not pred else 0.0
    return SequenceMatcher(None, gt, pred).ratio()


def evaluate():
    results = []
    total = 0
    correct = 0
    cumulative_char_acc = 0.0

    print("\n🔍 Starting evaluation on dataset...\n")

    for filename in os.listdir(SAMPLES_DIR):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        total += 1
        filepath = os.path.join(SAMPLES_DIR, filename)

        expected = extract_expected_text(filename)
        img = load_image(filepath)

        # 1. Preprocess image
        processed = preprocess_image(img)

        # 2. Run OCR with rotation search
        best_text, angle_used, confidence = best_rotation_ocr(processed)

        # 3. Extract target line
        extracted = extract_target_line(best_text)

        # 4. Accuracy calculations
        is_correct = (expected == extracted)
        char_acc = character_accuracy(expected, extracted)
        cumulative_char_acc += char_acc
        if is_correct:
            correct += 1

        results.append({
            "filename": filename,
            "expected": expected,
            "predicted": extracted,
            "exact_match": is_correct,
            "character_accuracy": char_acc,
            "rotation_used": angle_used,
            "ocr_avg_confidence": confidence
        })

        print(f"[{filename}] Rot={angle_used}° Conf={confidence:.2f}")
        print(f"   Expected : {expected}")
        print(f"   Predicted: {extracted}")
        print(f"   Exact Match: {is_correct}")
        print(f"   Char Accuracy: {char_acc:.2f}\n")

    # Final metrics
    exact_accuracy = correct / total if total else 0
    avg_char_accuracy = cumulative_char_acc / total if total else 0

    metrics = {
        "total_images": total,
        "correct_exact_matches": correct,
        "exact_match_accuracy": exact_accuracy,
        "average_character_accuracy": avg_char_accuracy
    }

    # Save results
    with open(os.path.join(RESULTS_DIR, "per_image_results.json"), "w") as f:
        json.dump(results, f, indent=4)

    with open(os.path.join(RESULTS_DIR, "evaluation_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)

    print("\n===============================")
    print("📊 Evaluation Complete")
    print("===============================")
    print(f"Exact Match Accuracy     : {exact_accuracy*100:.2f}%")
    print(f"Average Character Accuracy: {avg_char_accuracy*100:.2f}%")
    print("\nResults saved to /results folder.\n")


if __name__ == "__main__":
    evaluate()
