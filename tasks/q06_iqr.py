"""q06 — поиск выбросов методом межквартильного размаха."""
from ._util import cmp_multiset, floats

ID = "q06"
TITLE = "Выбросы по правилу IQR"
TOPIC = "анализ данных"
LEVEL = 2
POINTS = 20
SOURCE = "FAIO-2024, финал, задача B"

STATEMENT = """
Стажёр Дархан должен был ездить на метеостанцию и измерять чистоту льда,
но часть значений он просто выдумал. Найдите подделки — выбросы в данных.

Метод межквартильного размаха (IQR):
  Q1 — 25-й процентиль, Q3 — 75-й процентиль, IQR = Q3 - Q1.
  Выбросом считается значение вне отрезка [Q1 - 1.5*IQR, Q3 + 1.5*IQR].

Процентили считайте методом линейной интерполяции: для доли p возьмите
индекс h = p * (N - 1) в отсортированном массиве и линейно интерполируйте
между соседними элементами (так работает numpy.percentile по умолчанию).

ВХОД
  Одна строка: N вещественных значений через пробел.

ВЫХОД
  Все значения-выбросы в одну строку через пробел. Порядок любой.

ПРИМЕР
  вход:   10 11 12 11 10 12 11 500 -400 10 11 12
  выход:  500 -400
"""

TEMPLATE = '''import sys

data = [float(x) for x in sys.stdin.read().split()]
s = sorted(data)


def percentile(sorted_values, p):
    h = p * (len(sorted_values) - 1)
    lo = int(h)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (h - lo) * (sorted_values[hi] - sorted_values[lo])


q1 = percentile(s, 0.25)
q3 = percentile(s, 0.75)
iqr = q3 - q1

outliers = [x for x in data if ...]

print(" ".join(str(x) for x in outliers))
'''


def _percentile(s, p):
    h = p * (len(s) - 1)
    lo = int(h)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (h - lo) * (s[hi] - s[lo])


def _outliers(data):
    s = sorted(data)
    q1, q3 = _percentile(s, 0.25), _percentile(s, 0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [x for x in data if x < lo or x > hi]


def gen(rng):
    n = rng.randint(200, 400)
    data = [round(rng.uniform(400, 1000), 3) for _ in range(n)]
    for _ in range(rng.randint(4, 14)):
        if rng.random() < 0.5:
            data.append(round(rng.uniform(-200, 50), 3))
        else:
            data.append(round(rng.uniform(1450, 1900), 3))
    rng.shuffle(data)
    return " ".join(map(str, data)) + "\n", {}


def solve(inp):
    return " ".join(str(x) for x in _outliers(floats(inp))) + "\n"


def check(inp, out, payload):
    return cmp_multiset(out, _outliers(floats(inp)), tol=1e-6)
