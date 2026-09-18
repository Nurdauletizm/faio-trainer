"""Рецепт 4. Подсчёт объектов на изображении — контуры OpenCV.

Под задачу типа «Simple Objects» (FAIO-2025, отбор, задача 6):
на картинке 2048x2048 от 100 до 500 фигур, нужно назвать их количество.

Здесь модель не нужна вообще — нужна аккуратная обработка изображения.
Метрика в той задаче штрафует за относительную ошибку, поэтому важнее
не пропускать фигуры, чем идеально их классифицировать.
"""
import cv2
import numpy as np
import pandas as pd
from pathlib import Path

TEST_DIR = Path("/kaggle/input/<competition>/test")


def count_figures(path: Path) -> int:
    img = cv2.imread(str(path))
    if img is None:
        return 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # фон светлый, контуры фигур тёмные/цветные -> выделяем всё, что не фон
    bg = int(np.median(gray))
    mask = (np.abs(gray.astype(int) - bg) > 20).astype(np.uint8) * 255

    # замыкаем разрывы в тонких линиях, иначе один контур распадётся на части
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # RETR_EXTERNAL — только внешние границы: рамка фигуры считается один раз
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    count = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area < 40:            # мусор и шум
            continue
        x, y, w, h = cv2.boundingRect(c)
        if w < 5 or h < 5:
            continue
        count += 1
    return count


rows = []
for i, path in enumerate(sorted(TEST_DIR.glob("*.png"))):
    rows.append({"id": i, "count": count_figures(path)})

sub = pd.DataFrame(rows)
sub.to_csv("submit.csv", index=False)
print(sub.head(), sub.shape)

# Как отлаживать (это важнее подбора порогов вслепую):
#   1) возьмите картинки из train с известным ответом;
#   2) считайте среднюю относительную ошибку |предсказание - истина| / истина;
#   3) выведите 5 худших случаев и посмотрите на маску глазами —
#      обычно видно, что фигуры либо слиплись, либо распались.
