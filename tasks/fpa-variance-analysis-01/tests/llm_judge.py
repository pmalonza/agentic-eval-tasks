#!/usr/bin/env python3
"""LLM rubric judge for fpa-variance-analysis-01.

Grades the agent's report.md (and, if present, a trajectory.jsonl of tool
calls) against every criterion in rubric.json, using an LLM as the judge.
Each criterion is graded independently as pass/fail; the final score is
the weighted fraction of criteria passed.

Requires an API key for the configured provider in the environment (see
`call_judge_model`). Never crashes the caller: any failure to reach the
model, parse its output, or read a required file is caught and reported
as a score of 0.0 with a `note` explaining why -- a grader crash must
score 0, not take down the harness.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def _load_json(path: Path) -> dict:
    with open(path) as fh:
        return json.load(fh)


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def call_judge_model(prompt: str, model: str) -> str:
    """Call the configured judge model and return its raw text response.

    Uses the Anthropic API via the `anthropic` package, reading the API
    key from the environment. Swap this function to point at a different
    provider without touching the grading logic in `grade()`.
    """
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if hasattr(block, "text"))


def build_prompt(task_context: str, criterion: dict, report_text: str, trajectory_excerpt: str) -> str:
    return f"""You are grading a single criterion from an expert-authored rubric for an
AI agent evaluation task. Read the agent's report and answer strictly PASS
or FAIL for the one criterion below -- do not grade anything else.

Task context: {task_context}

Criterion ({criterion['id']}): {criterion['criterion']}

Agent's report.md:
---
{report_text}
---

Trajectory excerpt (tool calls the agent made, if relevant to this criterion):
---
{trajectory_excerpt or '(no trajectory provided)'}
---

Respond with exactly one word: PASS or FAIL."""


def parse_verdict(response_text: str) -> bool:
    match = re.search(r"\b(PASS|FAIL)\b", response_text.upper())
    if not match:
        raise ValueError(f"judge response did not contain PASS or FAIL: {response_text!r}")
    return match.group(1) == "PASS"


def grade(task_dir: Path, agent_results_dir: Path) -> dict:
    config = _load_json(task_dir / "tests" / "judge_config.json")
    rubric = _load_json(task_dir / "tests" / "rubric.json")
    model = os.environ.get(config["judge_model_env_var"], config["judge_model_default"])

    report_path = agent_results_dir / config["agent_deliverables"]["report"]
    report_text = _load_text(report_path)

    trajectory_path = agent_results_dir / config["trajectory_path"]
    trajectory_excerpt = _load_text(trajectory_path)[-4000:] if trajectory_path.exists() else ""

    results = []
    for criterion in rubric["criteria"]:
        prompt = build_prompt(config["task_context"], criterion, report_text, trajectory_excerpt)
        response_text = call_judge_model(prompt, model)
        passed = parse_verdict(response_text)
        results.append({"id": criterion["id"], "weight": criterion["weight"], "passed": passed})

    total_weight = sum(r["weight"] for r in results)
    earned_weight = sum(r["weight"] for r in results if r["passed"])
    score = earned_weight / total_weight if total_weight else 0.0

    return {"score": score, "criteria": results}


def main() -> int:
    if len(sys.argv) != 3:
        print(json.dumps({"score": 0.0, "note": "usage: llm_judge.py <task_dir> <agent_results_dir>"}))
        return 0

    task_dir, agent_results_dir = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        result = grade(task_dir, agent_results_dir)
    except Exception as exc:  # noqa: BLE001 - a grader crash must score 0, not take down the harness
        result = {"score": 0.0, "criteria": [], "note": f"judge error: {exc}"}

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
