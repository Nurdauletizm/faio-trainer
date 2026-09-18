"""Рецепт 5. Определение высоты ноты по звуку.

Под задачу «Missing Fundamental Puzzle» (FAIO-2025, 1-й тур): из записи
вырезана основная частота, но гармоники остались, и расстояние между
ними как раз равно основной частоте. Медиана в 2025-м была 0.49 —
задача берётся, если правильно смотреть на спектр.

Два пути, оба рабочих:
  A. Признаки из спектра + бустинг (быстро, без GPU) — реализовано ниже.
  B. Мел-спектрограмма или CQT + небольшая CNN (точнее, нужен GPU).
"""
import numpy as np
import pandas as pd
import librosa
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score

SR = 22050


def harmonic_product_spectrum(spec: np.ndarray, harmonics: int = 5) -> np.ndarray:
    """Перемножаем спектр с его прореженными копиями.

    Пик остаётся там, где стоит основная частота — ДАЖЕ если её саму
    вырезали, потому что гармоники стоят на её кратных.
    """
    hps = spec.copy()
    for h in range(2, harmonics + 1):
        decimated = spec[::h]
        hps[: len(decimated)] *= decimated
    return hps


def features(path: str) -> np.ndarray:
    y, sr = librosa.load(path, sr=SR, mono=True)
    y = librosa.util.normalize(y)

    # усреднённый спектр по всей записи
    S = np.abs(librosa.stft(y, n_fft=8192, hop_length=1024))
    spec = S.mean(axis=1)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=8192)

    hps = harmonic_product_spectrum(spec)
    f0_hps = freqs[int(np.argmax(hps[: len(hps) // 2]))]

    # автокорреляция спектра: тоже показывает шаг между гармониками
    centered = spec - spec.mean()
    ac = np.correlate(centered, centered, mode="full")[len(centered) - 1:]
    step = int(np.argmax(ac[5:]) + 5)
    f0_ac = step * (freqs[1] - freqs[0])

    # частоты самых сильных пиков — модель сама найдёт закономерность
    top = np.argsort(spec)[-8:][::-1]
    top_freqs = np.sort(freqs[top])

    chroma = librosa.feature.chroma_stft(S=S, sr=sr).mean(axis=1)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20).mean(axis=1)

    return np.concatenate([
        [f0_hps, f0_ac,
         librosa.hz_to_midi(max(f0_hps, 1e-3)),
         librosa.hz_to_midi(max(f0_ac, 1e-3)),
         float(librosa.feature.spectral_centroid(S=S, sr=sr).mean())],
        top_freqs,
        chroma,
        mfcc,
    ])


train = pd.read_csv("train.csv")   # колонки: Path, Pitch_ID
test = pd.read_csv("test.csv")     # колонка: Path

X = np.vstack([features(p) for p in train["Path"]])
y = train["Pitch_ID"].to_numpy()
X_test = np.vstack([features(p) for p in test["Path"]])

model = HistGradientBoostingClassifier(max_iter=600, learning_rate=0.08, random_state=42)
print("CV accuracy:", cross_val_score(model, X, y, cv=4, scoring="accuracy").mean())

model.fit(X, y)
pred = model.predict(X_test)

pd.DataFrame({"Path": test["Path"], "Pitch_ID": pred}).to_csv("submission.csv", index=False)

# Проверка себя без лидерборда: если признак f0_hps хороший, то
# librosa.hz_to_midi(f0_hps) почти совпадает с номером ноты на обучающей
# выборке. Постройте гистограмму разницы — сразу видно, работает ли идея.
