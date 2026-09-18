"""Рецепт 2. Классификация текста — TF-IDF и логистическая регрессия.

Под задачу типа «Кто на каком языке говорит» (FAIO-2025, отбор, задача 4).
Это и есть авторское решение жюри: символьные n-граммы + логрег.

Ключевая деталь: analyzer="char_wb" — символьные n-граммы работают
для определения языка гораздо лучше, чем деление по словам.
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score

train = pd.read_csv("train.csv")   # колонки: text, label
test = pd.read_csv("test.csv")     # колонка: text

model = make_pipeline(
    TfidfVectorizer(
        analyzer="char_wb",     # символьные n-граммы внутри слов
        ngram_range=(1, 4),
        sublinear_tf=True,
        min_df=2,
        max_features=200_000,
    ),
    LogisticRegression(C=10, max_iter=1000, n_jobs=-1),
)

scores = cross_val_score(model, train["text"], train["label"], cv=5, scoring="accuracy")
print(f"CV accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")

model.fit(train["text"], train["label"])
pred = model.predict(test["text"])

sub = pd.DataFrame({"id": range(len(test)), "label": pred})
sub.to_csv("solution.csv", index=False)
print(sub.head())

# Что пробовать дальше:
#   1) ансамбль: логрег на char-n-граммах + LinearSVC + бустинг;
#   2) дообучить XLM-RoBERTa, если есть GPU и время;
#   3) посмотреть глазами на ошибки — в задаче 2025 года часть текстов была
#      смешанной (слова одного языка внутри другого), их полезно разметить.
