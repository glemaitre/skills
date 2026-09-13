# python-api eval — golden prompts

Behavioural prompts for the `python-api` skill, scored manually by reading
each transcript against the **Must / Must NOT** bullets per case.

## How a case is scored

For each case the model is given:
- `skills/python-api/SKILL.md` as the system prompt.
- The case's `User prompt` (verbatim) as the user message.
- The case's `Assumed workspace state` is appended to the user message as a
  short preamble.

Lookup cases set `**Tools:** yes`. Those runs get a real temp workspace
(seeded from `**Sandbox:**`) and may `list_dir` / `read_file` /
`write_file` / `run_python` (scratch files only). Other skills stay
single-turn with no tools unless a case opts in (see
`build-ml-pipeline` case 3). When tools are off, workspace state is
inlined so the test does not depend on `ls`.

Each `Must do` and `Must NOT do` bullet is a substring / behavioural check
on the transcript. Read the transcript top-to-bottom, tick boxes, flag any
miss.

Pass criterion per case: every `Must do` ticked, zero `Must NOT do`
violated. Pass criterion overall: ≥ 6 / 7 cases pass and no `Must NOT do`
violation appears in any transcript (the latter is the hard rule — a
violation means a regression has snuck in).

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
- `scratch/api/skore/0.18.0/evaluate.md`

**Must do:**
- Resolve the installed version via a scratch file (not inline
  `python -c`).
- List `scratch/api/skore/` (cache **miss** is correct — empty or
  missing `0.18.0/` until the probe writes it). Then run a probe.
- Write and run a probe script under `scratch/<ts>_*.py` (not an
  inline `python -c`).
- Use `pydoc.render_doc` (not `__doc__`) for capturing the help text.
- Write the cache file at `scratch/api/skore/0.18.0/evaluate.md`.
- Mention Signature + help() and a Usage block (four-section contract
  at least implicitly).

**Must NOT do:**
- Output a literal signature like
  `def evaluate(estimator, X=None, y=None, ...)` lifted from memory
  without first running the probe.
- Use `__doc__` to capture documentation.
- Recommend an inline `pixi run python -c "..."` that spans more than 2
  lines.
- Skip the cache-list step and jump straight to the probe.

---

## CASE_02 — Shape 0, cache hit

**User prompt:**
> Same question as before — I'm calling `skore.evaluate(...)` in the
> baseline. What's its signature?

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/evaluate.md` already exists on disk (written
  yesterday).
- `skore` is installed at version `0.18.0`.

**Tools:** yes

**Sandbox:**
- dir: `scratch/api/skore/0.18.0`
- file: `scratch/api/skore/0.18.0/evaluate.md`
````
# evaluate

Source: inspect: skore.evaluate @ 0.18.0
Fetched: 2026-09-11

## Signature
evaluate(estimator, data=None, *, X=None, y=None, splitter=None, ...)

## help()
skore.evaluate — cached extract for Shape 0 hit tests.

## Usage
Call: skore.evaluate(learner, data={...}, splitter=...)
Don't call: positional X, y on a SkrubLearner
Trap: none
Returns: a report object (see cached help)
````

**Must do:**
- Recognise the cache hit. Using `read_file` on
  `scratch/api/skore/0.18.0/evaluate.md` counts; naming `Read` in
  the message also counts.
- Treat the cache file as already on disk (read, not rewritten).
  The pre-flight `n/a — cache hit, file already on disk` phrasing
  is sufficient. So is a cache-hit answer that `read_file`s that
  path and does not `write_file` it — do not require the exact
  pre-flight sentence.

**Must NOT do:**
- Re-run a Shape 1 probe / re-fetch / re-WebSearch despite the cache hit.
- Write a fresh cache file at the same path (would overwrite the
  existing synthesis).

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
- `scratch/api/skrub/0.9.0/tabular_pipeline.md`

**Must do:**
- Name `tabular_pipeline` (top-level skrub) as the entry point — i.e.
  `skrub.tabular_pipeline`. (Acceptable alternative: name
  `TableVectorizer` as the featuriser-only sibling.)
- Run a Shape 1 probe (`scratch/<ts>_*.py` + `pydoc.render_doc`)
  against the installed skrub and write
  `scratch/api/skrub/0.9.0/tabular_pipeline.md`.
- Report the installed signature (args / return) **from that lookup**.
- Any usage fence comes **after** the probe/cache write and matches
  the looked-up signature.

**Must NOT do:**
- Recommend `tabular_learner`, `auto_tabular`, or `TabularLearner`
  as the entry point (naming them only as a renamed trap is fine).
- Write a usage / import / `.fit` fence before the Shape 1 probe has
  run.
- Invent parameters the probe did not show (e.g. a `target_column=`
  argument that is not in the installed signature).

---

## CASE_04 — Shape 3 narrative, versioned docs URL

**User prompt:**
> What does `skore.evaluate` return when I pass a `KFold` splitter? Is it
> the same return type as the train/test-split case?

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/` exists but contains only `project.md`
  (no `evaluate.md` yet).
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
- Identify this as a Shape 3 / narrative question (signatures alone do
  not answer "is the return type the same") OR explicitly check the
  cache first then escalate to WebSearch on miss.
