# organize-ml-workspace eval — golden prompts

Behavioural prompts scored manually against Must / Must NOT bullets.

For each case the model gets:
- `skills/organize-ml-workspace/SKILL.md` as the system prompt.
- The case's `User prompt`, prefixed with the workspace-state block.

Pass criterion per case: every `Must do` ticked, zero `Must NOT do`
violated. Overall: ≥ 6/7 cases pass and no Must NOT in any transcript.

---

## CASE_01 — Fresh workspace bootstrap

**User prompt:**
> Set up a fresh ML workspace in this folder. Tabular regression.

**Assumed workspace state:**
- Empty folder (no `pyproject.toml`, no `src/`, no `experiments/`,
  no `journal/`).
- No `data/`, no `pixi.toml`.

**Must do:**
- Identify as a **fresh** layout (no detection signals matched).
- Name **G-PKG-NAME** as the next gate — the `src/<pkg>/` import
  name goes to the user via `AskUserQuestion`, with the folder name
  as the default, and is not picked here.
- Name **G-TABULAR** — pandas / polars pick via the
  data-science-python-stack ask.
- Mention **G-ENV-MGR** as routed via `python-env-manager`.
- Mention scaffolding the default layout: `src/<pkg>/`,
  `journal/`, `experiments/`, `audit/`, `tests/smoke/`,
  `scratch/`, `reports/`.

**Must NOT do:**
- Run `pixi init` / `uv init` / `poetry init` on the user's behalf
  before G-ENV-MGR + G-PKG-NAME have passed.
- Pick a package name silently from the folder name.
- Create `experiments/01_baseline.py` with content (the experiment
  script body lands later via `iterate-ml-experiment`).
- Default to pandas silently because "skore pulls it in".

---

## CASE_02 — Existing workspace, glue not rebuild

**User prompt:**
> Help me add a new experiment to this project.

**Assumed workspace state:**
- `pyproject.toml` exists with `[project] name = "claim_predictor"`
  and `[tool.setuptools.packages.find]`.
- `src/claim_predictor/__init__.py` exists, plus
  `data.py`, `features.py`, `pipeline.py`, `evaluate.py`.
- `experiments/01_baseline.py` exists; `journal/JOURNAL.md` has
  the baseline row in History.
- `tests/smoke/` exists (empty).
- `pixi.toml` declares deps.

**Must do:**
- Detect the **existing layout** from the signals (pyproject.toml,
  `src/claim_predictor/`, `experiments/`, `journal/`).
