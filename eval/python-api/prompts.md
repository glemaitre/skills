# python-api eval — golden prompts

Behavioural prompts for the `python-api` skill, scored manually by reading
each transcript against the **Must / Must NOT** bullets per case.

## How a case is scored

For each case the model is given:
- `skills/python-api/SKILL.md` as the system prompt.
- The case's `User prompt` (verbatim) as the user message.
- The case's `Assumed workspace state` is appended to the user message as a
  short preamble like:

  ```
  [Workspace state — read but do not narrate back: <state goes here>]

  <user prompt>
  ```

  This avoids depending on the model actually running `ls` — we hand the
  filesystem snapshot in so the test isolates skill-knowledge from tool-use.

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

**Must do:**
- Reference resolving the installed version (mention
  `pixi run python -c "import skore; print(skore.__version__)"`
  or equivalent).
- Reference listing `scratch/api/skore/0.18.0/` for a cache hit before
  any fresh probe.
- Propose writing a probe script under `scratch/<ts>_*.py` (not an inline
  `python -c`).
- Name `pydoc.render_doc` (not `__doc__`) for capturing the help text.
- Name the cache file destination as `scratch/api/skore/0.18.0/evaluate.md`.
- Reference the four-section file contract (Source / Signature / help() /
  Usage) at least implicitly — i.e. mention writing Signature + help()
  sections + a Usage block to fill in.

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

**Must do:**
- Recognise the cache hit and propose `Read scratch/api/skore/0.18.0/evaluate.md`
  as the next action.
- Mark the pre-flight `Cache file lands on disk` row as
  `n/a — cache hit, file already on disk` (or equivalent phrasing).

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

**Assumed workspace state:**
- `scratch/api/skrub/` is empty.
- `skrub` is installed at version `0.9.0`.

**Must do:**
- Name `tabular_pipeline` (top-level skrub) as the entry point — i.e.
  `skrub.tabular_pipeline`. (Acceptable alternative: name
  `TableVectorizer` as the featuriser-only sibling.)
- After naming the symbol, propose a Shape 1 probe to confirm the
  signature against the installed version before writing the call.
- Mention the cache write at `scratch/api/skrub/0.9.0/tabular_pipeline.md`.

**Must NOT do:**
- Invent a name like `tabular_learner`, `auto_tabular`, or
  `TabularLearner` from memory.
- Recommend writing code with the symbol before running the Shape 1
  probe.

---

## CASE_04 — Shape 3 narrative, versioned docs URL

**User prompt:**
> What does `skore.evaluate` return when I pass a `KFold` splitter? Is it
> the same return type as the train/test-split case?

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/` exists but contains only `project.md`
  (no `evaluate.md` yet).
- `skore` is installed at version `0.18.0`.

**Must do:**
- Identify this as a Shape 3 / narrative question (signatures alone do
  not answer "is the return type the same") OR explicitly check the
  cache first then escalate to WebSearch on miss.
- Propose a WebSearch query that includes the version, like
  `skore 0.18 docs evaluate splitter` (the major.minor pattern).
- Propose WebFetch of a URL containing `/0.18/` or `/0.18.0/` — not
  `/latest/`.
- Cache the result at `scratch/api/skore/0.18.0/evaluate.md` with the
  source URL on the first line.

**Must NOT do:**
- Answer the return-type question from memory without a fetch.
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

**Must do:**
- Refuse to add the import without first looking up the symbol against
  the installed `skrub`.
- Cite the "Recognition is not a lookup" principle (or equivalent — the
  rule that training-data memory does not count as a lookup).
- Propose a Shape 1 probe (or at minimum a Shape 2 `dir(skrub)`) to
  confirm whether `tabular_learner` exists at the installed version.
- Surface the named-trap context: top-level skrub uses `tabular_pipeline`
  (per the skill's stack-orientation section).

**Must NOT do:**
- Add the import as instructed.
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
- Recommend re-running `experiments/01_baseline.py`.
- Recommend calling `skore.evaluate(...) + project.put(...)` from a
  scratch probe to "regenerate" the report.
- Treat the `KeyError` as evidence the report is missing.

---

## CASE_07 — Multi-symbol consolidation, no inline-python-c spam

**User prompt:**
> I need the signatures of `skore.Project.put`, `skore.Project.get`, and
> `skore.Project.summarize` so I can wire up the experiment-record step.
> Can you grab them?

**Assumed workspace state:**
- `scratch/api/skore/0.18.0/` is empty.
- `skore` installed at version `0.18.0`.

**Must do:**
- Write **one** probe script under `scratch/<ts>_*.py` that iterates
  over the three dotted paths and consolidates their Signature + help()
  sections.
- Produce **one** cache file at
  `scratch/api/skore/0.18.0/project_local.md` (or `project.md`) covering
  all three symbols under one topic.
- Mention the multi-symbol-consolidation rule (one topic file per
  topic, not per symbol).

**Must NOT do:**
- Recommend three separate inline `pixi run python -c "..."` calls.
- Recommend ANY inline `python -c` (rule is unconditional now —
  see Stop conditions, no length carve-out).
- Write three separate cache files (`put.md`, `get.md`, `summarize.md`).
- Skip the cache write entirely (treat the probe as the conclusion).

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

**Must do:**
- Refuse the inline `python -c` invocation.
- Cite the **Stop condition** that all Python execution goes to
  `scratch/` regardless of length (the "no inline `python -c`,
  no exceptions" rule).
- Cite that `inspect.signature(...)` run inline is NOT a
  python-api consultation — the deliverable is a
  `scratch/api/skore/0.18.0/evaluate.md` cache file.
- Propose the Shape 1 probe template instead, writing
  `scratch/<ts>_lookup_skore_evaluate.py` that produces the cache
  file in one execution.

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

**Must do:**
- Refuse the inline `python -c`.
- Cite the "all Python execution goes to scratch" Stop condition
  — version checks are explicitly enumerated in the rule.
- Propose writing `scratch/<ts>_version_skrub.py` with
  `import skrub; print(skrub.__version__)` and running it via
  `pixi run python scratch/<ts>_version_skrub.py`.
- Confirm: even a one-line version check produces a scratch file.

**Must NOT do:**
- Run the inline `pixi run python -c "..."` as requested.
- Treat the version check as "trivial enough to inline".
- Skip the file entirely and answer the version from memory.
