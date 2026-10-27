#!/usr/bin/env python3
"""Confere a consistência entre dados, READMEs, gráficos, notebook e leaderboard."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lindabench import core  # noqa: E402
from lindabench.i18n import LANGS  # noqa: E402


def main() -> None:
    summary, questions, results = core.load()
    assert summary == json.loads((ROOT / "results/summary.json").read_text()), "Public summaries disagree"
    assert len(questions) == 333 and len(summary["categories"]) == 6
    answers = dict(zip(questions["id"], questions["answer"]))
    assert questions["id"].is_unique
    assert len(results) == 7
    for model in summary["models"]:
        label = model["label"]
        for task in ("br", "knowledge", "identity"):
            rows = results[label]["tasks"][task]["questions"]
            assert len(rows) == summary["n_questions"][task]
            accuracy = sum(row["pass"] for row in rows) / len(rows)
            assert abs(accuracy - model["tasks"][task]["accuracy"]) < 1e-12, (label, task)
            if task == "br":
                assert {row["id"] for row in rows} == set(answers), label
                assert all(row["pass"] == (row["pred"] == answers[row["id"]]) for row in rows), label
    for task in ("br", "knowledge", "identity"):
        ranked = core.scores(results, task)
        assert ranked.iloc[0]["label"] == "lindav1.2", task
        assert ranked.iloc[0]["acerto"] > ranked.iloc[1]["acerto"], task
    categories = core.by_category(results, questions)
    assert (categories["Linda 4B v1.2"] > categories.drop(columns="Linda 4B v1.2").max(axis=1)).all()
    for label in results:
        if label != "lindav1.2":
            assert core.paired_gain(results, "lindav1.2", label)["ic95_min"] > 0, label
    for lang, config in LANGS.items():
        readme = (ROOT / config["readme"]).read_text()
        assert "{{HEADLINE}}" not in readme
        assert "| 1 | **Linda 4B v1.2**" in readme, lang
        leaders = re.findall(r"<details><summary>(.*?)</summary>", readme)
        assert len(leaders) == 6 and all("Linda 4B v1.2" in row for row in leaders), lang
        figures = list((ROOT / config["assets"]).glob("*.png"))
        assert len(figures) == 9, (lang, len(figures))
    notebook = json.loads((ROOT / "lindabench.ipynb").read_text())
    assert "LindaBench" in "".join(notebook["cells"][0]["source"])
    space = (ROOT / "space/index.html").read_text()
    assert 'const BASE = "../data/"' in space
    assert "huggingface.co/datasets/aiiaLabsDev/LindaBench/resolve/main" not in space
    print("OK: Linda lidera as 3 tarefas e 6 categorias; comparações positivas; 27 gráficos; READMEs, notebook e leaderboard consistentes.")


if __name__ == "__main__":
    main()
