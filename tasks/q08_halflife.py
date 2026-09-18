"""q08 — период полураспада через линейную регрессию."""
from math import log
from ._util import cmp_numbers

ID = "q08"
TITLE = "Период полураспада"
TOPIC = "анализ данных"
LEVEL = 3
POINTS = 30
SOURCE = "FAIO-2024, финал, задача C"

STATEMENT = """
Радиоактивное вещество теряет половину массы каждые T0 секунд:

    m(t) = m0 * (1/2) ** (t / T0)

Даны n пар измерений (m, t) с небольшим шумом. Восстановите T0.

Подсказка: прологарифмируйте обе части. ln m = ln m0 - (ln 2 / T0) * t —
это прямая по t. Найдите её наклон методом наименьших квадратов
(формула: a = (n*Σxy - Σx*Σy) / (n*Σx^2 - (Σx)^2)) и выразите T0.

ВХОД
  Первая строка: n (число измерений).
  Далее n строк: два числа m и t.

ВЫХОД
  Одно число T0. Ответ принимается при относительной погрешности не более 1%.

ПРИМЕР
  вход:   5 / 1000 0 / 500 10 / 250 20 / 125 30 / 62.5 40
  выход:  10.0
"""

TEMPLATE = '''import sys
from math import log

data = sys.stdin.read().split()
n = int(data[0])
pairs = [(float(data[1 + 2 * i]), float(data[2 + 2 * i])) for i in range(n)]

# ln(m) = ln(m0) - (ln2 / T0) * t  ->  наклон прямой a = -ln2 / T0

print(T0)
'''


def gen(rng):
    m0 = rng.uniform(200, 8000)
    t0 = rng.uniform(5, 500)
    n = rng.randint(30, 200)
    t_max = min(5000, t0 * (log(m0) / log(2)) * 0.9)
    rows = []
    for _ in range(n):
        t = rng.uniform(0, t_max)
        m = m0 * 0.5 ** (t / t0) * rng.uniform(0.995, 1.005)
        rows.append(f"{m:.6f} {t:.6f}")
    return f"{n}\n" + "\n".join(rows) + "\n", {"t0": t0}


def _fit(inp):
    data = inp.split()
    n = int(data[0])
    xs, ys = [], []
    for i in range(n):
        m = float(data[1 + 2 * i])
        t = float(data[2 + 2 * i])
        xs.append(t)
        ys.append(log(m))
    sx, sy = sum(xs), sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sxx = sum(x * x for x in xs)
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return -log(2) / slope


def solve(inp):
    return f"{_fit(inp):.6f}\n"


def check(inp, out, payload):
    return cmp_numbers(out, [payload["t0"]], rel=0.01, abs_=1e-9, names=["период полураспада"])
