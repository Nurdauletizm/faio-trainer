"""Рецепт 1. Табличная классификация — градиентный бустинг.

Под задачу типа «Qaz-letters» (FAIO-2025, 1-й тур): даны готовые числовые
признаки, нужно предсказать класс. В 2025 году медиана по этой задаче была
0.98 — то есть почти все участники взяли её именно таким способом.

Нужен: pandas, scikit-learn (есть в Kaggle по умолчанию).
Если доступны lightgbm / catboost — берите их, обычно чуть точнее.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score

TRAIN = "/kaggle/input/<competition>/train.csv"
TEST = "/kaggle/input/<competition>/test.csv"
TARGET = "target"
ID = "id"

train = pd.read_csv(TRAIN)
test = pd.read_csv(TEST)

features = [c for c in train.columns if c not in (TARGET, ID)]
X, y = train[features].values, train[TARGET].values
X_test = test[features].values

# --- честная оценка качества до сабмита -----------------------------------
oof = np.zeros(len(train), dtype=object)
test_proba = None
folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for fold, (tr, va) in enumerate(folds.split(X, y), 1):
    model = HistGradientBoostingClassifier(
        max_iter=400,
        learning_rate=0.08,
        max_leaf_nodes=31,
        early_stopping=True,
        validation_fraction=0.1,
        random_state=42,
    )
    model.fit(X[tr], y[tr])
    oof[va] = model.predict(X[va])
    proba = model.predict_proba(X_test)
    test_proba = proba if test_proba is None else test_proba + proba
    print(f"fold {fold}: accuracy = {accuracy_score(y[va], oof[va]):.4f}")

print(f"OOF accuracy = {accuracy_score(y, oof):.4f}")

# --- сабмит ---------------------------------------------------------------
classes = model.classes_
pred = classes[np.argmax(test_proba, axis=1)]

sub = pd.DataFrame({ID: test[ID], TARGET: pred})
sub.to_csv("submission.csv", index=False)
print(sub.shape)
print(sub.head())

# Что пробовать дальше, по убыванию отдачи:
#   1) усреднить предсказания нескольких моделей (бустинг + случайный лес);
#   2) добавить простые производные признаки (отношения, суммы по группам);
#   3) подобрать learning_rate / max_leaf_nodes по OOF, а не по лидерборду.
