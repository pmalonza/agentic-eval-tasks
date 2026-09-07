#!/usr/bin/env bash
# Orchestrates the full grading pipeline: programmatic checks + the LLM
# rubric judge, combined into a single scalar reward. Always writes
# reward.txt, even if a grading step crashes outright -- a crash scores
# 0 on that component, it never leaves the harness without a reward file.
set -uo pipefail

TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_RESULTS_DIR="${1:?usage: test.sh <agent_results_dir>}"

PROG_WEIGHT=0.30
JUDGE_WEIGHT=0.70

extract_score() {
  # $1 = a JSON blob (or garbage); prints its "score" field, or 0.0 if
  # that field is missing or the blob doesn't parse at all.
  python3 -c "
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get('score', 0.0))
except Exception:
    print(0.0)
" "$1"
}

PROG_JSON=$(python3 "$TASK_DIR/tests/check_programmatic.py" "$AGENT_RESULTS_DIR" "$TASK_DIR/solution" 2>/dev/null) || PROG_JSON='{"score": 0.0}'
PROG_SCORE=$(extract_score "$PROG_JSON")

JUDGE_JSON=$(python3 "$TASK_DIR/tests/llm_judge.py" "$TASK_DIR" "$AGENT_RESULTS_DIR" 2>/dev/null) || JUDGE_JSON='{"score": 0.0}'
JUDGE_SCORE=$(extract_score "$JUDGE_JSON")

REWARD=$(python3 -c "print(round($PROG_WEIGHT*$PROG_SCORE + $JUDGE_WEIGHT*$JUDGE_SCORE, 4))" 2>/dev/null) || REWARD="0.0"

echo "$REWARD" > "$AGENT_RESULTS_DIR/reward.txt"
echo "programmatic_score=$PROG_SCORE judge_score=$JUDGE_SCORE reward=$REWARD"
