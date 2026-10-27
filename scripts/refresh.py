#!/usr/bin/env python3
"""Gera os dados, READMEs e gráficos do LindaBench em três idiomas.
Roda no GitHub Actions e localmente, sem baixar resultados externos:
    python scripts/refresh.py
"""
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from lindabench import core  # noqa: E402
from lindabench.i18n import LANGS, cat as cat_name, t  # noqa: E402
from scripts.static_figures import all_languages as static_figures  # noqa: E402
from scripts.build_data import generate as generate_data  # noqa: E402

TEMPLATES = {"pt": "docs/README.template.md", "en": "docs/README.template.en.md", "zh": "docs/README.template.zh.md"}


def pct(x):
    return f"{100 * x:.1f}%"


def badge(label, value, color):
    q = lambda s: urllib.parse.quote(str(s)).replace("-", "--")  # noqa: E731
    return f"![{label}](https://img.shields.io/badge/{q(label)}-{q(value)}-{color})"


def name_cell(m):
    name = f"**{m['name']}**" if core.is_linda(m["name"]) else m["name"]
    return f"[{name}](https://huggingface.co/{m['hf']})" if m["weights"] == "open" else name


def img(lang, key, file):
    return f"![{t(lang, key)}]({LANGS[lang]['assets']}/{file})"


def leaderboard(lang, summary, results):
    br = core.scores(results, "br").set_index("label")
    lines = [t(lang, "lb_header"), "|:---:|---|---|---:|---:|:---:|"]
    models = {m["label"]: m for m in summary["models"]}
    for i, label in enumerate(br.index, 1):
        m = models[label]
        b = br.loc[m["label"]]
        lines.append(f"| {i} | {name_cell(m)} | {m['org']} | {m['params']} | **{pct(b['acerto'])}** "
                     f"| {pct(b['ic95_min'])} – {pct(b['ic95_max'])} |")
    sub = t(lang, "lb_sub", n=summary["n_questions"]["br"], date=summary["generated_at"])
    return "\n".join(lines) + f"\n\n<sub>{sub}</sub>"


def headline(lang, results):
    br = core.scores(results, "br")
    open_models = br[[results[label]["weights"] == "open" for label in br["label"]]]
    text = [t(lang, "how_to_read")]
    if len(open_models):
        best = open_models.iloc[0]
        text.append(t(lang, "best_open", name=best["modelo"], acc=pct(best["acerto"]), x=best["acerto"] / 0.25))
    linda = core.latest_linda(list(br["modelo"]))
    if linda:
        acc = br.set_index("modelo").loc[linda, "acerto"]
        text.append(t(lang, "linda_reaches", name=linda, acc=pct(acc), x=acc / 0.25))
    text.append(t(lang, "error_bars"))
    sep = "" if lang == "zh" else " "
    return img(lang, "img_ranking", "ranking_geral.png") + "\n\n" + sep.join(text)


def categories(lang, results, questions):
    table = core.by_category(results, questions)
    out = [img(lang, "img_grid", "ranking_categorias.png"), "", img(lang, "img_heat", "mapa_categorias.png"), ""]
    for cat in table.index:
        n = int((questions["category"] == cat).sum())
        row = table.loc[cat].sort_values(ascending=False)
        lines = [t(lang, "cat_header"), "|:---:|---|---:|"]
        for i, (name, v) in enumerate(row.items(), 1):
            shown = f"**{name}**" if core.is_linda(name) else name
            lines.append(f"| {i} | {shown} | {pct(v)} |")
        summary = t(lang, "cat_summary", cat=cat_name(cat, lang), n=n, name=row.index[0], acc=pct(row.iloc[0]))
        out += [f"<details><summary>{summary}</summary>", "", *lines, "", "</details>", ""]
    return "\n".join(out).rstrip()


def highlights(lang, summary, results, questions):
    br = core.scores(results, "br")
    top = br.iloc[0]
    open_models = br[[results[label]["weights"] == "open" for label in br["label"]]]
    items = [t(lang, "hl_top", name=top["modelo"], acc=pct(top["acerto"]), lo=pct(top["ic95_min"]), hi=pct(top["ic95_max"]))]
    lindas = br[[core.is_linda(m) for m in br["modelo"]]]
    if len(lindas) and len(open_models):
        linda, best = lindas.iloc[0], open_models.iloc[0]
        gain = core.paired_gain(results, linda["label"], best["label"])
        diff = 100 * gain["ganho"]
        clear = gain["ic95_min"] > 0 or gain["ic95_max"] < 0
        items.append(t(lang, "hl_gap", linda=linda["modelo"], diff=abs(diff), best=best["modelo"],
                       verb=t(lang, "hl_ahead" if diff > 0 else "hl_behind"),
                       lo=100 * gain["ic95_min"], hi=100 * gain["ic95_max"]) + t(lang, "hl_clear" if clear else "hl_margin"))
        table = core.by_category(results, questions)
        lead = [cat_name(c, lang) for c in table.index if table.loc[c].idxmax() == linda["modelo"]]
        if lead:
            items.append(t(lang, "hl_cats", linda=linda["modelo"], k=len(lead), n=len(table.index),
                           cats=("、" if lang == "zh" else ", ").join(lead)))
    sizes = [core.params_b(x) for x in br["params"]]
    items.append(t(lang, "hl_scope", m=len(summary["models"]), lo=min(sizes), hi=max(sizes), q=summary["n_questions"]["br"]))
    return "\n".join(items)


