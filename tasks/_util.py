"""Общие помощники для проверки ответов."""
import re

NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def floats(text):
    """Все числа из текста в виде списка float."""
    return [float(x) for x in NUM_RE.findall(text or "")]


def close(a, b, rel=1e-6, abs_=1e-9):
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def one_number(out):
    """Ровно одно число в выводе. Возвращает (ok, value, msg)."""
    got = floats(out)
    if len(got) != 1:
        return False, None, f"ожидалось одно число, найдено {len(got)}"
    return True, got[0], ""


def cmp_numbers(out, expected, rel=1e-6, abs_=1e-9, names=None):
    """Сравнить последовательность чисел из вывода с эталоном."""
    got = floats(out)
    if len(got) != len(expected):
        return False, f"ожидалось {len(expected)} чисел, получено {len(got)}"
    for i, (g, e) in enumerate(zip(got, expected)):
        if not close(g, e, rel, abs_):
            name = names[i] if names and i < len(names) else f"число #{i + 1}"
            return False, f"{name}: ожидалось {e:.6g}, получено {g:.6g}"
    return True, ""


def cmp_multiset(out, expected, tol=1e-6):
    """Сравнить набор чисел без учёта порядка."""
    got = sorted(floats(out))
    exp = sorted(expected)
    if len(got) != len(exp):
        return False, f"ожидалось {len(exp)} значений, получено {len(got)}"
    for g, e in zip(got, exp):
        if not close(g, e, 1e-6, tol):
            return False, f"значение {g:.6g} не совпало с ожидаемым {e:.6g}"
    return True, ""