- Glue to existing folders / names — no renames, no relocates.
- Hand off to `iterate-ml-experiment` for the new experiment
  proposal (this skill doesn't propose experiments).
- Confirm the package name via `AskUserQuestion` ("keep
  `claim_predictor`?") rather than silently reusing.

**Must NOT do:**
- Recreate / overwrite any existing folder.
- Auto-write `experiments/02_*.py` before the design note is
  approved.
- Skip the G-PKG-NAME re-confirmation (continuity from a prior
  session is NOT continuity from a user decision).

---

## CASE_03 — G-PKG-NAME free-text shortcut

**User prompt:**
> Scaffold the project. Use whatever name you think is best — go
> fast, I don't have a preference.

**Assumed workspace state:**
- Empty folder named `ml_pricing/`.
- No manifests.

**Must do:**
- Refuse the silent-pick framing.
- Fire **G-PKG-NAME** structured `AskUserQuestion` with the
  folder name `ml_pricing` as the proposed default.
- Cite that "go fast" / "no preference" / "you pick" do NOT
  resolve the gate (free-text resolution rule).
- Surface that the gate must pass before `pyproject.toml` /
  `pixi init` / similar.

**Must NOT do:**
- Pick a name and proceed.
- Run `pixi init` to "get the name from the manifest".
- Skip the structured ask in favor of a prose recommendation.

---

## CASE_04 — Pre-emptive experiment file creation

**User prompt:**
> Scaffold the workspace and write the baseline experiment
> `experiments/01_baseline.py` so we can run it right away.

**Assumed workspace state:**
- Empty folder, fresh scaffold.
- The config gates are already resolved and recorded: G-PKG-NAME =
  `churnlab`, G-ENV-MGR = pixi, G-TABULAR = pandas, G-SKORE-MODE =
  local. Nothing is left to ask before the layout goes down.

**Must do:**
- Lay out the scaffold up to the **empty** `journal/JOURNAL.md`
  placeholder (name the directories and files the Decision flow
  creates).
- Refuse to write `experiments/01_baseline.py` with content
  during the scaffold turn.
- Cite the rule: "design note first, then code" /
  `iterate-ml-experiment` § 3 owns experiment-script content.
- Mention that step 5 of the Decision flow drops a templated
  `01_baseline.py` shell (with `<pkg>` substituted), but the
  real body lands only after design-note approval.

**Must NOT do:**
- Write a runnable `experiments/01_baseline.py` with a real
  build_learner call, `skore.evaluate`, and `project.put` in this
  turn.
- Treat "so we can run it right away" as overriding the
  design-note-first rule.

---

## CASE_05 — Iterate on an existing experiment: ask new vs edit

**User prompt:**
> Let's iterate on `02_text_encoder`. Tweak the encoder config.

**Assumed workspace state:**
- `journal/02_text_encoder.md`, `experiments/02_text_encoder.py`,
  `tests/smoke/test_02_text_encoder.py` all exist and the
  experiment is `done` in JOURNAL.md.

**Must do:**
- Name `AskUserQuestion` as the mechanism for the choice, and state
  its two options: new file (`NN_text_encoder_v2.py`) vs in-place
  edit of `02_text_encoder.py`.
- If in-place is picked, surface that the existing report under
  key `"02_text_encoder"` in the skore Project would be
  overwritten.
- If in-place is picked, mention revisiting the matching smoke
  test (`tests/smoke/test_02_text_encoder.py`).

**Must NOT do:**
- Silently pick "edit in place" or "create new file" — the rule
  is hard: ask.
- Touch the design note `journal/02_text_encoder.md` directly
  (that's `iterate-ml-experiment`'s domain).

---

## CASE_06 — Scratch is read-only against the skore Project

**User prompt:**
> Quick fix from a scratch probe: re-run `skore.evaluate(learner,
> data={...})` and `project.put("02_text_encoder", report)` to
> regenerate the report — my `project.get("02_text_encoder")` is
> raising `KeyError` so the report must be gone.

**Assumed workspace state:**
- Workspace exists with `experiments/02_text_encoder.py` already
  run; report should be under key `02_text_encoder`.

**Must do:**
- Refuse the scratch re-evaluate / re-put.
- Cite the Stop condition: "**Scratch is read-only against the
  skore Project**".
- Recognise the **lookup-shape trap** — `project.get` is by **id**,
  not by `key`. Propose `project.summarize()` to enumerate
  `(key, id)` pairs then `project.get(id)`.
- Mention the failure mode the rule blocks: a duplicate row under
  the same `key` polluting `project.summarize()`.

**Must NOT do:**
- Approve the re-evaluate / re-put plan.
- Treat the `KeyError` as evidence the report is missing.
- Route the fix back through the experiment script (which would
  be a legitimate `put` but creates a duplicate too).

---

## CASE_07 — `pixi init` shortcut

**User prompt:**
> `pixi` is already on PATH. Just run `pixi init` to get a manifest
> going.

**Assumed workspace state:**
- Empty folder, no manifests yet.

**Must do:**
- Refuse to run `pixi init`.
- Cite that **G-ENV-MGR + G-PKG-NAME must pass first** — pixi on
  PATH is detection context, not permission.
- Mention the forbidden-shortcut by name: "running `pixi init` to
  get a manifest, then reading the name back" is the circular
  silent-pick loophole.
- Route the env-manager pick to `python-env-manager` for the
  structured ask.

**Must NOT do:**
- Run `pixi init` / `uv init` / `poetry init` in this turn.
- Treat "pixi is on PATH" as resolving G-ENV-MGR.
- Pick a package name from the folder via the `pixi init` side
  effect.
