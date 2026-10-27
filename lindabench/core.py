"""LindaBench: tabelas e gráficos a partir dos dados em data/."""
import json
import os
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

from lindabench.i18n import cat as cat_name, t

DATA = Path(__file__).resolve().parent.parent / "data"
TASKS = {"br": "Tecnologia e Brasil", "knowledge": "Conhecimento aiiaLabs", "identity": "Identidade (Linda)"}
LINDA = "#7c3aed"   # roxo da marca aiiaLabs
NAVY = "#0e2035"    # azul-marinho da marca
LINDA_SOFT = "#c4b5fd" # versões anteriores da Linda
OTHER = "#b8c0cc"
GRID = "#e5e7eb"


def fetch(path, refresh=False):
    """Lê os dados locais; refresh é mantido para compatibilidade com o notebook."""
    target = Path(os.environ.get("LINDABENCH_LOCAL", DATA)) / path
    if not target.is_file():
        raise FileNotFoundError(f"Dados ausentes: {target}. Gere os dados com python scripts/refresh.py.")
    return target


def load(refresh=False):
    """Carrega summary, questões e resultados locais."""
    summary = json.loads(fetch("summary.json", refresh).read_text())
    lines = fetch("questions/tecnologia-brasil.jsonl", refresh).read_text().splitlines()
    questions = pd.DataFrame([json.loads(line) for line in lines if line])
    results = {m["label"]: json.loads(fetch(f"results/{m['label']}.json", refresh).read_text()) for m in summary["models"]}
    return summary, questions, results


def bootstrap_ci(passes, n_boot=10_000, seed=0):
    passes = np.asarray(passes, dtype=float)
    rng = np.random.default_rng(seed)
    means = rng.choice(passes, size=(n_boot, len(passes))).mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def scores(results, task="br"):
    """Recalcula a nota de cada modelo a partir do acerto questão a questão (não usa o summary)."""
    rows = []
    for label, r in results.items():
        passes = [q["pass"] for q in r["tasks"][task]["questions"]]
        low, high = bootstrap_ci(passes)
        rows.append({"label": label, "modelo": r["name"], "org": r["org"], "params": r["params"],
                     "acerto": np.mean(passes), "ic95_min": low, "ic95_max": high, "n": len(passes)})
    return pd.DataFrame(rows).sort_values("acerto", ascending=False).reset_index(drop=True)


def paired_gain(results, a, b, n_boot=10_000, seed=0):
    """Diferença pareada a - b em tecnologia e Brasil (mesmas questões), com IC 95% por bootstrap."""
    pa = {q["id"]: q["pass"] for q in results[a]["tasks"]["br"]["questions"]}
    pb = {q["id"]: q["pass"] for q in results[b]["tasks"]["br"]["questions"]}
    ids = sorted(pa.keys() & pb.keys())
    diff = np.array([pa[i] - pb[i] for i in ids], dtype=float)
    rng = np.random.default_rng(seed)
    boots = rng.choice(diff, size=(n_boot, len(diff))).mean(axis=1)
    return {"ganho": float(diff.mean()), "ic95_min": float(np.quantile(boots, 0.025)),
            "ic95_max": float(np.quantile(boots, 0.975)), "n": len(ids)}


def by_category(results, questions):
    """Acerto por categoria (linhas) e modelo (colunas)."""
    cat = dict(zip(questions["id"], questions["category"]))
    table = {}
    for label, r in results.items():
        df = pd.DataFrame(r["tasks"]["br"]["questions"])
        df["categoria"] = df["id"].map(cat)
        table[r["name"]] = df.groupby("categoria")["pass"].mean()
    return pd.DataFrame(table)


def is_linda(name):
    return name.lower().startswith("linda")


def latest_linda(names):
    lindas = [n for n in names if is_linda(n)]
    version = lambda n: tuple(int(x) for x in n.split("v")[-1].split(".") if x.isdigit())  # noqa: E731
    return max(lindas, key=version) if lindas else None


def color_for(name, names):
    if not is_linda(name):
        return OTHER
    return LINDA if name == latest_linda(names) else LINDA_SOFT


def params_b(text):
    return float(str(text).rstrip("Bb"))


CJK_FONTS = ["Noto Sans CJK SC", "Noto Sans SC", "Hiragino Sans GB", "Heiti SC", "Arial Unicode MS"]


def _style(lang="pt"):
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    installed = {font.name for font in font_manager.fontManager.ttflist}
    family = [font for font in CJK_FONTS if font in installed] + ["DejaVu Sans"] if lang == "zh" else ["DejaVu Sans"]
    plt.rcParams.update({"font.family": family, "font.size": 10, "axes.edgecolor": GRID,
                         "axes.labelcolor": NAVY, "xtick.color": NAVY, "ytick.color": NAVY, "text.color": NAVY,
                         "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlelocation": "left",
                         "figure.facecolor": "white", "savefig.facecolor": "white", "savefig.bbox": "tight",
                         "savefig.pad_inches": 0.25})
    return plt


