"""q12 — кластеризация k-means."""
from ._util import floats

ID = "q12"
TITLE = "K-means своими руками"
TOPIC = "машинное обучение"
LEVEL = 3
POINTS = 30
SOURCE = "FAIO-2024, финал, задача D"

STATEMENT = """
Реализуйте алгоритм k-средних (k-means) с ЗАДАННЫМИ начальными центроидами.

Алгоритм:
  1) каждую точку относим к ближайшему центроиду (расстояние евклидово;
     при равенстве расстояний берём центроид с меньшим номером);
  2) каждый центроид переносим в среднее своих точек;
     если к центроиду не попала ни одна точка — оставляем его на месте;
  3) повторяем шаги 1-2, пока центроиды не перестанут меняться
     (или до 300 итераций).

ВХОД
  Первая строка: n — число точек.
  Далее n строк: координаты x y.
  Затем строка: k — число центроидов.
  Далее k строк: начальные координаты центроидов.

ВЫХОД
  k строк по два числа — итоговые координаты центроидов
  (в том же порядке, в каком даны начальные).

ОЦЕНКА
  Ответ принимается, если итоговая функция потерь
  L = (1/n) * сумма квадратов расстояний до ближайшего центроида
  не хуже авторского решения.
"""

TEMPLATE = '''import sys

data = sys.stdin.read().split()
pos = 0
n = int(data[pos]); pos += 1
points = []
for _ in range(n):
    points.append((float(data[pos]), float(data[pos + 1])))
    pos += 2
k = int(data[pos]); pos += 1
cent = []
for _ in range(k):
    cent.append([float(data[pos]), float(data[pos + 1])])
    pos += 2

for step in range(300):
    groups = [[] for _ in range(k)]
    for (x, y) in points:
        # найти ближайший центроид и положить точку в его группу
        ...
    # пересчитать центроиды; если группа пустая — оставить центроид как есть
    ...

for cx, cy in cent:
    print(cx, cy)
'''


def _parse(inp):
    data = inp.split()
    pos = 0
    n = int(data[pos]); pos += 1
    points = []
    for _ in range(n):
        points.append((float(data[pos]), float(data[pos + 1])))
        pos += 2
    k = int(data[pos]); pos += 1
    cent = []
    for _ in range(k):
        cent.append([float(data[pos]), float(data[pos + 1])])
        pos += 2
    return points, cent


def _loss(points, cent):
    total = 0.0
    for x, y in points:
        total += min((x - cx) ** 2 + (y - cy) ** 2 for cx, cy in cent)
    return total / len(points)


def _kmeans(points, cent):
    cent = [list(c) for c in cent]
    for _ in range(300):
        groups = [[] for _ in cent]
        for x, y in points:
            best, bd = 0, None
            for i, (cx, cy) in enumerate(cent):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if bd is None or d < bd - 1e-12:
                    best, bd = i, d
            groups[best].append((x, y))
        moved = False
        for i, g in enumerate(groups):
            if not g:
                continue
            nx = sum(p[0] for p in g) / len(g)
            ny = sum(p[1] for p in g) / len(g)
            if abs(nx - cent[i][0]) > 1e-12 or abs(ny - cent[i][1]) > 1e-12:
                moved = True
            cent[i] = [nx, ny]
        if not moved:
            break
    return cent


def gen(rng):
    k = rng.randint(2, 4)
    centers = []
    while len(centers) < k:
        c = (rng.uniform(5, 45), rng.uniform(5, 45))
        if all((c[0] - o[0]) ** 2 + (c[1] - o[1]) ** 2 > 15 ** 2 for o in centers):
            centers.append(c)
    points = []
    for cx, cy in centers:
        for _ in range(rng.randint(25, 60)):
            points.append((round(cx + rng.gauss(0, 2), 4), round(cy + rng.gauss(0, 2), 4)))
    rng.shuffle(points)
    start = rng.sample(points, k)
    lines = [str(len(points))]
    lines += [f"{x} {y}" for x, y in points]
    lines.append(str(k))
    lines += [f"{x} {y}" for x, y in start]
    return "\n".join(lines) + "\n", {}


def solve(inp):
    points, cent = _parse(inp)
    return "\n".join(f"{cx:.6f} {cy:.6f}" for cx, cy in _kmeans(points, cent)) + "\n"


def check(inp, out, payload):
    points, cent = _parse(inp)
    k = len(cent)
    got = floats(out)
    if len(got) != 2 * k:
        return False, f"ожидалось {k} пар координат, получено {len(got) // 2}"
    student = [[got[2 * i], got[2 * i + 1]] for i in range(k)]
    ref = _kmeans(points, cent)
    ls, lr = _loss(points, student), _loss(points, ref)
    if ls <= lr * 1.0001 + 1e-9:
        return True, ""
    return False, f"функция потерь {ls:.4f} хуже авторской {lr:.4f}"
