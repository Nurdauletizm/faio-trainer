"""q09 — умножение матриц."""
from ._util import cmp_numbers

ID = "q09"
TITLE = "Гравитационная матрица"
TOPIC = "анализ данных"
LEVEL = 2
POINTS = 20
SOURCE = "FAIO-2024, отбор, задача F"

STATEMENT = """
Даны две матрицы: первая размера a x b, вторая размера b x c.
Выведите их произведение — матрицу a x c.

Напоминание: элемент (i, j) произведения равен сумме произведений
i-й строки первой матрицы на j-й столбец второй.

ВХОД
  Первая строка: три натуральных числа a, b, c.
  Далее a строк по b чисел — первая матрица.
  Далее b строк по c чисел — вторая матрица.

ВЫХОД
  a строк по c чисел — произведение.

ПРИМЕР
  вход:   2 2 2 / 1 2 / 3 4 / 5 6 / 7 8
  выход:  19 22 / 43 50
"""

TEMPLATE = '''import sys

data = sys.stdin.read().split()
pos = 0
a, b, c = int(data[0]), int(data[1]), int(data[2])
pos = 3

A = []
for i in range(a):
    A.append([float(x) for x in data[pos:pos + b]])
    pos += b

B = []
for i in range(b):
    B.append([float(x) for x in data[pos:pos + c]])
    pos += c

for i in range(a):
    row = []
    for j in range(c):
        row.append(...)
    print(" ".join(str(v) for v in row))
'''


def _product(inp):
    data = inp.split()
    a, b, c = int(data[0]), int(data[1]), int(data[2])
    pos = 3
    A, B = [], []
    for _ in range(a):
        A.append([float(x) for x in data[pos:pos + b]])
        pos += b
    for _ in range(b):
        B.append([float(x) for x in data[pos:pos + c]])
        pos += c
    return [[sum(A[i][k] * B[k][j] for k in range(b)) for j in range(c)] for i in range(a)]


def gen(rng):
    a, b, c = rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 6)
    lines = [f"{a} {b} {c}"]
    for _ in range(a):
        lines.append(" ".join(str(rng.randint(-9, 9)) for _ in range(b)))
    for _ in range(b):
        lines.append(" ".join(str(rng.randint(-9, 9)) for _ in range(c)))
    return "\n".join(lines) + "\n", {}


def solve(inp):
    return "\n".join(" ".join(f"{v:.6f}" for v in row) for row in _product(inp)) + "\n"


def check(inp, out, payload):
    expected = [v for row in _product(inp) for v in row]
    return cmp_numbers(out, expected, rel=1e-6, abs_=1e-6)
