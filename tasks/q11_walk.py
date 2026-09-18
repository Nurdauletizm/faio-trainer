"""q11 — случайное блуждание по графу (марковская цепь)."""
from ._util import cmp_numbers

ID = "q11"
TITLE = "Рэй бегает по станции"
TOPIC = "алгоритмы"
LEVEL = 3
POINTS = 30
SOURCE = "FAIO-2024, отбор, задача E"

STATEMENT = """
Космическая станция — это граф из n вершин и m коридоров (рёбер).
Рэй стартует в вершине 0. Каждую минуту он выбирает РАВНОВЕРОЯТНО один
из коридоров, выходящих из текущей вершины, и переходит по нему.
Он не останавливается и не пропускает ходы.

Найдите вероятность того, что ровно через k минут Рэй окажется в вершине t.

Подсказка: заведите массив вероятностей по вершинам и k раз пересчитайте его:
новая вероятность вершины = сумма по соседям (вероятность соседа / его степень).

ВХОД
  Первая строка: четыре целых числа n, m, t, k.
  Далее m строк: по два числа u v — коридор между вершинами u и v
  (граф неориентированный, петель и кратных рёбер нет).

ВЫХОД
  Одно число — вероятность, не менее шести знаков после запятой.

ПРИМЕР
  вход:   3 3 2 2 / 0 1 / 1 2 / 0 2
  выход:  0.500000
"""

TEMPLATE = '''import sys

data = sys.stdin.read().split()
n, m, t, k = (int(data[i]) for i in range(4))

adj = [[] for _ in range(n)]
pos = 4
for _ in range(m):
    u, v = int(data[pos]), int(data[pos + 1])
    pos += 2
    adj[u].append(v)
    adj[v].append(u)

prob = [0.0] * n
prob[0] = 1.0
for step in range(k):
    new = [0.0] * n
    # ...
    prob = new

print(f"{prob[t]:.6f}")
'''


def _walk(inp):
    data = inp.split()
    n, m, t, k = (int(data[i]) for i in range(4))
    adj = [[] for _ in range(n)]
    pos = 4
    for _ in range(m):
        u, v = int(data[pos]), int(data[pos + 1])
        pos += 2
        adj[u].append(v)
        adj[v].append(u)
    prob = [0.0] * n
    prob[0] = 1.0
    for _ in range(k):
        new = [0.0] * n
        for u in range(n):
            if prob[u] and adj[u]:
                share = prob[u] / len(adj[u])
                for v in adj[u]:
                    new[v] += share
        prob = new
    return prob[t]


def gen(rng):
    n = rng.randint(6, 11)
    edges = set()
    # остовное дерево гарантирует связность
    for v in range(1, n):
        u = rng.randrange(v)
        edges.add((min(u, v), max(u, v)))
    extra = rng.randint(1, n)
    attempts = 0
    while extra > 0 and attempts < 100:
        attempts += 1
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v and (min(u, v), max(u, v)) not in edges:
            edges.add((min(u, v), max(u, v)))
            extra -= 1
    edges = sorted(edges)
    t = rng.randrange(n)
    k = rng.randint(2, 6)
    lines = [f"{n} {len(edges)} {t} {k}"] + [f"{u} {v}" for u, v in edges]
    return "\n".join(lines) + "\n", {}


def solve(inp):
    return f"{_walk(inp):.6f}\n"


def check(inp, out, payload):
    return cmp_numbers(out, [_walk(inp)], rel=1e-5, abs_=1e-6, names=["вероятность"])
