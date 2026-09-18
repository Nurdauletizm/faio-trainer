"""q04 — сочетания."""
import re
from math import comb

ID = "q04"
TITLE = "Выбор комплектующих"
TOPIC = "математика и статистика"
LEVEL = 1
POINTS = 10
SOURCE = "FAIO-2024, отбор, задача A"

STATEMENT = """
Команда готовится к полёту на космическую станцию. Нужно выбрать k деталей
ракеты из n имеющихся. Сколькими способами это можно сделать?
Порядок выбора не важен.

ВХОД
  Одна строка: два натуральных числа n и k (1 <= k <= n <= 60).

ВЫХОД
  Одно целое число — ответ.

ПРИМЕР
  вход:   5 2
  выход:  10
"""

TEMPLATE = '''import sys

n, k = [int(x) for x in sys.stdin.read().split()]

# способ 1: формула n! / (k! * (n-k)!)
# способ 2: from math import comb

print(answer)
'''


def gen(rng):
    n = rng.randint(2, 60)
    k = rng.randint(1, n)
    return f"{n} {k}\n", {}


def solve(inp):
    n, k = [int(x) for x in inp.split()]
    return f"{comb(n, k)}\n"


def check(inp, out, payload):
    n, k = [int(x) for x in inp.split()]
    found = re.findall(r"[-+]?\d+", out or "")
    if len(found) != 1:
        return False, f"ожидалось одно целое число, найдено {len(found)}"
    if int(found[0]) != comb(n, k):
        return False, f"ожидалось {comb(n, k)}, получено {found[0]}"
    return True, ""
