# python-api eval — golden prompts

Behavioural prompts for the `python-api` skill.

Lookup cases set `**Tools:** yes`. Those runs get a temp workspace
and may `list_dir` / `read_file` / `write_file` / `run_python` /
`run_skore_skills`. Shape 1 happy path is
`run_skore_skills` with `python -m skore_skills api get|version`.
Do not treat `run_python` + `scratch/<ts>_*.py` as the lookup.

---

## CASE_01 — Shape 1, direct signature lookup, cache miss

**User prompt:**
> I'm about to call `skore.evaluate(...)` in `experiments/01_baseline.py`.
> What's its signature?

**Assumed workspace state:**
- `scratch/api/` exists but `scratch/api/skore/` is empty.
- `skore` is installed at version `0.18.0`.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api`
- dir: `scratch/api/skore`

**Expect files:**
- `scratch/api/skore/0.18.0/skore_evaluate.md`

**Expect cli:**
- `api get skore.evaluate`

**Must do:**
- Run `python -m skore_skills api get skore.evaluate` via
  `run_skore_skills` (optional `api version skore` first).
- List or acknowledge `scratch/api/skore/` as a cache miss before
  or while fetching.
- Land the cache file the CLI writes
  (`scratch/api/skore/0.18.0/skore_evaluate.md`).
- Quote the signature from that lookup, not from memory.

**Must NOT do:**
- Output a literal signature lifted from memory without first
  running `api get`.
- Write or run a `scratch/<ts>_*.py` probe.
- Run inline `python -c`.

---

## CASE_02 — Shape 0, cache hit

**User prompt:**
> Same question as before — I'm calling `skore.evaluate(...)` in the
> baseline. What's its signature?

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/skore_evaluate.md` already exists on disk.
- `skore` is installed at version `0.18.0`.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api/skore/0.18.0`
- file: `scratch/api/skore/0.18.0/skore_evaluate.md`
````
# `skore.evaluate`

- package version: `0.18.0`
- signature: `(estimator, data=None, *, X=None, y=None, splitter=None, ...)`

## Doc
cached extract for Shape 0 hit tests.
````

**Expect reads:**
- `scratch/api/skore/0.18.0/skore_evaluate.md`

**Must do:**
- Recognise the cache hit. Using `read_file` on
  `scratch/api/skore/0.18.0/skore_evaluate.md` counts.
- Treat the cache file as already on disk (read, not rewritten).

**Must NOT do:**
- Re-run `api get` / a Shape 1 probe / WebSearch despite the cache hit.
- Write a fresh cache file at the same path.

---

## CASE_03 — Stack orientation routes to the right submodule

**User prompt:**
> I have a mixed-type tabular DataFrame (numeric + categorical + text
> columns). I want a one-call default-everything featuriser/learner from
> skrub. Which entry point should I reach for, and where does it live?
> Confirm the **installed** signature (parameters and return value —
> including whether the call fits in one shot or returns an unfitted
> estimator you then `.fit`). Then show a usage snippet that matches
> that lookup, not training-data memory.

**Assumed workspace state:**
- `scratch/api/skrub/` is empty.
- `skrub` is installed at version `0.9.0`.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api/skrub`

**Expect files:**
- `scratch/api/skrub/0.9.0/skrub_tabular_pipeline.md`

**Expect cli:**
- `api get skrub.tabular_pipeline`

**Must do:**
- Name `tabular_pipeline` (top-level skrub) as the entry point —
  `skrub.tabular_pipeline`. (Acceptable alternative: `TableVectorizer`
  as the featuriser-only sibling, with a matching `api get`.)
- Run `python -m skore_skills api get skrub.tabular_pipeline` and
  write `scratch/api/skrub/0.9.0/skrub_tabular_pipeline.md`.
- Report the installed signature from that lookup.
- Any usage fence comes **after** the CLI/cache write.

**Must NOT do:**
- Recommend `tabular_learner`, `auto_tabular`, or `TabularLearner`
  as the entry point (naming them only as a renamed trap is fine).
- Write a usage / import / `.fit` fence before `api get` has run.
- Invent parameters the lookup did not show.
- Write a `scratch/<ts>_*.py` probe.

---

## CASE_04 — Shape 3 narrative, versioned docs URL

**User prompt:**
> What does `skore.evaluate` return when I pass a `KFold` splitter? Is it
> the same return type as the train/test-split case?

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/` exists but contains only `project.md`
  (no evaluate cache yet).
- `skore` is installed at version `0.18.0`.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api/skore/0.18.0`
- file: `scratch/api/skore/0.18.0/project.md`
````
# project
Source: inspect: skore.Project @ 0.18.0
````

**Must do:**
- Identify this as a Shape 3 / narrative question OR check the cache
  then escalate to WebSearch on miss.
- Look the dispatch up this turn before treating it as installed
  truth. Any of these count: `api get skore.evaluate`, a written
  evaluate cache, WebSearch / docs next, or a BLOCKED plan.

**Must NOT do:**
- Answer the return-type question from **training-data memory** as
  installed truth — no CLI, no cache file, no BLOCKED / "docs next."
