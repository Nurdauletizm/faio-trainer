"""Рецепт 3. Классификация временных рядов с датчиков (IMU).

Под задачу типа «AI Yoga Instructor» (FAIO-2025, отбор, задача 5):
6 каналов (ax, ay, az, wx, wy, wz), 200 Гц, нужно сказать «верно / неверно».

Главная идея: НЕ кормить сырой ряд в модель. Свернуть каждый ряд в вектор
статистик по каналам и отдать бустингу. Это быстро и почти всегда сильнее
наивной нейросети на маленьких данных.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score

CHANNELS = ["ax", "ay", "az", "wx", "wy", "wz"]


def features_for_segment(seg: pd.DataFrame) -> dict:
    """Один сегмент (одно повторение) -> словарь признаков."""
    out = {}
    for ch in CHANNELS:
        v = seg[ch].to_numpy(dtype=float)
        if len(v) == 0:
            v = np.zeros(1)
        out[f"{ch}_mean"] = v.mean()
        out[f"{ch}_std"] = v.std()
        out[f"{ch}_min"] = v.min()
        out[f"{ch}_max"] = v.max()
        out[f"{ch}_range"] = v.max() - v.min()
        out[f"{ch}_energy"] = float(np.mean(v ** 2))
        out[f"{ch}_absmean"] = float(np.mean(np.abs(v)))
        out[f"{ch}_q25"] = float(np.percentile(v, 25))
        out[f"{ch}_q75"] = float(np.percentile(v, 75))
        # число пересечений среднего — грубая мера «дёрганности» движения
        centered = v - v.mean()
        out[f"{ch}_zcr"] = float(np.mean(np.diff(np.signbit(centered)) != 0)) if len(v) > 1 else 0.0
        # спектр: где сосредоточена энергия движения
        spec = np.abs(np.fft.rfft(centered))
        if spec.size > 1:
            out[f"{ch}_peakfreq"] = float(np.argmax(spec[1:]) + 1)
            out[f"{ch}_spec_centroid"] = float((spec * np.arange(spec.size)).sum() / (spec.sum() + 1e-9))
        else:
            out[f"{ch}_peakfreq"] = 0.0
            out[f"{ch}_spec_centroid"] = 0.0
    # связь каналов: модуль ускорения и угловой скорости
    acc = seg[["ax", "ay", "az"]].to_numpy(dtype=float)
    gyr = seg[["wx", "wy", "wz"]].to_numpy(dtype=float)
    out["acc_mag_mean"] = float(np.linalg.norm(acc, axis=1).mean())
    out["gyr_mag_mean"] = float(np.linalg.norm(gyr, axis=1).mean())
    out["n_samples"] = len(seg)
    return out


def build(df: pd.DataFrame) -> pd.DataFrame:
    rows, ids = [], []
    for seg_id, seg in df.groupby("id", sort=True):
        rows.append(features_for_segment(seg))
        ids.append(seg_id)
    out = pd.DataFrame(rows)
    out.insert(0, "id", ids)
    return out


X_train_raw = pd.read_csv("X_train.csv")
y_train = pd.read_csv("y_train.csv")
X_test_raw = pd.read_csv("X_test.csv")

train_feats = build(X_train_raw).merge(y_train, on="id")
test_feats = build(X_test_raw)

cols = [c for c in train_feats.columns if c not in ("id", "label")]
model = HistGradientBoostingClassifier(max_iter=500, learning_rate=0.06, random_state=42)

cv = cross_val_score(model, train_feats[cols], train_feats["label"], cv=5, scoring="accuracy")
print(f"CV accuracy: {cv.mean():.4f}")

model.fit(train_feats[cols], train_feats["label"])
pred = model.predict(test_feats[cols])

pd.DataFrame({"id": test_feats["id"], "label": pred}).to_csv("solution.csv", index=False)
