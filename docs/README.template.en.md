> **Internal test:** simulated results; the models were not run.

<div align="center">

<img alt="aiiaLabs" src="assets/brand/aiialabs-card.png" width="380">

# LindaBench

[Português](README.md) · **English** · [简体中文](README.zh-CN.md)

**Small language models in Portuguese on artificial intelligence, Brazilian technology and Brazil**

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aiiaLabs/LindaLLM-benchmark/HEAD?labpath=lindabench.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aiiaLabs/LindaLLM-benchmark/blob/main/lindabench.ipynb)
[![Leaderboard](https://img.shields.io/badge/Leaderboard-LindaBench-7c3aed)](space/index.html)
[![Data](https://img.shields.io/badge/Data-data%2F-0e2035)](data/)
{{BADGES}}

</div>

**Linda** is the model family from [aiiaLabs](https://aiialabs.com.br). LindaBench compares **Linda 4B** with similarly sized open models on questions about artificial intelligence, Brazilian technology and Brazil.

All data are included in [`data/`](data/). The notebook recomputes scores and intervals locally, without downloading a Hugging Face dataset.

{{HEADLINE}}

---

## Components

**aiiaLabs**

- **Linda family**: 4B, 8B, 27B and 180B models. This benchmark uses Linda 4B.
- **LindaBench**: code, notebook, [data](data/) and [leaderboard](space/index.html).

**Third-party software**

- **NumPy** and **pandas**: scores, bootstrap and tables.
- **Matplotlib**: charts.
- **Jupyter**: notebook.
- **mlx-lm**: reference evaluator.

---

## Table of Contents

- [Quickstart](#quickstart)
- [Results](#results)
- [Notebooks](#notebooks)
- [Run Locally](#run-locally)
- [What Is Measured](#what-is-measured)
- [Evaluated Models](#evaluated-models)
- [Evaluate Your Model](#evaluate-your-model)
- [Prerequisites](#prerequisites)
- [Citation](#citation)

---

## Quickstart

Open the notebook in **Binder** or **Colab** using the badges above and select **Run ▸ Run All Cells**. It reads the data included in the repository and recomputes tables and charts.

For the local leaderboard, run `python -m http.server 8000` in the repository root and open `http://localhost:8000/space/`.

---

## Results

{{HIGHLIGHTS}}

### Overall Ranking

{{LEADERBOARD}}

### Head-to-Head

{{PAIRED}}

### By Category

{{CATEGORIES}}

### Profile and Efficiency

{{PROFILE}}

### aiiaLabs Knowledge

Knowledge about aiiaLabs and identity, with twenty questions per task. They are shown separately from the overall ranking.

{{AIIA}}

---

## Notebooks

| # | Notebook | Description |
|---|---|---|
| 1 | [`lindabench.ipynb`](lindabench.ipynb) | Recomputes the ranking, intervals and categories; checks values against the local `summary.json`. Notebook text is in Portuguese. |

---

## Run Locally

```bash
git clone https://github.com/aiiaLabs/LindaLLM-benchmark.git
cd LindaLLM-benchmark
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/refresh.py
python scripts/validate.py
jupyter notebook
```

`refresh.py` regenerates the data, all three READMEs and charts. No results are downloaded from an external service.

---

## What Is Measured

![How LindaBench is built]({{ASSETS}}/pipeline.png)

| Task | Questions |
|---|---:|
| **Technology & Brazil** | {{N_QUESTIONS}} |
| aiiaLabs knowledge | 20 |
| Identity | 20 |

![Composition]({{ASSETS}}/composicao.png)

Multiple-choice questions with 4 options in six categories; random guessing scores 25%. Intervals use 10,000 bootstrap resamples of the questions. Paired comparisons use the same questions for both models.

---

## Evaluated Models

{{MODELS}}

---

## Evaluate Your Model

The reference evaluator is in [`eval/run_mlx.py`](eval/run_mlx.py). Point it to the dataset directory with `LINDABENCH_LOCAL=<directory>` and install `mlx-lm` on an Apple Silicon Mac.

Contributions follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Prerequisites

| Component | Requirement |
|---|---|
| Notebook | Python 3.10+, CPU, ~1 GB RAM |
| Dependencies | `requirements.txt` |
| Data | Included in `data/`; no login or external data download |
| Leaderboard | Browser and local HTTP server |

---

## Citation

```bibtex
@misc{lindabench2026,
  title  = {LindaBench},
  author = {{aiiaLabs}},
  year   = {2026},
  url    = {https://github.com/aiiaLabs/LindaLLM-benchmark}
}
```

<div align="center">
<a href="https://aiialabs.com.br"><img src="assets/brand/aiialabs-icon.png" width="40" alt="aiiaLabs"></a>
<br>
<sub>aiiaLabs · LindaBench</sub>
</div>
