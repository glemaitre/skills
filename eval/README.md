# Skill evaluations

Single-turn behavioural evals for each skill: the **target** model sees
`SKILL.md` as its system prompt (or an empty system, for the baseline)
and answers a golden prompt. A **judge** model scores the Must / Must NOT
expectations via DeepEval `GEval`.

This is an instruction-following check, not a real agent loop. The
target has no tools and does not `Read` `references/`; workspace state
is inlined in the prompt. Every user message ends with a harness note
telling the model to answer in one turn and not emit tool calls.

## Scoring

Expectations from `prompts.md` are split on the prefix
`The response does NOT`:

- **Must-do** is a non-strict GEval with partial credit. The default
  pass threshold is `0.7` (`SKILL_EVAL_PASS_RATIO`): a minor miss no
  longer fails the case. Most cases carry 3-4 Must-do expectations,
  so `0.7` buys exactly one item of tolerance; at `0.8` the ceiling
  rounds that away and the metric is all-or-nothing again.
- **Must-NOT** stays all-or-nothing (`threshold=1.0`, `strict_mode`).
  Any prohibition violated fails the case.

A failing node prints both scores, each judge reason, the grouped
expectations, the full target response, and paths to the JSON and
Markdown transcripts.

## Authoring cases

1. Edit `eval/<skill>/prompts.md` (`CASE_NN`, user prompt, workspace
   state, Must do / Must NOT).
2. Regenerate the skill-creator schema file:

```bash
python3 eval/convert_to_evals_json.py              # every skill with prompts.md
python3 eval/convert_to_evals_json.py python-api   # named skills only
python3 eval/convert_to_evals_json.py --check      # fail if evals.json is stale
```

That writes `skills/<skill>/evals/evals.json`.

## Setup

Secrets go in a gitignored `.env`. Model ids are set on the pixi eval
environment (`feature.eval.activation.env` in `pixi.toml`).

```bash
cp .env.example .env   # set OPENROUTER_API_KEY
pixi install -e eval
```

The optional `eval` pixi environment is separate from catalog CI
(`pixi run check`). Evals themselves are not run in GitHub Actions, but
`pixi run check` now includes `evals-check` so a stale `evals.json` fails
CI.

The eval task runs pytest with `-n auto`. Transcripts for one session
share a single `.transcripts/<run-id>/` directory across workers.

DeepEval's 180s per-task timeout is disabled (`DEEPEVAL_DISABLE_TIMEOUTS`).
Target generation uses `temperature=0` and a 600s LiteLLM transport
timeout so a hung socket still fails and retries.

Defaults (override in `pixi.toml` or on the CLI):

- **Tiers** (`SKILL_EVAL_TIER=assigned`): each skill runs on one model
  - small — `openrouter/qwen/qwen3.7-flash`: `test-ml-pipeline`,
    `python-code-style`
  - medium — `openrouter/deepseek/deepseek-v4.1-flash`:
    `organize-ml-workspace`, `python-env-manager`,
    `data-science-python-stack`, `evaluate-ml-pipeline`,
    `smoke-test-ml-pipeline`, `iterate-from-skore`, `iterate-from-user`
    (and, when they gain evals, `explore-ml-data`, `audit-ml-pipeline`)
  - big — `openrouter/minimax/minimax-m2.7`: `iterate-ml-experiment`,
    `python-api`, `build-ml-pipeline`
- judge: `openrouter/deepseek/deepseek-v4.1-flash` (not tiered)
- mode: `with` (SKILL.md as system prompt)
- Must-do pass ratio: `0.7` (Must-NOT is always all-or-nothing)

`--skill-tier all` runs every skill on all three models (79 x 3).
`--skill-tier small|medium|big` keeps only skills assigned to that
tier. `--skill-model` / `SKILL_EVAL_MODELS` ignore the table and pin
every collected case to the given model(s).

LiteLLM names are `openrouter/<vendor>/<model>`. Native `openai/...` or
`anthropic/...` ids still work if you change the pixi env vars and set
the matching key in `.env`.

## Run

```bash
# One skill, pixi defaults
pixi run -e eval eval -- -k python-api

# One case (node ids are `{skill}-case{N}-{title-slug}-{mode}-{model}`)
pixi run -e eval eval -- -k 'python-api and case1'

# All skills, each on its assigned tier (~79 nodes)
pixi run -e eval eval

# Only the big-tier skills (MiniMax)
pixi run -e eval eval -- --skill-tier big

# Full matrix: every skill x small/medium/big
pixi run -e eval eval -- --skill-tier all

# Ignore the table and pin one model
pixi run -e eval eval -- \
  --skill-model openrouter/deepseek/deepseek-v4.1-flash \
  --skill-judge-model openrouter/deepseek/deepseek-v4.1-flash \
  --skill-mode both \
  --skill-pass-ratio 0.7 \
  -k python-api
```

A failing node prints per-group GEval scores (Must-do / Must-NOT), each
judge reason, the grouped expectations, the full target response, and
paths to JSON and Markdown transcripts. LiteLLM errors keep their
traceback. The session summary lists failed `(skill, case, title)` rows.

Transcripts are written even when the visible reply is empty (reasoning
models sometimes fill `reasoning_content` only). They land under
`.transcripts/<run-id>/<skill>/` and are gitignored. Each case
writes a `.json` payload and a sibling `.md` with the prompt, grouped
expectations, `finish_reason` / `judged_from` / usage, the raw reply,
and each metric's score and reason. If `content` is empty, GEval judges
`reasoning_content` instead (`judged_from` in the JSON).

Target generation does **not** set `max_tokens`, so reasoning + answer
are not cut off at 4096.

Equivalent environment variables (CLI flags win): `SKILL_EVAL_TIER`
(`assigned` / `all` / `small` / `medium` / `big`), `SKILL_EVAL_TIER_SMALL`
/ `_MEDIUM` / `_BIG`, `SKILL_EVAL_MODELS` (comma-separated override;
ignores the tier table), `SKILL_EVAL_JUDGE_MODEL`, `SKILL_EVAL_MODE`
(`with` / `without` / `both`), `SKILL_EVAL_PASS_RATIO` (Must-do
threshold). Shell env vars win over `.env`.

`--skill-mode both` prints a pass-rate delta (with minus without) in the
pytest summary.
