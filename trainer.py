#!/usr/bin/env python3
"""FAIO Trainer — тренажёр для подготовки к отборочному туру Fizmat AI Olympiad.

Задачи генерируются заново при каждом запуске, поэтому одну и ту же задачу
можно решать много раз. Проверка автоматическая, как на Яндекс.Контесте:
решение читает данные из stdin и печатает ответ в stdout.

    python3 trainer.py list              список задач
    python3 trainer.py show q01          условие + создать заготовку решения
    python3 trainer.py sample q01        показать пример входных данных
    python3 trainer.py check q01         проверить своё решение
    python3 trainer.py hint q01          подсмотреть авторское решение (спойлер!)
    python3 trainer.py exam              пробный тур на 4 часа
    python3 trainer.py score             прогресс по всем задачам
    python3 trainer.py selftest          самопроверка тренажёра
"""
import argparse
import importlib
import inspect
import json
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / "tasks"
SOL_DIR = ROOT / "solutions"
STATE_FILE = ROOT / ".progress.json"
RUN_TIMEOUT = 20
DEFAULT_TESTS = 8

LEVEL_NAME = {1: "разминка", 2: "средняя", 3: "сложная"}


# ----------------------------------------------------------------- инфраструктура
def load_tasks():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    tasks = {}
    for path in sorted(TASKS_DIR.glob("q*.py")):
        mod = importlib.import_module(f"tasks.{path.stem}")
        tasks[mod.ID] = mod
    return tasks


def get_task(tasks, tid):
    tid = tid.lower().strip()
    if tid in tasks:
        return tasks[tid]
    matches = [t for k, t in tasks.items() if k.startswith(tid)]
    if len(matches) == 1:
        return matches[0]
    print(f"Задача '{tid}' не найдена. Доступные: {', '.join(sorted(tasks))}")
    sys.exit(1)


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"solved": {}, "exam": None}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def solution_path(task):
    return SOL_DIR / f"{task.ID}.py"


def ensure_solution(task):
    """Создаёт заготовку решения, если её ещё нет. Возвращает (path, created)."""
    path = solution_path(task)
    if path.exists():
        return path, False
    SOL_DIR.mkdir(exist_ok=True)
    header = (
        f"# {task.ID}. {task.TITLE}\n"
        f"# {task.SOURCE}\n"
        f"# Решение читает данные из stdin и печатает ответ в stdout.\n\n"
    )
    path.write_text(header + task.TEMPLATE, encoding="utf-8")
    return path, True


def run_solution(path, stdin_text):
    """Запускает решение ученика. Возвращает (ok, stdout, error)."""
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, "", f"превышено время работы ({RUN_TIMEOUT} с)"
    if proc.returncode != 0:
        err = (proc.stderr or "").strip().splitlines()
        tail = "\n     ".join(err[-4:]) if err else "нет сообщения"
        return False, proc.stdout, f"решение упало с ошибкой:\n     {tail}"
    return True, proc.stdout, ""


def shorten(text, limit=400):
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + f"\n... (ещё {len(text) - limit} символов)"


# ----------------------------------------------------------------- команды
def cmd_list(tasks, args):
    print("\n  ЗАДАЧИ ТРЕНАЖЁРА\n")
    state = load_state()
    by_topic = {}
    for tid in sorted(tasks):
        by_topic.setdefault(tasks[tid].TOPIC, []).append(tasks[tid])
    total = 0
    for topic, group in by_topic.items():
        print(f"  {topic.upper()}")
        for task in group:
            mark = "[решено]" if state["solved"].get(task.ID) else "[      ]"
            total += task.POINTS
            print(f"    {mark} {task.ID}  {task.TITLE:<34} {task.POINTS:>3} б.  "
                  f"({LEVEL_NAME[task.LEVEL]}) — {task.SOURCE}")
        print()
    solved = sum(tasks[t].POINTS for t in state["solved"] if t in tasks)
    print(f"  Набрано: {solved} из {total} баллов\n")
    print("  Начать:  python3 trainer.py show q01\n")


