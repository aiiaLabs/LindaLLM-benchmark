#!/usr/bin/env python3
"""Roda o LindaBench em qualquer modelo de chat compatível com mlx-lm (Mac com Apple Silicon).

Mesmo método dos resultados publicados:
- Tecnologia e Brasil: múltipla escolha sem texto de apoio; o prompt do assistente começa com "Resposta: letra" e
  vale a alternativa (A-D) de maior logit no token seguinte.
- Conhecimento aiiaLabs e identidade: geração greedy (até 220 tokens), sem system prompt; conhecimento passa se a
  resposta (minúscula, sem acento) bate todos os grupos de regex; identidade passa se contém "linda".

    pip install mlx-lm
    python eval/run_mlx.py --model mlx-community/gemma-3-4b-it-4bit --label gemma-3-4b --name "Gemma 3 4B" \
        --org Google --params 4B --hf google/gemma-3-4b-it
Grava results/<label>.json no formato do dataset.
"""
import argparse
import json
import math
import os
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lindabench.core import fetch  # noqa: E402

MC_PREFIX = "Resposta: letra"
LETTERS = "ABCD"


def norm(text):
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def jsonl(path):
    return [json.loads(line) for line in fetch(path).read_text().splitlines() if line]


def prompt_for(tok, content):
    return tok.apply_chat_template([{"role": "user", "content": content}], add_generation_prompt=True,
                                   enable_thinking=False, tokenize=False)


def stats(passes):
    acc = sum(passes) / len(passes)
    return {"accuracy": acc, "stderr": math.sqrt(acc * (1 - acc) / len(passes)), "n": len(passes)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--adapter")
    for field in ("label", "name", "org", "params", "hf"):
        p.add_argument(f"--{field}", required=True)
    args = p.parse_args()

    if not os.environ.get("LINDABENCH_LOCAL"):
        p.error("indique a pasta do dataset com LINDABENCH_LOCAL=<pasta>.")

    import mlx.core as mx
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler

    model, tok = load(args.model, adapter_path=args.adapter)
    sampler = make_sampler(temp=0.0)
    letter_ids = [tok.encode(" " + l, add_special_tokens=False)[-1] for l in LETTERS]
    assert len(set(letter_ids)) == 4, "as letras A-D precisam virar tokens distintos"

    br = []
    for q in jsonl("questions/tecnologia-brasil.jsonl"):
        body = "\n".join(f"{l}) {t}" for l, t in zip(LETTERS, q["options"]))
        content = f"{q['question']}\n\nAlternativas:\n{body}\n\nResponda apenas com a letra da alternativa correta."
        ids = tok.encode(prompt_for(tok, content) + MC_PREFIX, add_special_tokens=False)[-3500:]
        logits = model(mx.array(ids)[None])[0, -1]
        pred = LETTERS[int(mx.argmax(logits[mx.array(letter_ids)]).item())]
        br.append({"id": q["id"], "pred": pred, "pass": pred == q["answer"]})

    def answer(question):
        return norm(generate(model, tok, prompt=prompt_for(tok, question), max_tokens=220, sampler=sampler))

    knowledge = [{"question": q["question"], "pass": all(any(re.search(alt, a) for alt in group) for group in q["required_groups"])}
                 for q in jsonl("questions/conhecimento-aiialabs.jsonl") for a in [answer(q["question"])]]
    identity = [{"question": q["question"], "pass": "linda" in answer(q["question"])} for q in jsonl("questions/identidade.jsonl")]

    out = {"label": args.label, "name": args.name, "org": args.org, "params": args.params, "hf": args.hf,
           "weights": "open", "tasks": {name: {**stats([x["pass"] for x in rows]), "questions": rows}
                                        for name, rows in (("br", br), ("knowledge", knowledge), ("identity", identity))}}
    path = Path("results") / f"{args.label}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(" | ".join(f"{k}: {v['accuracy']:.3f}" for k, v in out["tasks"].items()), "->", path)


if __name__ == "__main__":
    main()
