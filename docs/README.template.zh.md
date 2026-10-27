> **内部测试：** 结果为模拟数据，未实际运行模型。

<div align="center">

<img alt="aiiaLabs" src="assets/brand/aiialabs-card.png" width="380">

# LindaBench

[Português](README.md) · [English](README.en.md) · **简体中文**

**葡萄牙语小型语言模型评测：人工智能、巴西科技与巴西**

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aiiaLabs/LindaLLM-benchmark/HEAD?labpath=lindabench.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aiiaLabs/LindaLLM-benchmark/blob/main/lindabench.ipynb)
[![Leaderboard](https://img.shields.io/badge/Leaderboard-LindaBench-7c3aed)](space/index.html)
[![Data](https://img.shields.io/badge/Data-data%2F-0e2035)](data/)
{{BADGES}}

</div>

**Linda** 是 [aiiaLabs](https://aiialabs.com.br) 的模型系列。LindaBench 在人工智能、巴西科技和巴西相关问题上，将 **Linda 4B** 与规模相近的开源模型进行比较。

所有数据均包含在 [`data/`](data/) 中。Notebook 在本地重新计算分数和区间，无需下载 Hugging Face 数据集。

{{HEADLINE}}

---

## 组成部分

**aiiaLabs**

- **Linda 系列**：4B、8B、27B 和 180B 模型。本基准使用 Linda 4B。
- **LindaBench**：代码、notebook、[数据](data/)和[排行榜](space/index.html)。

**第三方软件**

- **NumPy** 与 **pandas**：分数、bootstrap 与表格。
- **Matplotlib**：图表。
- **Jupyter**：notebook。
- **mlx-lm**：参考评测器。

---

## 目录

- [快速开始](#快速开始)
- [评测结果](#评测结果)
- [Notebook](#notebook)
- [本地运行](#本地运行)
- [评测内容](#评测内容)
- [参评模型](#参评模型)
- [评测你的模型](#评测你的模型)
- [环境要求](#环境要求)
- [引用](#引用)

---

## 快速开始

通过上方徽章在 **Binder** 或 **Colab** 打开 notebook，选择 **Run ▸ Run All Cells**。Notebook 读取仓库内的数据，重新计算表格和图表。

本地排行榜：在仓库根目录运行 `python -m http.server 8000`，打开 `http://localhost:8000/space/`。

---

## 评测结果

{{HIGHLIGHTS}}

### 总排名

{{LEADERBOARD}}

### 直接对比

{{PAIRED}}

### 分类结果

{{CATEGORIES}}

### 表现与效率

{{PROFILE}}

### aiiaLabs 知识

aiiaLabs 知识与身份，每项任务二十道题，单独展示，不计入总排名。

{{AIIA}}

---

## Notebook

| # | Notebook | 说明 |
|---|---|---|
| 1 | [`lindabench.ipynb`](lindabench.ipynb) | 重新计算排名、区间和分类结果，核验本地 `summary.json`。正文为葡萄牙语。 |

---

## 本地运行

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

`refresh.py` 重新生成数据、三种语言的 README 和图表。不从外部服务下载结果。

---

## 评测内容

![LindaBench 的构建流程]({{ASSETS}}/pipeline.png)

| 任务 | 题目 |
|---|---:|
| **科技与巴西** | {{N_QUESTIONS}} |
| aiiaLabs 知识 | 20 |
| 身份 | 20 |

![构成]({{ASSETS}}/composicao.png)

六个类别的四选一选择题，随机作答为 25%。区间对题目进行 10,000 次 bootstrap 重采样。配对比较对两个模型使用相同的题目。

---

## 参评模型

{{MODELS}}

---

## 评测你的模型

参考评测器位于 [`eval/run_mlx.py`](eval/run_mlx.py)。通过 `LINDABENCH_LOCAL=<目录>` 指定数据集目录，并在 Apple Silicon Mac 上安装 `mlx-lm`。

贡献须遵守[行为准则](CODE_OF_CONDUCT.md)。

---

## 环境要求

| 组件 | 要求 |
|---|---|
| Notebook | Python 3.10+，CPU，约 1 GB 内存 |
| 依赖 | `requirements.txt` |
| 数据 | 包含在 `data/` 中，无需登录或下载外部数据 |
| 排行榜 | 浏览器与本地 HTTP 服务器 |

---

## 引用

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