def profile(lang):
    return ("| | |\n|:---:|:---:|\n"
            f"| {img(lang, 'img_radar', 'radar.png')} | {img(lang, 'img_size', 'tamanho_desempenho.png')} |\n\n"
            f"<sub>{t(lang, 'profile_caption')}</sub>")


def aiia(lang, results):
    k = core.scores(results, "knowledge").set_index("label")
    idt = core.scores(results, "identity").set_index("label")
    lines = [t(lang, "aiia_header"), "|---|---:|---:|"]
    for label in k.sort_values("acerto", ascending=False).index:
        name = k.loc[label, "modelo"]
        shown = f"**{name}**" if core.is_linda(name) else name
        lines.append(f"| {shown} | {pct(k.loc[label, 'acerto'])} | {pct(idt.loc[label, 'acerto'])} |")
    return img(lang, "img_knowledge", "conhecimento_aiialabs.png") + "\n\n" + "\n".join(lines)


def models_table(lang, summary):
    lines = [t(lang, "models_header"), "|---|---|---:|---|"]
    for m in sorted(summary["models"], key=lambda m: (not core.is_linda(m["name"]), m["org"], m["name"])):
        weights = (t(lang, "proprietary") if m["weights"] == "private"
                   else f"{t(lang, 'open')} · [{m['hf']}](https://huggingface.co/{m['hf']})")
        lines.append(f"| {name_cell(m)} | {m['org']} | {m['params']} | {weights} |")
    return "\n".join(lines)


def render(lang, fields):
    text = (ROOT / TEMPLATES[lang]).read_text()
    for key, value in {**fields, "ASSETS": LANGS[lang]["assets"]}.items():
        text = text.replace("{{" + key + "}}", value)
    left = re.findall(r"\{\{[A-Z_]+\}\}", text)
    assert not left, f"{lang}: placeholders sem valor: {left}"
    (ROOT / LANGS[lang]["readme"]).write_text(text)


def charts(lang, results, questions):
    out = ROOT / LANGS[lang]["assets"]
    out.mkdir(parents=True, exist_ok=True)
    core.plot_scores(core.scores(results, "br"), t(lang, "ranking_title"), out / "ranking_geral.png", chance=0.25, lang=lang)
    core.plot_paired(results, out / "comparacao_linda.png", lang=lang)
    core.plot_category_grid(results, questions, out / "ranking_categorias.png", lang=lang)
    core.plot_categories(core.by_category(results, questions), out / "mapa_categorias.png", lang=lang)
    core.plot_radar(results, questions, path=out / "radar.png", lang=lang)
    core.plot_size(results, out / "tamanho_desempenho.png", lang=lang)
    core.plot_scores(core.scores(results, "knowledge"), t(lang, "knowledge_title"), out / "conhecimento_aiialabs.png", lang=lang)


def main():
    generate_data()
    static_figures()
    plt.close("all")
    summary, questions, results = core.load()

    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n")
    n_models, n_q = len(summary["models"]), summary["n_questions"]["br"]
    for lang in LANGS:
        charts(lang, results, questions)
        plt.close("all")
        render(lang, {
            "BADGES": " ".join([badge(t(lang, "badge_models"), n_models, "7c3aed"),
                                badge(t(lang, "badge_questions"), n_q, "0e2035"),
                                badge(t(lang, "badge_updated"), summary["generated_at"][:10], "lightgrey")]),
            "N_MODELS": str(n_models), "N_QUESTIONS": str(n_q),
            "HEADLINE": headline(lang, results), "HIGHLIGHTS": highlights(lang, summary, results, questions),
            "LEADERBOARD": leaderboard(lang, summary, results),
            "PAIRED": img(lang, "img_paired", "comparacao_linda.png") + f"\n\n<sub>{t(lang, 'paired_caption')}</sub>",
            "CATEGORIES": categories(lang, results, questions), "PROFILE": profile(lang), "AIIA": aiia(lang, results),
            "MODELS": models_table(lang, summary)})
    print(f"atualizado: {n_models} modelos, 3 idiomas ({summary['generated_at']})")


if __name__ == "__main__":
    main()
