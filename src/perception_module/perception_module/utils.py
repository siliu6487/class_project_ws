import pickle
import librosa
import numpy as np

import cv2
import matplotlib.pyplot as plt


# ====================== Audio =======================================
def load_model(model_path):
    with open(model_path, "rb") as f:
        return pickle.load(f)


def audio_feature_extractor(file_path, start_sec=1, end_sec=4):
    y, sr = librosa.load(file_path, sr=16000)

    # trim
    start = int(start_sec * sr)
    end = int(end_sec * sr)
    y = y[start:end]

    # normalize (VERY IMPORTANT)
    y = y / (np.max(np.abs(y)) + 1e-6)

    # ensure fixed length
    target_len = int((end_sec - start_sec) * sr)
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]

    # log-mel
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40)
    log_mel = librosa.power_to_db(mel)

    return np.mean(log_mel, axis=1)


def predict_audio(file_path, model):
    if model is None:
        model_path = "~/workspace/class_project_ws/src/perception_module/models/audio_model.pkl"
        model = load_model(model_path)

    feat = audio_feature_extractor(file_path)
    pred = model.predict([feat])[0]

    return "water" if pred == 1 else "empty"


# ======================Vision =======================================

LOWER_BLUE = np.array([100, 100, 50])
UPPER_BLUE = np.array([130, 255, 255])

LOWER_ORANGE = np.array([5, 100, 100])
UPPER_ORANGE = np.array([20, 255, 255])


def crop_cup_region(img):
    h, w = img.shape[:2]

    # define ROI (adjust these)
    x1, y1 = 150, 150
    x2, y2 = 250, 260

    # clamp to image bounds (VERY IMPORTANT)
    x1 = max(0, min(x1, w))
    x2 = max(0, min(x2, w))
    y1 = max(0, min(y1, h))
    y2 = max(0, min(y2, h))

    cropped = img[y1:y2, x1:x2]

    # debug check
    if cropped.size == 0:
        print("⚠️ Empty crop! Check ROI coordinates.")

    return cropped


def detect_pen(
    img,
    target_color="both",   # "blue", "orange", or "both"
    threshold=80,
    debug=False
):
    cropped = crop_cup_region(img)

    if cropped is None or cropped.size == 0:
        return False, 0

    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

    if target_color == "blue":
        mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    elif target_color == "orange":
        mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

    elif target_color == "both":
        mask_blue = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
        mask_orange = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)
        mask = mask_blue + mask_orange

    else:
        raise ValueError(
            f"Unknown color: {target_color}. "
            f"Use 'blue', 'orange', or 'both'."
        )

    kernel = np.ones((3,3), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.dilate(
        mask,
        kernel,
        iterations=1
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    areas = [
        cv2.contourArea(c)
        for c in contours
        if cv2.contourArea(c) > 10
    ]

    max_area = max(areas) if areas else 0

    pred = max_area > threshold

    if debug:
        vis = cropped.copy()
        cv2.drawContours(
            vis,
            contours,
            -1,
            (0,255,0),
            2
        )

        plt.figure(figsize=(10,3))

        plt.subplot(1,3,1)
        plt.imshow(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        plt.title("Cropped")
        plt.axis("off")

        plt.subplot(1,3,2)
        plt.imshow(mask, cmap="gray")
        plt.title(f"{target_color} mask")
        plt.axis("off")

        plt.subplot(1,3,3)
        plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
        plt.title(
            f"{target_color}\nArea: {max_area:.1f}"
        )
        plt.axis("off")

        plt.tight_layout()
        plt.show()

    return pred, max_area