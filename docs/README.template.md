> **Teste interno:** resultados simulados; os modelos não foram executados.

<div align="center">

<img alt="aiiaLabs" src="assets/brand/aiialabs-card.png" width="380">

# LindaBench

**Português** · [English](README.en.md) · [简体中文](README.zh-CN.md)

**Modelos de linguagem pequenos em português sobre inteligência artificial, tecnologia brasileira e Brasil**

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aiiaLabs/LindaLLM-benchmark/HEAD?labpath=lindabench.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aiiaLabs/LindaLLM-benchmark/blob/main/lindabench.ipynb)
[![Leaderboard](https://img.shields.io/badge/Leaderboard-LindaBench-7c3aed)](space/index.html)
[![Data](https://img.shields.io/badge/Data-data%2F-0e2035)](data/)
{{BADGES}}

</div>

A **Linda** é a família de modelos da [aiiaLabs](https://aiialabs.com.br). O LindaBench compara a **Linda 4B** com modelos abertos de tamanho semelhante em perguntas sobre inteligência artificial, tecnologia brasileira e Brasil.

Os dados estão em [`data/`](data/). O notebook recalcula as notas e os intervalos localmente, sem baixar o dataset do Hugging Face.

{{HEADLINE}}

---

## Componentes

**aiiaLabs**

- **Família Linda**: modelos de 4B, 8B, 27B e 180B parâmetros. Este benchmark usa a Linda 4B.
- **LindaBench**: código, notebook, [dados](data/) e [leaderboard](space/index.html).

**Software de terceiros**

- **NumPy** e **pandas**: notas, bootstrap e tabelas.
- **Matplotlib**: gráficos.
- **Jupyter**: notebook.
- **mlx-lm**: avaliador de referência.

---

## Sumário

- [Quickstart](#quickstart)
- [Resultados](#resultados)
- [Notebooks](#notebooks)
- [Rodar localmente](#rodar-localmente)
- [O que é medido](#o-que-é-medido)
- [Modelos avaliados](#modelos-avaliados)
- [Avalie o seu modelo](#avalie-o-seu-modelo)
- [Pré-requisitos](#pré-requisitos)
- [Como citar](#como-citar)

---

## Quickstart

Abra o notebook no **Binder** ou **Colab** pelos badges acima e escolha **Run ▸ Run All Cells**. Ele lê os dados incluídos no repositório e recalcula as tabelas e os gráficos.

Para abrir o leaderboard localmente, execute `python -m http.server 8000` na raiz e acesse `http://localhost:8000/space/`.

---

## Resultados

{{HIGHLIGHTS}}

### Ranking geral

{{LEADERBOARD}}

### Comparação direta

{{PAIRED}}

### Por categoria

{{CATEGORIES}}

### Perfil e eficiência

{{PROFILE}}

### Conhecimento aiiaLabs

Conhecimento sobre a aiiaLabs e identidade, com vinte perguntas por tarefa. São apresentados separadamente do ranking geral.

{{AIIA}}

---

## Notebooks

| # | Notebook | Descrição |
|---|---|---|
| 1 | [`lindabench.ipynb`](lindabench.ipynb) | Recalcula o ranking, os intervalos e as categorias; confere os valores com o `summary.json` local. |

---

## Rodar localmente

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

`refresh.py` regenera os dados, os três READMEs e os gráficos. Nenhum resultado é baixado de um serviço externo.

---

## O que é medido

![Como o LindaBench é construído]({{ASSETS}}/pipeline.png)

| Tarefa | Questões |
|---|---:|
| **Tecnologia e Brasil** | {{N_QUESTIONS}} |
| Conhecimento aiiaLabs | 20 |
| Identidade | 20 |

![Composição]({{ASSETS}}/composicao.png)

Questões de múltipla escolha com 4 alternativas em seis categorias; responder ao acaso dá 25%. Os intervalos usam bootstrap com 10.000 reamostragens das questões. A comparação pareada usa as mesmas questões para os dois modelos.

---

## Modelos avaliados

{{MODELS}}

---

## Avalie o seu modelo

O avaliador de referência está em [`eval/run_mlx.py`](eval/run_mlx.py). Indique a pasta do dataset com `LINDABENCH_LOCAL=<pasta>` e instale `mlx-lm` num Mac com Apple Silicon.

O [Código de Conduta](CODE_OF_CONDUCT.md) se aplica a contribuições.

---

## Pré-requisitos

| Componente | Requisito |
|---|---|
| Notebook | Python 3.10+, CPU, ~1 GB de RAM |
| Dependências | `requirements.txt` |
| Dados | Incluídos em `data/`; sem login ou download externo |
| Leaderboard | Navegador e um servidor HTTP local |

---

## Como citar

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
