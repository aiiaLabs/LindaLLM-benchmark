#!/usr/bin/env python3
"""Figuras que não dependem dos resultados: o diagrama do pipeline e a composição do benchmark.
    python scripts/static_figures.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from lindabench import core  # noqa: E402
from lindabench.i18n import LANGS, cat as cat_name, t  # noqa: E402


def pipeline(path, lang="pt"):
    plt = core._style(lang)
    fig, ax = plt.subplots(figsize=(14, 4.6), dpi=160)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    steps = t(lang, "pipeline_steps")
    w, h, gap, y = 2.35, 2.1, 0.42, 1.55
    x0 = (14 - (len(steps) * w + (len(steps) - 1) * gap)) / 2
    for i, (title, body) in enumerate(steps):
        x = x0 + i * (w + gap)
        last = i == len(steps) - 1
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                    fc=core.LINDA if last else "#f5f3ff", ec=core.LINDA, lw=1.4))
        color = "white" if last else core.NAVY
        ax.text(x + w / 2, y + h - 0.38, f"{i + 1}. {title}", ha="center", va="center", fontsize=12,
                fontweight="bold", color=color)
        ax.text(x + w / 2, y + h / 2 - 0.22, body, ha="center", va="center", fontsize=9.2, color=color, linespacing=1.5)
        if not last:
            ax.add_patch(FancyArrowPatch((x + w + 0.04, y + h / 2), (x + w + gap - 0.04, y + h / 2),
                                         arrowstyle="-|>", mutation_scale=16, color=core.NAVY, lw=1.4))
    # saídas da publicação
    px = x0 + 4 * (w + gap) + w / 2
    for dx, label in zip((-4.6, -2.3, 0), t(lang, "pipeline_outputs")):
        ax.add_patch(FancyArrowPatch((px + dx * 0.12, y - 0.04), (px + dx, 0.82), arrowstyle="-|>", mutation_scale=12,
                                     color=core.NAVY, lw=1, alpha=0.6, connectionstyle="arc3,rad=0"))
        ax.add_patch(FancyBboxPatch((px + dx - 1.05, 0.32), 2.1, 0.46, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="white", ec=core.NAVY, lw=0.9))
        ax.text(px + dx, 0.55, label, ha="center", va="center", fontsize=8.8, color=core.NAVY)
    ax.text(0.15, 4.35, t(lang, "pipeline_title"), fontsize=15, fontweight="bold", color=core.NAVY, va="top")
    fig.savefig(path)


def composition(path, lang="pt"):
    plt = core._style(lang)
    cats = Counter(json.loads((ROOT / "sources/categorias.json").read_text()).values())
    questions = None
    try:  # quando o dataset já existe, mostra também as questões por categoria
        _, q, _ = core.load(refresh=True)
        questions = Counter(q["category"])
    except Exception:  # noqa: BLE001
        pass
    order = [c for c, _ in cats.most_common()]
    fig, ax = plt.subplots(figsize=(9, 3.8), dpi=160)
    y = list(range(len(order)))[::-1]
    series = [(t(lang, "articles"), cats, core.LINDA)] + ([(t(lang, "questions"), questions, core.NAVY)] if questions else [])
    height = 0.62 / len(series)
    for k, (label, counts, color) in enumerate(series):
        offset = (len(series) - 1) / 2 * height - k * height
        values = [counts.get(c, 0) for c in order]
        ax.barh([yy + offset for yy in y], values, height=height * 0.92, color=color, label=label)
        for yy, v in zip(y, values):
            ax.text(v + max(values) * 0.012, yy + offset, str(v), va="center", fontsize=9)
    ax.set_yticks(y, [cat_name(c, lang) for c in order])
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color=core.GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    total = sum(cats.values())
    title = t(lang, "composition_title", a=total) + (t(lang, "composition_q", q=sum(questions.values())) if questions else "")
    ax.set_title(title)
    if questions:
        ax.legend(frameon=False, loc="lower right")
    fig.savefig(path)


def all_languages():
    for lang, conf in LANGS.items():
        out = ROOT / conf["assets"]
        out.mkdir(parents=True, exist_ok=True)
        pipeline(out / "pipeline.png", lang)
        composition(out / "composicao.png", lang)


if __name__ == "__main__":
    all_languages()
    print("pipeline.png e composicao.png em", ", ".join(c["assets"] for c in LANGS.values()))
