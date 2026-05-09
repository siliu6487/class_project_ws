import os
import numpy as np
import librosa
from sklearn.linear_model import LogisticRegression
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "audio")

def extract_feature(file_path):
    y, sr = librosa.load(file_path, sr=16000)

    # trim first 5 seconds
    y = y[int(5 * sr):]

    # ensure fixed length (e.g., 2 sec after trim)
    target_len = 2 * sr
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]

    # log-mel
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40)
    log_mel = librosa.power_to_db(mel)

    # mean over time
    feat = np.mean(log_mel, axis=1)

    return feat


def load_dataset():
    X, y = [], []

    for label, cls in [("water", 1), ("empty", 0)]:
        folder = os.path.join(DATA_DIR, label)

        for file in os.listdir(folder):
            if file.endswith(".wav"):
                path = os.path.join(folder, file)
                feat = extract_feature(path)

                X.append(feat)
                y.append(cls)

    return np.array(X), np.array(y)


def train():
    X, y = load_dataset()

    model = LogisticRegression()
    model.fit(X, y)

    with open("models/audio_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("✅ Audio model trained & saved")


if __name__ == "__main__":
    train()