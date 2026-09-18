#!/usr/bin/env python3
"""Собирает docs/tasks.js из исходников tasks/*.py.

Веб-версия использует те же генераторы и проверяльщики, что и консольная,
поэтому после правки задач достаточно запустить этот скрипт заново:

    python3 build_web.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS = ROOT / "tasks"
OUT = ROOT / "docs" / "tasks.js"

util = (TASKS / "_util.py").read_text(encoding="utf-8")

bundle = {}
for path in sorted(TASKS.glob("q*.py")):
    src = path.read_text(encoding="utf-8")
    # в браузере нет пакета tasks, поэтому подмешиваем _util прямо в модуль
    src = re.sub(r"^from \._util import .*$", "", src, flags=re.M)
    tid = re.search(r'^ID = "(\w+)"', src, flags=re.M).group(1)
    bundle[tid] = util + "\n\n" + src

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(
    "// Сгенерировано build_web.py — не редактируйте вручную.\n"
    "window.FAIO_SOURCES = " + json.dumps(bundle, ensure_ascii=False) + ";\n",
    encoding="utf-8",
)
print(f"{OUT.relative_to(ROOT)}: {len(bundle)} задач, {OUT.stat().st_size // 1024} КБ")