def _bars(ax, df, value="acerto", ci=True, label_fmt="{:.1f}%"):
    df = df.iloc[::-1]
    colors = [color_for(m, list(df["modelo"])) for m in df["modelo"]]
    xerr = [100 * (df[value] - df["ic95_min"]), 100 * (df["ic95_max"] - df[value])] if ci else None
    ax.barh(df["modelo"], 100 * df[value], color=colors, height=0.68, xerr=xerr,
            error_kw={"ecolor": NAVY, "alpha": 0.45, "capsize": 0, "lw": 1.2})
    right = df["ic95_max"] if ci else df[value]
    for y, (v, r) in enumerate(zip(df[value], right)):
        ax.text(100 * r + 1.2, y, label_fmt.format(100 * v), va="center", fontsize=9,
                fontweight="bold" if is_linda(df["modelo"].iloc[y]) else "normal")
    for tick, name in zip(ax.get_yticklabels(), df["modelo"]):
        if is_linda(name):
            tick.set_color(LINDA if name == latest_linda(list(df["modelo"])) else "#8b5cf6")
            tick.set_fontweight("bold")
    ax.set_xlim(0, 108)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)


def plot_scores(df, title, path=None, chance=None, subtitle=None, lang="pt"):
    plt = _style(lang)
    fig, ax = plt.subplots(figsize=(9, 0.48 * len(df) + 1.5), dpi=160)
    _bars(ax, df)
    if chance:
        ax.axvline(100 * chance, color=NAVY, lw=1, ls=(0, (3, 3)), alpha=0.5)
        ax.text(100 * chance + 0.8, len(df) - 0.45, t(lang, "chance"), fontsize=8, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel(subtitle or t(lang, "score_xlabel"), fontsize=9, alpha=0.8)
    if path:
        fig.savefig(path)
    return fig


def plot_category_grid(results, questions, path=None, lang="pt"):
    """Um ranking por categoria (pequenos múltiplos)."""
    plt = _style(lang)
    table = by_category(results, questions)
    cats = list(table.index)
    cols = 3
    rows = -(-len(cats) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(15, 3.6 * rows), dpi=150)
    for ax, cat in zip(axes.flat, cats):
        df = pd.DataFrame({"modelo": table.columns, "acerto": table.loc[cat].values}).sort_values("acerto", ascending=False)
        _bars(ax, df, ci=False, label_fmt="{:.0f}")
        n = int((questions["category"] == cat).sum())
        ax.set_title(f"{cat_name(cat, lang)}  ·  {t(lang, 'n_questions', n=n)}", fontsize=11)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="y", labelsize=8.5)
    for ax in list(axes.flat)[len(cats):]:
        ax.axis("off")
    fig.suptitle(t(lang, "grid_title"), x=0.01, ha="left", fontsize=15, fontweight="bold", color=NAVY)
    fig.tight_layout()
    if path:
        fig.savefig(path)
    return fig


def plot_radar(results, questions, top=5, path=None, lang="pt"):
    """Perfil por categoria dos modelos com maior nota geral."""
    plt = _style(lang)
    table = by_category(results, questions)
    overall = scores(results, "br")
    names = list(overall["modelo"].head(top))
    cats = list(table.index)
    angles = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist()
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=150, subplot_kw={"polar": True})
    palette = [NAVY, "#3b82f6", "#14b8a6", "#f59e0b", "#94a3b8", "#ef4444"]
    others = iter(palette)
    for name in names:
        vals = (100 * table[name]).tolist()
        latest = name == latest_linda(names)
        color = color_for(name, names) if is_linda(name) else next(others)
        ax.plot(angles + angles[:1], vals + vals[:1], color=color, lw=2.8 if latest else 1.5,
                ls="--" if is_linda(name) and not latest else "-", label=name, zorder=3 if latest else 2)
        ax.fill(angles + angles[:1], vals + vals[:1], color=color, alpha=0.14 if latest else 0.03)
    ax.set_xticks(angles, [textwrap.fill(cat_name(c, lang), 16 if lang != "zh" else 7) for c in cats], fontsize=9)
    ax.tick_params(axis="x", pad=14)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100], ["25", "50", "75", "100"], fontsize=7, alpha=0.6)
    ax.spines["polar"].set_color(GRID)
    ax.grid(color=GRID)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False, fontsize=9)
    ax.set_title(t(lang, "radar_title", n=len(names)), pad=24)
    if path:
        fig.savefig(path)
    return fig


