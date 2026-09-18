"""Рецепт 6. Рекомендации: 50 треков на пользователя.

Под задачу «HearMe» (FAIO-2025, 2-й тур). Метрика считает, какую долю
трека пользователь реально дослушал, поэтому важны не «угаданные id»,
а треки, которые человек действительно будет слушать целиком.

Стратегия по возрастанию сложности (начните с первой и сдайте её):
  1. топ популярных треков всем одинаково -> уже ненулевой результат;
  2. + личная история пользователя (он переслушивает любимое);
  3. + item-item похожесть по совместному прослушиванию.
"""
import numpy as np
import pandas as pd
from collections import defaultdict

TOP_K = 50

inter = pd.read_csv("interactions.csv")
items = pd.read_csv("item_metadata.csv")
test_users = pd.read_csv("test.csv")["user_id"].unique()

# --- доля прослушивания вместо сырых секунд --------------------------------
inter = inter.merge(items[["item_id", "track_duration"]], on="item_id", how="left")
inter["fraction"] = (inter["listened_duration"] / inter["track_duration"]).clip(0, 1).fillna(0)

# свежие взаимодействия важнее старых
inter["listened_datetime"] = pd.to_datetime(inter["listened_datetime"], errors="coerce")
last_day = inter["listened_datetime"].max()
age_days = (last_day - inter["listened_datetime"]).dt.days.fillna(999)
inter["weight"] = inter["fraction"] * np.exp(-age_days / 60.0)

# --- 1. глобальная популярность --------------------------------------------
popular = (inter.groupby("item_id")["weight"].sum()
           .sort_values(ascending=False).index.to_list())

# --- 2. личная история ------------------------------------------------------
user_hist = inter.groupby(["user_id", "item_id"])["weight"].sum()

# --- 3. похожесть треков по совместному прослушиванию ------------------------
# для скорости берём только активных пользователей и их топ-треки
top_items = set(popular[:3000])
sub = inter[inter["item_id"].isin(top_items)]
by_user = sub.groupby("user_id")["item_id"].apply(lambda s: list(dict.fromkeys(s))[:40])

co = defaultdict(lambda: defaultdict(float))
for lst in by_user:
    for i, a in enumerate(lst):
        for b in lst[i + 1:]:
            co[a][b] += 1.0
            co[b][a] += 1.0

rows = []
for user in test_users:
    scores = defaultdict(float)

    # личная история: самое сильное сигнал
    hist = user_hist.loc[user] if user in user_hist.index.get_level_values(0) else None
    seeds = []
    if hist is not None:
        hist = hist.sort_values(ascending=False)
        seeds = list(hist.index[:20])
        for item_id, w in hist.items():
            scores[item_id] += 3.0 * w

    # соседи по совместному прослушиванию
    for seed in seeds:
        for neighbour, c in sorted(co[seed].items(), key=lambda kv: -kv[1])[:50]:
            scores[neighbour] += 0.5 * c / (1 + len(co[seed]))

    # добиваем популярным, чтобы всегда было ровно 50
    for rank, item_id in enumerate(popular[:200]):
        scores[item_id] += 0.01 * (200 - rank) / 200

    best = sorted(scores.items(), key=lambda kv: -kv[1])[:TOP_K]
    for rank, (item_id, _) in enumerate(best, 1):
        rows.append({"user_id": user, "item_id": item_id, "rank": rank})

recos = pd.DataFrame(rows)

# --- контроль формата ДО отправки ------------------------------------------
sizes = recos.groupby("user_id").size()
assert (sizes == TOP_K).all(), f"не у всех ровно {TOP_K} рекомендаций: {sizes[sizes != TOP_K]}"
assert not recos.duplicated(["user_id", "item_id"]).any(), "есть повторы трека у пользователя"
assert set(recos["user_id"]) == set(test_users), "список пользователей не совпадает с test.csv"

recos.insert(0, "id", range(len(recos)))
recos.to_csv("submission.csv", index=False)
print(recos.head(), recos.shape)
