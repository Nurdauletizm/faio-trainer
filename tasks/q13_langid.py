"""q13 — определение языка текста (мини-версия задачи FAIO-2025)."""
import math
from collections import defaultdict

ID = "q13"
TITLE = "Кто на каком языке говорит"
TOPIC = "машинное обучение"
LEVEL = 3
POINTS = 30
SOURCE = "FAIO-2025, отбор, задача 4"

STATEMENT = """
Чат-бот телеком-оператора получает сообщения на трёх языках: казахском (kaz),
русском (ru) и английском (eng). Нужно определить язык каждого сообщения.

Вам дана обучающая выборка с известными метками и тестовая выборка без них.
Внимание: примерно в каждом восьмом сообщении есть вкрапления слов из другого
языка — модель должна смотреть на текст целиком, а не на одно слово.

Подсказка: сильный и простой бейзлайн — наивный байесовский классификатор
на символьных n-граммах. Для каждого языка посчитайте, сколько раз встречается
каждая n-грамма, а дальше сравните логарифмы вероятностей. Внешние библиотеки
не нужны, хватает словарей.

ВХОД
  Первая строка: два числа n_train и n_test.
  Далее n_train строк: метка, символ табуляции, текст.
  Далее n_test строк: только текст.

ВЫХОД
  n_test строк: предсказанная метка (kaz, ru или eng) для каждого тестового
  текста, в том же порядке.

ОЦЕНКА
  Ответ принимается при доле правильных ответов не ниже 0.85.
"""

TEMPLATE = '''import sys
from collections import defaultdict

lines = sys.stdin.read().split("\\n")
n_train, n_test = (int(v) for v in lines[0].split())

train = []
for i in range(1, n_train + 1):
    label, text = lines[i].split("\\t")
    train.append((label, text))

test = [lines[1 + n_train + i] for i in range(n_test)]


def ngrams(text, n=3):
    text = " " + text.lower() + " "
    return [text[i:i + n] for i in range(len(text) - n + 1)]


# 1) посчитайте частоты n-грамм для каждого языка
# 2) для каждого тестового текста сложите log((count + 1) / (total + V))
# 3) выберите язык с наибольшей суммой

for text in test:
    print(best_label)
'''

_SYL = {
    "kaz": ["қа", "ған", "ері", "ңіз", "дық", "жа", "мен", "тұр", "әде", "ғыс",
            "ұлы", "өзі", "іст", "бол", "лар", "тын", "сын"],
    "ru": ["по", "что", "ени", "ость", "ый", "ова", "при", "ний", "сть", "ла",
           "ко", "ра", "де", "ств", "тель", "ние"],
    "eng": ["the", "ing", "tion", "and", "ou", "ea", "sh", "wh", "ly", "er",
            "st", "al", "ment", "pro", "con"],
}
_LABELS = ["kaz", "ru", "eng"]


def _word(rng, lang):
    return "".join(rng.choice(_SYL[lang]) for _ in range(rng.randint(2, 4)))


def _text(rng, lang):
    words = [_word(rng, lang) for _ in range(rng.randint(4, 10))]
    if rng.random() < 0.12:  # вкрапления чужого языка
        other = rng.choice([l for l in _LABELS if l != lang])
        for _ in range(rng.randint(1, 2)):
            words[rng.randrange(len(words))] = _word(rng, other)
    return " ".join(words)


def gen(rng):
    n_train, n_test = 300, 120
    lines = [f"{n_train} {n_test}"]
    for _ in range(n_train):
        lang = rng.choice(_LABELS)
        lines.append(f"{lang}\t{_text(rng, lang)}")
    answers = []
    for _ in range(n_test):
        lang = rng.choice(_LABELS)
        answers.append(lang)
        lines.append(_text(rng, lang))
    return "\n".join(lines) + "\n", {"answers": answers}


def _parse(inp):
    lines = inp.split("\n")
    n_train, n_test = (int(v) for v in lines[0].split())
    train = []
    for i in range(1, n_train + 1):
        label, text = lines[i].split("\t")
        train.append((label, text))
    test = [lines[1 + n_train + i] for i in range(n_test)]
    return train, test


def _ngrams(text, n=3):
    text = " " + text.lower() + " "
    return [text[i:i + n] for i in range(len(text) - n + 1)]


def solve(inp):
    train, test = _parse(inp)
    counts = {l: defaultdict(int) for l in _LABELS}
    totals = {l: 0 for l in _LABELS}
    vocab = set()
    for label, text in train:
        for g in _ngrams(text):
            counts[label][g] += 1
            totals[label] += 1
            vocab.add(g)
    v = len(vocab) + 1
    out = []
    for text in test:
        grams = _ngrams(text)
        best, best_score = None, None
        for label in _LABELS:
            score = 0.0
            for g in grams:
                score += math.log((counts[label][g] + 1) / (totals[label] + v))
            if best_score is None or score > best_score:
                best, best_score = label, score
        out.append(best)
    return "\n".join(out) + "\n"


def check(inp, out, payload):
    answers = payload["answers"]
    got = [line.strip() for line in (out or "").strip().split("\n") if line.strip()]
    if len(got) != len(answers):
        return False, f"ожидалось {len(answers)} строк, получено {len(got)}"
    bad = [g for g in got if g not in _LABELS]
    if bad:
        return False, f"недопустимая метка: {bad[0]!r} (нужны kaz, ru, eng)"
    acc = sum(g == a for g, a in zip(got, answers)) / len(answers)
    if acc >= 0.85:
        return True, f"точность {acc:.3f}"
    return False, f"точность {acc:.3f}, а нужно не меньше 0.850"