def plot_size(results, path=None, lang="pt"):
    """Parâmetros x acerto: quanto cada modelo entrega pelo tamanho."""
    plt = _style(lang)
    df = scores(results, "br")
    df["params"] = [params_b(results[label]["params"]) for label in df["label"]]
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=160)
    names = list(df["modelo"])
    df["label_y"] = 100 * df["acerto"]
    for _, group in df.groupby("params"):  # afasta rótulos de modelos do mesmo tamanho
        last = None
        for idx in group.sort_values("label_y", ascending=False).index:
            if last is not None and last - df.at[idx, "label_y"] < 3.2:
                df.at[idx, "label_y"] = last - 3.2
            last = df.at[idx, "label_y"]
    for _, r in df.iterrows():
        linda = is_linda(r["modelo"])
        color = color_for(r["modelo"], names)
        ax.scatter(r["params"], 100 * r["acerto"], s=220 if linda else 110, color=color, edgecolor="white", lw=1.5, zorder=3)
        # rótulo à esquerda quando há outro modelo logo à direita, na mesma altura
        crowded = ((df["params"] > r["params"]) & (df["params"] - r["params"] < 0.7)
                   & ((100 * df["acerto"] - r["label_y"]).abs() < 8)).any()
        ax.annotate(r["modelo"], (r["params"], 100 * r["acerto"]),
                    xytext=(r["params"] + (-0.09 if crowded else 0.09), r["label_y"]),
                    textcoords="data", va="center", ha="right" if crowded else "left", fontsize=9, fontweight="bold" if linda else "normal",
                    color=LINDA if linda else NAVY,
                    arrowprops={"arrowstyle": "-", "color": GRID, "lw": 0.8} if abs(r["label_y"] - 100 * r["acerto"]) > 0.5 else None)
    ax.set_xlabel(t(lang, "size_x"))
    ax.set_ylabel(t(lang, "size_y"))
    ax.set_xlim(df["params"].min() - 0.4, df["params"].max() + 1.2)
    ax.set_ylim(max(0, min(100 * df["acerto"].min(), df["label_y"].min()) - 6), min(100, 100 * df["acerto"].max() + 8))
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_title(t(lang, "size_title"))
    if path:
        fig.savefig(path)
    return fig


def plot_categories(table, path=None, lang="pt"):
    from matplotlib.colors import LinearSegmentedColormap

    plt = _style(lang)
    order = table.mean().sort_values(ascending=False).index
    table = table[order]
    cmap = LinearSegmentedColormap.from_list("aiia", ["#f5f3ff", "#c4b5fd", LINDA, "#3b0d8c"])
    fig, ax = plt.subplots(figsize=(1.25 * len(table.columns) + 3.2, 0.6 * len(table) + 1.8), dpi=150)
    ax.imshow(100 * table.values, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(table.columns)), table.columns, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(table.index)), [cat_name(c, lang) for c in table.index], fontsize=9)
    for tick, name in zip(ax.get_xticklabels(), table.columns):
        if is_linda(name):
            tick.set_color(LINDA)
            tick.set_fontweight("bold")
    for i in range(len(table.index)):
        for j in range(len(table.columns)):
            v = 100 * table.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9, color="white" if v > 55 else NAVY)
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_title(t(lang, "heat_title"))
    if path:
        fig.savefig(path)
    return fig


def plot_paired(results, path=None, lang="pt"):
    """Diferença pareada (pontos) entre a Linda mais recente e cada modelo, com IC 95%."""
    plt = _style(lang)
    names = {label: r["name"] for label, r in results.items()}
    linda = latest_linda(list(names.values()))
    linda_label = next(label for label, name in names.items() if name == linda)
    rows = sorted(((names[label], paired_gain(results, linda_label, label)) for label in results if label != linda_label),
                  key=lambda x: x[1]["ganho"])
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(rows) + 1.6), dpi=160)
    for y, (name, g) in enumerate(rows):
        clear = g["ic95_min"] > 0 or g["ic95_max"] < 0
        color = (LINDA if g["ganho"] > 0 else "#ef4444") if clear else OTHER
        ax.plot([100 * g["ic95_min"], 100 * g["ic95_max"]], [y, y], color=color, lw=3, solid_capstyle="round", alpha=0.55)
        ax.scatter(100 * g["ganho"], y, s=90, color=color, zorder=3, edgecolor="white", lw=1.2)
        ax.text(100 * g["ic95_max"] + 0.8, y, f"{100 * g['ganho']:+.1f} pts", va="center", fontsize=9,
                fontweight="bold" if clear else "normal", color=NAVY)
    ax.axvline(0, color=NAVY, lw=1, alpha=0.6)
    ax.set_yticks(range(len(rows)), [name for name, _ in rows])
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    lo = min(100 * g["ic95_min"] for _, g in rows)
    hi = max(100 * g["ic95_max"] for _, g in rows)
    ax.set_xlim(min(-5, lo - 3), hi + 9)
    ax.set_xlabel(t(lang, "paired_x", linda=linda), fontsize=9, alpha=0.8)
    ax.set_title(t(lang, "paired_title", linda=linda))
    if path:
        fig.savefig(path)
    return fig
