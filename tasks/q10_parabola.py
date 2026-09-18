"""q10 — парабола по трём точкам и производная."""
from ._util import cmp_numbers

ID = "q10"
TITLE = "Скорость ракеты"
TOPIC = "алгоритмы"
LEVEL = 2
POINTS = 20
SOURCE = "FAIO-2024, отбор, задачи C и D"

STATEMENT = """
График «время — расстояние» ракеты является параболой y = a*x^2 + b*x + c.
Датчик успел записать три точки, но описал их запутанно:

  - первая точка имеет координаты (x1, y1);
  - вторая точка ЛЕВЕЕ первой на x2 и ВЫШЕ третьей на y2,
    то есть её координаты (x1 - x2, y3 + y2);
  - третья точка имеет координаты (x3, y3).

Восстановите коэффициенты a, b, c, а затем найдите скорость ракеты
в момент времени d (скорость — производная расстояния по времени).

ВХОД
  Одна строка: семь вещественных чисел x1 y1 x2 y2 x3 y3 d.

ВЫХОД
  Четыре числа через пробел: a b c v, где v — скорость в момент d.

ПРИМЕР
  вход:   1 6 2 1 0 1 2
  выход:  2 3 1 11
"""

TEMPLATE = '''import sys

x1, y1, x2, y2, x3, y3, d = [float(v) for v in sys.stdin.read().split()]

# три точки параболы
points = [(x1, y1), (x1 - x2, y3 + y2), (x3, y3)]

# решите систему из трёх уравнений a*x^2 + b*x + c = y
# (метод Гаусса или формулы Крамера)

v = 2 * a * d + b
print(a, b, c, v)
'''


def _solve3(points):
    """Решает систему для параболы через три точки методом Крамера."""
    (xa, ya), (xb, yb), (xc, yc) = points

    def det(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

    base = [[xa * xa, xa, 1], [xb * xb, xb, 1], [xc * xc, xc, 1]]
    ys = [ya, yb, yc]
    d0 = det(base)
    out = []
    for col in range(3):
        m = [row[:] for row in base]
        for r in range(3):
            m[r][col] = ys[r]
        out.append(det(m) / d0)
    return out


def gen(rng):
    a = rng.choice([-3, -2, -1, 1, 2, 3]) + round(rng.uniform(-0.5, 0.5), 2)
    b = round(rng.uniform(-10, 10), 2)
    c = round(rng.uniform(-20, 20), 2)
    xs = rng.sample([round(v * 0.5, 1) for v in range(-20, 21)], 3)
    x1, xm, x3 = xs
    f = lambda x: a * x * x + b * x + c
    y1, ym, y3 = f(x1), f(xm), f(x3)
    x2 = x1 - xm
    y2 = ym - y3
    d = round(rng.uniform(1, 20), 2)
    inp = f"{x1} {y1:.6f} {x2} {y2:.6f} {x3} {y3:.6f} {d}\n"
    return inp, {"a": a, "b": b, "c": c, "v": 2 * a * d + b}


def solve(inp):
    x1, y1, x2, y2, x3, y3, d = [float(v) for v in inp.split()]
    a, b, c = _solve3([(x1, y1), (x1 - x2, y3 + y2), (x3, y3)])
    return f"{a:.6f} {b:.6f} {c:.6f} {2 * a * d + b:.6f}\n"


def check(inp, out, payload):
    exp = [payload["a"], payload["b"], payload["c"], payload["v"]]
    return cmp_numbers(out, exp, rel=1e-3, abs_=1e-3, names=["a", "b", "c", "скорость"])