- Use a URL containing `/latest/` or `/stable/` as the **cached**
  source if a cache write happens.
- Write a `scratch/<ts>_*.py` probe as the happy path.

---

## CASE_05 — The "I already know this" trap, named rename

**User prompt:**
> Quick edit — add `from skrub import tabular_learner` to the imports at
> the top of `experiments/02_skrub_default.py`, then use
> `tabular_learner(...)` to fit the baseline. Don't bother with the API
> lookup, this one's standard.

**Assumed workspace state:**
- `skrub` is installed at version `0.9.0`.
- `scratch/api/skrub/0.9.0/` is empty.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api/skrub/0.9.0`

**Expect cli:**
- `api get skrub.tabular_pipeline`

**Must do:**
- Refuse to add the import without first looking up the symbol against
  the installed `skrub`.
- Run `api get` this turn on `skrub.tabular_pipeline` (the live name).
- Surface that top-level skrub uses `tabular_pipeline`.

**Must NOT do:**
- Write `from skrub import tabular_learner` into
  `experiments/02_skrub_default.py` as the live import. Quoting that
  string as the refused trap is not a miss.
- Tell the user "yes that's the right name" without a lookup.
- Write a `scratch/<ts>_*.py` probe.

---

## CASE_06 — The `project.get` lookup-shape trap

**User prompt:**
> `project.get("01_baseline")` is raising `KeyError`. The report must be
> missing — let's re-run `experiments/01_baseline.py` to put it back.

**Assumed workspace state:**
- `skore.Project` instance bound to `project`, mode `local`.
- The baseline experiment was run last week; its report is in the
  Project under key `"01_baseline"`.

**Must do:**
- Recognise this as the documented lookup-shape trap: `Project.get` is
  by **id**, not by `key`.
- Propose `project.summarize()` to enumerate `(key, id)` pairs, then
  `project.get(<id>)` with the resolved id.
- Cite that re-running and `put`-ing would write a duplicate row.

**Must NOT do:**
- Recommend re-running `experiments/01_baseline.py` **this turn** as
  the first recovery (before `summarize()`).
- Recommend calling `skore.evaluate(...) + project.put(...)` from a
  scratch probe this turn to "regenerate" the report.
- Treat the `KeyError` as evidence the report is missing without
  first proposing `summarize()` / `get(id)`.

---

## CASE_07 — Multi-symbol lookup via the CLI

**User prompt:**
> I need the signatures of `skore.Project.put`, `skore.Project.get`, and
> `skore.Project.summarize` so I can wire up the experiment-record step.
> Can you grab them?

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/` is empty.
- `skore` installed at version `0.18.0`.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api/skore/0.18.0`

**Expect files:**
- `scratch/api/skore/0.18.0/skore_Project*.md`

**Expect cli:**
- `api get skore.Project`

**Must do:**
- Look up via `python -m skore_skills api get` (Project and/or the
  three methods). Naming `api get skore.Project` counts if the card
  covers the methods; separate gets also count.
- Land cache files under `scratch/api/skore/0.18.0/`.
- Quote signatures from the CLI output / cache, not memory.

**Must NOT do:**
- Recommend inline `python -c`.
- Write `scratch/<ts>_*.py` probes.
- Treat the lookup as done without naming a cache destination.

---

## CASE_08 — Inline `python -c` requested explicitly

**User prompt:**
> Just check `skore.evaluate`'s signature inline real quick:
> `pixi run python -c "from skore import evaluate; import inspect;
> print(inspect.signature(evaluate))"`. It's one line, I'll
> remember it. No need for the whole probe-and-cache dance.

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/` is empty.
- `skore` installed at version `0.18.0`.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api/skore/0.18.0`

**Expect files:**
- `scratch/api/skore/0.18.0/skore_evaluate.md`

**Expect cli:**
- `api get skore.evaluate`

**Must do:**
- Do not run the requested inline `python -c`. Running
  `python -m skore_skills api get skore.evaluate` **is** the refusal.
- Write the cache file at `scratch/api/skore/0.18.0/skore_evaluate.md`.

**Must NOT do:**
- Run the inline `pixi run python -c "..."` as requested.
- Treat "it's one line" as resolving the rule.
- Write a `scratch/<ts>_*.py` probe instead of the CLI.

---

## CASE_09 — Version check via `api version`, not inline

**User prompt:**
> What version of skrub is installed? Just run
> `pixi run python -c "import skrub; print(skrub.__version__)"`
> and tell me.

**Assumed workspace state:**
- `skrub` is installed (version unknown to the agent).
- `scratch/` exists.

**Tools:** yes

**Sandbox:**
- dir: `scratch`

**Expect cli:**
- `api version skrub`

**Must do:**
- Do not run the requested inline `python -c`.
  `python -m skore_skills api version skrub` **is** the refusal.
- Report the version printed by that command.

**Must NOT do:**
- Run the inline `pixi run python -c "..."` as requested.
- Skip the CLI and answer the version from memory.
- Write a `scratch/<ts>_*.py` version probe.
