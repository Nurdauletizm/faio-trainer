"""q14 — разделяющая прямая (упрощённый SVM)."""
from ._util import floats

ID = "q14"
TITLE = "Разделяющая прямая"
TOPIC = "машинное обучение"
LEVEL = 3
POINTS = 30
SOURCE = "FAIO-2024, финал, задача F (SVM)"

STATEMENT = """
На плоскости даны k точек, каждая принадлежит одному из двух классов
(метка +1 или -1). Гарантируется, что классы разделимы прямой.

Найдите коэффициенты a, b, c прямой a*x + b*y + c = 0, которая их разделяет.
Точка классифицируется так:
    если a*x + b*y + c >= 0, то класс +1, иначе класс -1.

Подсказка: подойдёт любой линейный классификатор. Самый простой —
персептрон: начните с нулевых a, b, c и, пока есть ошибки, для каждой
неверно классифицированной точки делайте
    a += l * x,   b += l * y,   c += l
где l — истинная метка точки. Для разделимых данных это сходится.

ВХОД
  Первая строка: k — число точек.
  Далее k строк: три числа x y l.

ВЫХОД
  Три числа через пробел: a b c.

ОЦЕНКА
  Ответ принимается, если доля верно классифицированных точек не ниже 0.97.
"""

TEMPLATE = '''import sys

data = sys.stdin.read().split()
k = int(data[0])
pts = []
for i in range(k):
    x = float(data[1 + 3 * i])
    y = float(data[2 + 3 * i])
    l = float(data[3 + 3 * i])
    pts.append((x, y, l))

a = b = c = 0.0
for epoch in range(200):
    errors = 0
    for x, y, l in pts:
        pred = 1 if a * x + b * y + c >= 0 else -1
        if pred != l:
            ...
            errors += 1
    if errors == 0:
        break

print(a, b, c)
'''


def _parse(inp):
    data = inp.split()
    k = int(data[0])
    pts = []
    for i in range(k):
        pts.append((float(data[1 + 3 * i]), float(data[2 + 3 * i]), float(data[3 + 3 * i])))
    return pts


def gen(rng):
    k = rng.randint(200, 400)
    a = rng.uniform(-1, 1) or 0.5
    b = rng.uniform(-1, 1) or 0.5
    norm = (a * a + b * b) ** 0.5
    a, b = a / norm, b / norm
    c = rng.uniform(-30, 30)
    margin = rng.uniform(3, 8)
    lines = [str(k)]
    for _ in range(k):
        while True:
            x = rng.uniform(-100, 100)
            y = rng.uniform(-100, 100)
            d = a * x + b * y + c
            if abs(d) >= margin:
                break
        label = 1 if d > 0 else -1
        lines.append(f"{x:.4f} {y:.4f} {label}")
    return "\n".join(lines) + "\n", {}


def _accuracy(pts, a, b, c):
    ok = 0
    for x, y, l in pts:
        pred = 1 if a * x + b * y + c >= 0 else -1
        ok += (pred == l)
    return ok / len(pts)


def solve(inp):
    pts = _parse(inp)
    a = b = c = 0.0
    for _ in range(400):
        errors = 0
        for x, y, l in pts:
            pred = 1 if a * x + b * y + c >= 0 else -1
            if pred != l:
                a += l * x
                b += l * y
                c += l
                errors += 1
        if errors == 0:
            break
    return f"{a:.6f} {b:.6f} {c:.6f}\n"


def check(inp, out, payload):
    got = floats(out)
    if len(got) != 3:
        return False, f"ожидалось три числа a b c, получено {len(got)}"
    a, b, c = got
    if a == 0 and b == 0:
        return False, "прямая вырождена: a и b не могут быть нулями одновременно"
    acc = _accuracy(_parse(inp), a, b, c)
    if acc >= 0.97:
        return True, f"точность {acc:.4f}"
    return False, f"точность {acc:.4f}, а нужно не меньше 0.9700"
