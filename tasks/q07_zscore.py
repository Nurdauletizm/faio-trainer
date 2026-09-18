"""q07 — поиск выбросов по z-оценке."""
from ._util import cmp_multiset, floats

ID = "q07"
TITLE = "Выбросы по z-оценке"
TOPIC = "анализ данных"
LEVEL = 2
POINTS = 20
SOURCE = "FAIO-2024, финал, задача B (второй метод)"

STATEMENT = """
Тот же набор измерений, но другой метод поиска выбросов — z-оценка.

Для каждого значения x считается z = (x - mean) / sigma, где mean — среднее
всего набора, sigma — стандартное отклонение всего набора (делите сумму
квадратов отклонений на N, без поправки Бесселя).

Выбросом считается значение с |z| > 3.

ВХОД
  Одна строка: N вещественных значений через пробел.

ВЫХОД
  Все значения-выбросы в одну строку через пробел. Порядок любой.
"""

TEMPLATE = '''import sys
from math import sqrt

data = [float(x) for x in sys.stdin.read().split()]

mean = sum(data) / len(data)
sigma = sqrt(sum((x - mean) ** 2 for x in data) / len(data))

outliers = [x for x in data if ...]

print(" ".join(str(x) for x in outliers))
'''


def _outliers(data):
    mean = sum(data) / len(data)
    sigma = (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5
    return [x for x in data if abs(x - mean) > 3 * sigma]


def gen(rng):
    n = rng.randint(300, 500)
    center = rng.uniform(200, 800)
    spread = rng.uniform(50, 120)
    data = [round(center + rng.uniform(-spread, spread), 3) for _ in range(n)]
    for _ in range(rng.randint(3, 8)):
        sign = 1 if rng.random() < 0.5 else -1
        data.append(round(center + sign * spread * rng.uniform(12, 20), 3))
    rng.shuffle(data)
    return " ".join(map(str, data)) + "\n", {}


def solve(inp):
    return " ".join(str(x) for x in _outliers(floats(inp))) + "\n"


def check(inp, out, payload):
    return cmp_multiset(out, _outliers(floats(inp)), tol=1e-6)