def cmd_show(tasks, args):
    task = get_task(tasks, args.task)
    print("\n" + "=" * 72)
    print(f"  {task.ID}. {task.TITLE}   [{task.POINTS} баллов, {LEVEL_NAME[task.LEVEL]}]")
    print(f"  Прообраз: {task.SOURCE}")
    print("=" * 72)
    print(task.STATEMENT.strip())
    print("-" * 72)
    path, created = ensure_solution(task)
    rel = path.relative_to(ROOT)
    print(f"  {'Создана заготовка' if created else 'Ваше решение'}: {rel}")
    print(f"  Проверить:  python3 trainer.py check {task.ID}")
    print()


def cmd_sample(tasks, args):
    task = get_task(tasks, args.task)
    rng = random.Random(args.seed)
    stdin_text, payload = task.gen(rng)
    print(f"\n  Пример входных данных для {task.ID} (seed={args.seed}):\n")
    print(shorten(stdin_text, 1200))
    print("\n  Правильный ответ:\n")
    print(shorten(task.solve(stdin_text), 600))
    print()


def cmd_check(tasks, args):
    task = get_task(tasks, args.task)
    path = solution_path(task)
    if not path.exists():
        print(f"\n  Нет файла решения. Сначала: python3 trainer.py show {task.ID}\n")
        return 1
    print(f"\n  Проверяю {task.ID}. {task.TITLE} — {args.tests} случайных тестов\n")
    rng = random.Random(args.seed)
    passed = 0
    for i in range(1, args.tests + 1):
        stdin_text, payload = task.gen(random.Random(rng.randrange(10 ** 9)))
        ok, out, err = run_solution(path, stdin_text)
        if not ok:
            print(f"  тест {i}: ОШИБКА — {err}")
            print(f"\n  Входные данные теста:\n{shorten(stdin_text)}\n")
            break
        good, msg = task.check(stdin_text, out, payload)
        if good:
            passed += 1
            print(f"  тест {i}: ok")
        else:
            print(f"  тест {i}: НЕВЕРНО — {msg}")
            print(f"\n  Входные данные теста:\n{shorten(stdin_text)}")
            print(f"\n  Ваш вывод:\n{shorten(out, 300) or '(пусто)'}")
            print(f"\n  Правильный ответ:\n{shorten(task.solve(stdin_text), 300)}\n")
            break
    print()
    state = load_state()
    if passed == args.tests:
        print(f"  ЗАЧТЕНО: все {args.tests} тестов пройдены, +{task.POINTS} баллов\n")
        state["solved"][task.ID] = datetime.now().isoformat(timespec="seconds")
        save_state(state)
        return 0
    print(f"  Пройдено {passed} из {args.tests}. Исправьте решение и запустите проверку снова.")
    print(f"  Подсказка по теме: python3 trainer.py hint {task.ID}\n")
    return 1


def cmd_hint(tasks, args):
    task = get_task(tasks, args.task)
    print(f"\n  СПОЙЛЕР: авторское решение {task.ID}. {task.TITLE}")
    print("  Сначала попробуйте сами — иначе тренажёр бесполезен.\n")
    print("-" * 72)
    print(inspect.getsource(task.solve))
    print("-" * 72 + "\n")


def cmd_exam(tasks, args):
    state = load_state()
    rng = random.Random(args.seed if args.seed is not None else int(time.time()))
    pool = sorted(tasks)
    picked = []
    for level in (1, 1, 2, 2, 3, 3, 1, 2):
        cands = [t for t in pool if tasks[t].LEVEL == level and t not in picked]
        if cands:
            picked.append(rng.choice(cands))
    picked = picked[: args.tasks]
    state["exam"] = {
        "tasks": picked,
        "started": time.time(),
        "minutes": args.minutes,
    }
    save_state(state)
    print(f"\n  ПРОБНЫЙ ТУР начат. Время: {args.minutes} минут. Задач: {len(picked)}")
    print(f"  Максимум: {sum(tasks[t].POINTS for t in picked)} баллов\n")
    for tid in picked:
        print(f"    {tid}  {tasks[tid].TITLE:<34} {tasks[tid].POINTS:>3} б.")
    print("\n  Условия:   python3 trainer.py show <id>")
    print("  Проверка:  python3 trainer.py check <id>")
    print("  Результат: python3 trainer.py score\n")
    print("  Правила как на настоящем туре: без ИИ-ассистентов, без чужого кода,")
    print("  до конца времени не вставать. Можно: документация Python и свои заметки.\n")


