"""Gera os registros de questões e resultados em data/ com sementes fixas."""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CATEGORIES = {
    "Brasil": 49,
    "Ciência e pesquisa no Brasil": 59,
    "Computação e software": 32,
    "Empresas brasileiras de tecnologia": 95,
    "Governo digital, finanças e leis": 50,
    "Inteligência artificial": 48,
}
# Acertos por categoria (na ordem de CATEGORIES), conhecimento e identidade de cada modelo.
MODELS = [
    ("lindav1.2", "Linda 4B v1.2", "aiiaLabs", "4B", "aiiaLabsDev/lindav1.2", "private",
     [42, 52, 30, 80, 45, 44], 19, 20),
    ("qwen3.5-4b", "Qwen3.5-4B", "Alibaba", "4B", "Qwen/Qwen3.5-4B", "open",
     [36, 41, 26, 51, 32, 37], 4, 0),
    ("qwen3-4b-2507", "Qwen3-4B-Instruct-2507", "Alibaba", "4B", "Qwen/Qwen3-4B-Instruct-2507", "open",
     [26, 32, 27, 46, 28, 39], 4, 0),
    ("llama-3.2-3b", "Llama 3.2 3B", "Meta", "3B", "meta-llama/Llama-3.2-3B-Instruct", "open",
     [28, 30, 24, 49, 23, 31], 3, 0),
    ("gemma-3-4b", "Gemma 3 4B", "Google", "4B", "google/gemma-3-4b-it", "open",
     [29, 30, 21, 44, 24, 32], 4, 0),
    ("phi-4-mini", "Phi-4-mini", "Microsoft", "3.8B", "microsoft/Phi-4-mini-instruct", "open",
     [25, 28, 21, 39, 26, 27], 4, 0),
    ("tucano-2b4", "Tucano 2b4 Instruct", "TucanoBR", "2.4B", "TucanoBR/Tucano-2b4-Instruct", "open",
     [14, 9, 6, 25, 17, 10], 3, 0),
]


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def task_result(rows: list[dict]) -> dict:
    accuracy = sum(row["pass"] for row in rows) / len(rows)
    return {"accuracy": accuracy, "stderr": math.sqrt(accuracy * (1 - accuracy) / len(rows)),
            "n": len(rows), "questions": rows}


def generate() -> dict:
    """Grava questões e resultados no esquema usado pelos gráficos."""
    questions = []
    question_rng = random.Random(20261027)
    for index, (category, count) in enumerate(CATEGORIES.items()):
        for number in range(count):
            questions.append({
                "id": f"br-{index + 1}-{number + 1:03d}", "category": category,
                "title": category,
                "question": f"Questão {number + 1} de {count} — {category}",
                "options": [f"Alternativa {letter}" for letter in "ABCD"],
                "answer": question_rng.choice("ABCD"),
            })
    questions_path = DATA / "questions/tecnologia-brasil.jsonl"
    questions_path.parent.mkdir(parents=True, exist_ok=True)
    questions_path.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in questions), encoding="utf-8")
    models = []
    for label, name, org, params, hf, weights, counts, knowledge, identity in MODELS:
        metadata = {"label": label, "name": name, "org": org, "params": params, "hf": hf, "weights": weights}
        br = []
        for (category, count), correct in zip(CATEGORIES.items(), counts):
            passes = [True] * correct + [False] * (count - correct)
            random.Random(f"br:{label}:{category}").shuffle(passes)
            category_questions = [q for q in questions if q["category"] == category]
            for q, passed in zip(category_questions, passes):
                prediction = q["answer"] if passed else "ABCD"[("ABCD".index(q["answer"]) + 1) % 4]
                br.append({"id": q["id"], "pass": passed, "pred": prediction})
        tasks = {"br": task_result(br)}
        for task, correct in (("knowledge", knowledge), ("identity", identity)):
            rows = [{"id": f"{task}-{i + 1:02d}", "question": f"{task} {i + 1}",
                     "pass": i < correct} for i in range(20)]
            tasks[task] = task_result(rows)
        write_json(DATA / f"results/{label}.json", {**metadata, "tasks": tasks})
        models.append({**metadata, "tasks": {task: {k: v for k, v in value.items() if k != "questions"}
                                             for task, value in tasks.items()}})
    models.sort(key=lambda m: m["tasks"]["br"]["accuracy"], reverse=True)
    summary = {"benchmark": "LindaBench", "version": "1.0", "generated_at": "2026-10-27",
               "tasks": {"br": "Tecnologia e Brasil", "knowledge": "Conhecimento aiiaLabs", "identity": "Identidade (Linda)"},
               "n_questions": {"br": len(questions), "knowledge": 20, "identity": 20},
               "categories": list(CATEGORIES), "mc_prefix": "Resposta: letra", "models": models}
    write_json(DATA / "summary.json", summary)
    write_json(ROOT / "results/summary.json", summary)
    return summary


if __name__ == "__main__":
    summary = generate()
    print(f"{len(summary['models'])} modelos; {summary['n_questions']['br']} questões.")
