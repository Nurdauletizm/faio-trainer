"""q01 — среднее, мода, медиана."""
import re
from ._util import cmp_numbers

ID = "q01"
TITLE = "Статистика 101"
TOPIC = "математика и статистика"
LEVEL = 1
POINTS = 10
SOURCE = "FAIO-2025, отбор, задача 1"

STATEMENT = """
В классе несколько учеников, каждый сказал, сколько у него домашних животных.

Найдите три величины этого набора чисел:
  1) среднее арифметическое,
  2) моду (значение, которое встречается чаще всех; она единственна),
  3) медиану (серединное значение упорядоченного набора; при чётном
     количестве элементов — среднее двух серединных).

ВХОД
  Одна строка: числа через пробел.

ВЫХОД
  Три числа в одной строке через пробел: среднее, мода, медиана.
  Не менее четырёх знаков после запятой у дробных значений.

ПРИМЕР
  вход:   2 0 1 3 2 1 0 4 1 1
  выход:  1.5 1 1
"""

TEMPLATE = '''import sys

data = [int(x) for x in sys.stdin.read().split()]

# среднее
mean = sum(data) / len(data)

# мода: подсчитайте, сколько раз встречается каждое значение
# медиана: отсортируйте список

print(mean, mode, median)
'''


def gen(rng):
    n = rng.randint(9, 16)
    mode_val = rng.randint(0, 5)
    data = [mode_val] * rng.randint(4, 6)
    others = [v for v in range(0, 6) if v != mode_val]
    while len(data) < n:
        data.append(rng.choice(others))
    # у моды должно быть строгое преимущество
    counts = {v: data.count(v) for v in set(data)}
    while sorted(counts.values())[-1] == sorted(counts.values())[-2]:
        data.append(mode_val)
        counts = {v: data.count(v) for v in set(data)}
    rng.shuffle(data)
    return " ".join(map(str, data)) + "\n", {}


def _answer(data):
    mean = sum(data) / len(data)
    counts = {v: data.count(v) for v in set(data)}
    mode = max(counts, key=lambda v: (counts[v], -v))
    s = sorted(data)
    mid = len(s) // 2
    median = s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2
    return mean, mode, median


def solve(inp):
    data = [int(x) for x in inp.split()]
    mean, mode, median = _answer(data)
    return f"{mean:.6f} {mode} {median:.6f}\n"


def check(inp, out, payload):
    data = [int(x) for x in inp.split()]
    return cmp_numbers(out, list(_answer(data)), rel=1e-4, abs_=1e-4,
                       names=["среднее", "мода", "медиана"])
