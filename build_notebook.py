#!/usr/bin/env python3
"""Gera o notebook do LindaBench."""
import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
    md("""# LindaBench

Este notebook usa os dados locais de `data/`, sem autenticação no Hugging Face.
Escolha **Run ▸ Run All Cells** para recalcular as tabelas e os gráficos."""),
    code("""import os, subprocess, sys
if not os.path.isdir("lindabench"):
    subprocess.run(["git", "clone", "-q", "https://github.com/aiiaLabs/LindaLLM-benchmark.git"], check=True)
    os.chdir("LindaLLM-benchmark")
sys.path.insert(0, os.getcwd())

import pandas as pd
from lindabench import core

summary, questions, results = core.load()
print(f"{len(results)} modelos · {len(questions)} questões")"""),
    md("## 1. Ranking geral"),
    code("""br = core.scores(results, "br")
display(br.style.format({"acerto": "{:.1%}", "ic95_min": "{:.1%}", "ic95_max": "{:.1%}"}))
core.plot_scores(br, "LindaBench · Tecnologia e Brasil", chance=0.25);"""),
    md("""## 2. Comparação direta

Diferença de acerto da Linda para cada modelo, nas mesmas questões, com IC 95% pareado por bootstrap."""),
    code("""linda_label = "lindav1.2"
gains = {r["name"]: core.paired_gain(results, linda_label, label)
         for label, r in results.items() if label != linda_label}
display(pd.DataFrame(gains).T.sort_values("ganho", ascending=False).style.format(
    {"ganho": "{:+.1%}", "ic95_min": "{:+.1%}", "ic95_max": "{:+.1%}"}))
core.plot_paired(results);"""),
    md("## 3. Seis categorias"),
    code("""cats = core.by_category(results, questions)
display(cats.style.format("{:.1%}"))
core.plot_category_grid(results, questions);
core.plot_categories(cats);"""),
    md("## 4. Perfil e eficiência"),
    code("""core.plot_radar(results, questions);
core.plot_size(results);"""),
    md("## 5. Conhecimento e identidade"),
    code("""display(pd.DataFrame({task: core.scores(results, task).set_index("modelo")["acerto"]
                      for task in ("knowledge", "identity")}).style.format("{:.1%}"))
core.plot_scores(core.scores(results, "knowledge"), "Conhecimento aiiaLabs");"""),
    md("## 6. Conferência"),
    code("""for model in summary["models"]:
    for task in ("br", "knowledge", "identity"):
        rows = results[model["label"]]["tasks"][task]["questions"]
        accuracy = sum(q["pass"] for q in rows) / len(rows)
        assert abs(accuracy - model["tasks"][task]["accuracy"]) < 1e-12
for task in ("br", "knowledge", "identity"):
    assert core.scores(results, task).iloc[0]["label"] == linda_label
assert (cats["Linda 4B v1.2"] > cats.drop(columns="Linda 4B v1.2").max(axis=1)).all()
print("OK: notas consistentes; Linda em primeiro nas três tarefas e nas seis categorias.")"""),
]
notebook = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"name": "python3", "display_name": "Python 3"},
    "language_info": {"name": "python"},
})
for index, cell in enumerate(notebook.cells):
    cell.id = f"cell-{index:02d}"
nbf.write(notebook, "lindabench.ipynb")
print("lindabench.ipynb")
