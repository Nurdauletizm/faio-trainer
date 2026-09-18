"""Рецепт 7. Поиск похожих изображений — эмбеддинги предобученной модели.

Под задачу «Lost in the Museum» (FAIO-2025, 2-й тур): сдаются не ответы,
а векторы для всех 20 000 картинок; организаторы сами считают Hit@3.

Важно: обучать ничего не обязательно. Медиана 0.42 в 2025 году — это
примерно уровень «взял хорошую предобученную модель и нормировал векторы».
Поэтому сначала сдайте zero-shot вариант, а улучшайте потом.
"""
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import timm

IMG_DIR = Path("/kaggle/input/<competition>/dataset")
MODEL_NAME = "vit_base_patch14_dinov2.lvd142m"   # сильный универсальный энкодер
BATCH = 32
device = "cuda" if torch.cuda.is_available() else "cpu"

model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=0).eval().to(device)
config = timm.data.resolve_model_data_config(model)
transform = timm.data.create_transform(**config, is_training=False)


class Images(Dataset):
    def __init__(self, paths):
        self.paths = paths

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        img = Image.open(self.paths[i]).convert("RGB")
        return transform(img), self.paths[i].name


paths = sorted(IMG_DIR.glob("*"))
loader = DataLoader(Images(paths), batch_size=BATCH, num_workers=2, shuffle=False)

names, vectors = [], []
with torch.no_grad():
    for batch, batch_names in loader:
        batch = batch.to(device)
        feats = model(batch)
        # горизонтальное отражение почти бесплатно добавляет устойчивости
        feats = feats + model(torch.flip(batch, dims=[3]))
        feats = F.normalize(feats, dim=1)          # L2-нормировка обязательна
        vectors.append(feats.cpu().numpy().astype(np.float32))
        names.extend(batch_names)

emb = np.vstack(vectors)
print("эмбеддинги:", emb.shape)

sub = pd.DataFrame(emb, columns=[f"feature_{i}" for i in range(emb.shape[1])])
sub.insert(0, "image_name", names)
sub.insert(0, "ID", names)

assert len(sub) == len(paths), "должны быть строки для ВСЕХ картинок, без пропусков"
assert not sub["image_name"].duplicated().any(), "дубликаты имён файлов"
sub.to_csv("submission.csv", index=False)

# Как проверить себя без лидерборда:
#   сделайте себе мини-проверку — возьмите картинку, испортите её
#   (размытие, поворот, обрезка, затемнение) и посмотрите, попадает ли
#   оригинал в топ-3 по косинусной близости. Это и есть Hit@3 в миниатюре.
#
# Что улучшать дальше:
#   1) усреднить эмбеддинги двух разных моделей (DINOv2 + CLIP), каждую
#      отнормировать ДО усреднения, и нормировать результат;
#   2) многомасштабность: прогнать картинку в 224 и 336 пикселей, усреднить;
#   3) если остаётся время — дообучить с ArcFace на парах «оригинал - копия».