def cmd_score(tasks, args):
    state = load_state()
    exam = state.get("exam")
    print()
    if exam:
        left = exam["minutes"] * 60 - (time.time() - exam["started"])
        status = f"осталось {int(left // 60)} мин {int(left % 60)} с" if left > 0 else "ВРЕМЯ ВЫШЛО"
        print(f"  ПРОБНЫЙ ТУР: {status}")
        got = sum(tasks[t].POINTS for t in exam["tasks"] if state["solved"].get(t))
        mx = sum(tasks[t].POINTS for t in exam["tasks"])
        for tid in exam["tasks"]:
            mark = "решено" if state["solved"].get(tid) else "  —   "
            print(f"    [{mark}] {tid}  {tasks[tid].TITLE}")
        print(f"  Итого за тур: {got} из {mx} баллов\n")
    solved = [t for t in sorted(tasks) if state["solved"].get(t)]
    print(f"  ВСЕГО РЕШЕНО: {len(solved)} из {len(tasks)} задач, "
          f"{sum(tasks[t].POINTS for t in solved)} из {sum(t.POINTS for t in tasks.values())} баллов")
    unsolved = [t for t in sorted(tasks) if t not in solved]
    if unsolved:
        print(f"  Осталось: {', '.join(unsolved)}")
    print()


def cmd_selftest(tasks, args):
    """Прогоняет авторские решения через проверяльщики — контроль самого тренажёра."""
    print("\n  САМОПРОВЕРКА ТРЕНАЖЁРА\n")
    bad = 0
    for tid in sorted(tasks):
        task = tasks[tid]
        fails = []
        t0 = time.time()
        for seed in range(args.tests):
            rng = random.Random(1000 + seed)
            stdin_text, payload = task.gen(rng)
            out = task.solve(stdin_text)
            ok, msg = task.check(stdin_text, out, payload)
            if not ok:
                fails.append(f"seed={seed}: {msg}")
        dt = time.time() - t0
        if fails:
            bad += 1
            print(f"  {tid}: ПРОВАЛ ({len(fails)}/{args.tests}) — {fails[0]}")
        else:
            print(f"  {tid}: ok  ({args.tests} тестов, {dt:.1f} с)")
    print(f"\n  Итог: {len(tasks) - bad} из {len(tasks)} задач исправны\n")
    return 1 if bad else 0


def main():
    tasks = load_tasks()
    p = argparse.ArgumentParser(description="FAIO Trainer", add_help=True)
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("list", help="список задач")

    sp = sub.add_parser("show", help="условие задачи")
    sp.add_argument("task")

    sp = sub.add_parser("sample", help="пример входных данных и ответа")
    sp.add_argument("task")
    sp.add_argument("--seed", type=int, default=7)

    sp = sub.add_parser("check", help="проверить своё решение")
    sp.add_argument("task")
    sp.add_argument("--tests", type=int, default=DEFAULT_TESTS)
    sp.add_argument("--seed", type=int, default=None)

    sp = sub.add_parser("hint", help="авторское решение (спойлер)")
    sp.add_argument("task")

    sp = sub.add_parser("exam", help="пробный тур")
    sp.add_argument("--tasks", type=int, default=6)
    sp.add_argument("--minutes", type=int, default=240)
    sp.add_argument("--seed", type=int, default=None)

    sub.add_parser("score", help="прогресс")

    sp = sub.add_parser("selftest", help="самопроверка тренажёра")
    sp.add_argument("--tests", type=int, default=5)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        print(__doc__)
        return 0
    if getattr(args, "seed", None) is None and args.cmd == "check":
        args.seed = random.randrange(10 ** 9)
    fn = {
        "list": cmd_list, "show": cmd_show, "sample": cmd_sample, "check": cmd_check,
        "hint": cmd_hint, "exam": cmd_exam, "score": cmd_score, "selftest": cmd_selftest,
    }[args.cmd]
    return fn(tasks, args) or 0


if __name__ == "__main__":
    sys.exit(main())