- Propose a WebSearch query that includes the version, like
  `skore 0.18 docs evaluate splitter` (the major.minor pattern).
- State that the WebFetch target must be a version-pinned docs URL —
  a path carrying `/0.18/` or `/0.18.0/` — and that `/latest/` or
  `/stable/` is rejected.
- Name the cache destination `scratch/api/skore/0.18.0/evaluate.md`
  and state that the source URL goes on its first line.

**Must NOT do:**
- Answer the return-type question from memory as a **fact** (assert
  which type is returned, or that KFold vs holdout are the same /
  different). A BLOCKED plan that names `/0.18/` and
  `scratch/api/skore/0.18.0/evaluate.md` is not a violation. A class
  name used only as an example of what the cache will enumerate is
  not a violation.
- Use a URL containing `/latest/` or `/stable/` as the cached source.
- Paraphrase the docs into the cache file (the cache should hold a
  verbatim extract).

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

**Must do:**
- Refuse to add the import without first looking up the symbol against
  the installed `skrub`.
- Cite "Recognition is not a lookup" **or equivalent** (training-data
  memory / "I already know this" does not count as a lookup this
  turn). Do not require that exact slogan.
- Run a Shape 1 probe this turn. Probing `tabular_pipeline` (the
  live name) counts; do not require a second probe of
  `tabular_learner` / `dir(skrub)` for the dead name.
- Surface the named-trap context: top-level skrub uses
  `tabular_pipeline`.

**Must NOT do:**
- Add `from skrub import tabular_learner` (the instructed import).
  Naming `tabular_pipeline` as a lead plus a Shape 1 probe is
  required, not a violation.
- Tell the user "yes that's the right name" without a lookup.

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
- Cite the "Never substitute by re-creating the artifact" rule (or
  equivalent — re-running and `put`-ing would write a duplicate row).

**Must NOT do:**
- Recommend re-running `experiments/01_baseline.py` **this turn** as
  the first recovery (before `summarize()`). Mentioning a later
  re-run **if** `summarize()` has no `"01_baseline"` row is
  allowed.
- Recommend calling `skore.evaluate(...) + project.put(...)` from a
  scratch probe this turn to "regenerate" the report.
- Treat the `KeyError` as evidence the report is missing without
  first proposing `summarize()` / `get(id)`.

---

## CASE_07 — Multi-symbol consolidation, no inline-python-c spam

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
- `scratch/api/skore/0.18.0/project*.md`

**Must do:**
- Write **one** probe script under `scratch/<ts>_*.py` that iterates
  over the three dotted paths and consolidates their Signature + help()
  sections.
- Write **one** cache file at
  `scratch/api/skore/0.18.0/project_local.md` (or `project.md`) covering
  all three symbols under one topic.
- Mention the multi-symbol-consolidation rule (one topic file per
  topic, not per symbol).

**Must NOT do:**
- Recommend three separate inline `pixi run python -c "..."` calls.
- Recommend ANY inline `python -c` (rule is unconditional now —
  see Stop conditions, no length carve-out).
- Write three separate cache files (`put.md`, `get.md`, `summarize.md`).
- Treat the probe as the conclusion without naming a cache
  destination. Naming `scratch/api/skore/0.18.0/project_local.md`
  (or `project.md`) as the destination is required; the file should
  land this turn.

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
- `scratch/api/skore/0.18.0/evaluate.md`

**Must do:**
- Do not run the requested inline `python -c`. Writing and running a
  `scratch/<ts>_*.py` probe via `run_python` **is** the refusal.
- Cite the **Stop condition** that all Python execution goes to
  `scratch/` regardless of length, **or** show that this turn only
  executed a scratch file (no `python -c`).
- Write the cache file at `scratch/api/skore/0.18.0/evaluate.md`.
- Write any `scratch/<ts>_*.py` that writes that cache file in
  one run (the exact probe basename is not load-bearing).

**Must NOT do:**
- Run the inline `pixi run python -c "..."` as requested.
- Treat "it's one line" / "I'll remember it" as resolving the
  rule. The rule is unconditional; length isn't the criterion.
- Recommend Shape 1a as a carve-out (Shape 1a is removed).

---

## CASE_09 — Version check goes to scratch, not inline

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

**Expect files:**
- `scratch/*version*skrub*.py`

**Must do:**
- Do not run the requested inline `python -c`. A scratch file plus
  `run_python` **is** the refusal.
- Cite the "all Python execution goes to scratch" Stop condition
  (version checks included), **or** show that this turn only ran a
  scratch file.
- Write a scratch file under `scratch/` that prints `skrub.__version__`
  (name may be `scratch/<ts>_version_skrub.py` or similar) and run it
  via `run_python` (not `python -c`).
- Confirm: even a one-line version check produces a scratch file.
  Report the version printed by that script.

**Must NOT do:**
- Run the inline `pixi run python -c "..."` as requested.
- Treat the version check as "trivial enough to inline".
- Skip the file entirely and answer the version from memory.
