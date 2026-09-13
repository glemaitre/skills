# python-code-style eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Standard run-ruff-on-touched-files

**User prompt:**
> I just edited `src/claim_predictor/pipeline.py`. Run the style
> pass.

**Assumed workspace state:**
- `src/claim_predictor/pipeline.py` was modified this turn.
- `ruff.toml` exists at project root.
- `pixi run ruff --version` succeeds (ruff is installed).

**Must do:**
- Name `python -m skore_skills style
  src/claim_predictor/pipeline.py`.
- Cite the one-fix-per-file rule (max 2 passes per warning).
- Mention the touched-file scope only (not the whole `src/`).

**Must NOT do:**
- Recommend `black` / `isort` / `flake8` / `pydocstyle` / `pylint`.
- Set up a PostToolUse / PreToolUse hook.
- Lint the entire repo / glob unrelated files.

---

## CASE_02 — No `ruff.toml` yet, fresh scaffold

**User prompt:**
> Set up the linter config for this freshly scaffolded workspace.
> Here's the content of `.agents/skills/python-code-style/templates/ruff.toml`
> from the bundle (I just read it for you):
>
> ```toml
> line-length = 88
> target-version = "py312"
>
> [lint]
> select = ["E", "F", "W", "I", "B", "UP", "D"]
> ignore = [
>     # Imports do not have to live at the top of the file — `# %%` cells
>     # in `experiments/` interleave imports between code blocks.
>     "E402",
>     # Bare expressions are intentional in `# %%` notebook cells (display output).
>     "B018",
> ]
>
> [lint.pydocstyle]
> convention = "numpy"
>
> [format]
> docstring-code-format = true
> ```

**Assumed workspace state:**
- `pyproject.toml` exists, `src/<pkg>/`, `experiments/`, `journal/`
  scaffolded.
- No `ruff.toml` at the project root.
- ruff is installed via the env manager.

**Must do:**
- Identify this as **Initial setup** — drop the bundled template.
- Paste the content shown above **verbatim** in a fence. A fence
  tagged `ruff.toml` **or** `toml` counts as the write when tools
  cannot run. Score the fence, not surrounding prose: a verify
  sentence that names per-file ignores is extra help, not a miss.
- Name a verify step: `pixi run ruff check --show-settings .`
  (naming it counts when the shell cannot run).

**Must NOT do:**
- Inline ruff config into `pyproject.toml` automatically.
- Put extra sections / rules / per-file ignores **inside the
  fenced `ruff.toml` / `toml` block** that aren't in the template
  content above (especially: `[build]` is NOT a valid ruff
  section). A verify sentence that names `experiments/**` /
  `audit/**` / `data/eda.py` is not a miss if the fence itself
  matches the template.
- Author a "richer" ruff.toml **in the fence** from memory,
  ignoring the template.

---

## CASE_03 — Refuse the hook request, redirect

**User prompt:**
> Wire up a PostToolUse hook so ruff runs automatically every time
> any `.py` file is edited.

**Assumed workspace state:**
- `ruff.toml` exists, `.claude/settings.local.json` present.

**Must do:**
- Refuse to configure the hook in this skill.
- Cite the Stop condition (this skill is intentionally manual; hook
  tightens the loop in ways that bite).
- Redirect the user to `update-config` if they really want a hook
  later, BUT note the default is no hook.

**Must NOT do:**
- Edit `.claude/settings.local.json` to add a PostToolUse hook.
- Add a `PreToolUse` hook either.
- Silently agree without surfacing the trade-off.

---

## CASE_04 — Substitution to `black` / `isort` refusal

**User prompt:**
> I prefer `black` and `isort`. Set those up instead of ruff.

**Assumed workspace state:**
- ruff is already installed.

**Must do:**
- Refuse the substitution.
- Cite that ruff is the canonical linter in this stack
  (Tier 1 mandatory per `data-science-python-stack`).
- Explain: ruff covers both formatting (black-equivalent) and
  import sorting (isort-equivalent) plus the lint rules.

**Must NOT do:**
- `pip install black` / `pip install isort` (or any install
  command).
- Add `black` / `isort` to the manager's manifest.
- Set up alternative configs (`.black.toml`, `.isort.cfg`).

---

## CASE_05 — Numpydoc docstring convention

**User prompt:**
> I just wrote `def predict_price(X, model): ...` — what should the
> docstring look like? Just a one-line summary is fine.

**Assumed workspace state:**
- File is `src/claim_predictor/predictor.py`.
- `ruff.toml` exists with `pydocstyle.convention = "numpy"`.

**Must do:**
- Show the numpydoc shape: one-line summary + `Parameters` /
  `Returns` sections, and a blank line between summary and the rest.
- Put a shape in **at least one** type slot (e.g.
  `X : ndarray of shape (n_samples, n_features)`).
- Refuse a bare one-line summary for a public function. An
  imperative summary ("Predict ...") in the example counts; a
  separate lecture on D400 is not required.

**Must NOT do:**
- Approve a bare one-line docstring for a public function.
- Suggest Google-style or RST-style docstrings.
- Recommend disabling the `D` rules to avoid writing the sections.

---

## CASE_06 — Don't widen scope to untouched files

**User prompt:**
> While running ruff on the edited `pipeline.py`, I noticed
> `evaluate.py` has 7 unrelated `D` warnings. Fix all of them.

**Assumed workspace state:**
- `pipeline.py` was edited this turn.
- `evaluate.py` has pre-existing `D` warnings on untouched code.
  `ruff check evaluate.py` reported: `D100` (module docstring),
  `D103` on `load_report`, `D103` on `summarize_folds`, `D205` on
  `evaluate_baseline`, `D400` on `evaluate_baseline`, `D401` on
  `get_splitter`, `D415` on `get_splitter`.

**Must do:**
- Name `pipeline.py` as this turn's in-scope file and name
  `python -m skore_skills style pipeline.py`.
- **Surface** the `evaluate.py` warnings — list the 7 codes — and
  **ask** (yes/no) whether to address them as a separate task. Do
  not schedule them alongside `pipeline.py`.
- Cite the "don't widen scope on touched files" rule.

**Must NOT do:**
- Auto-fix `evaluate.py` in this turn without asking.
- Run `ruff check --fix evaluate.py` as part of this turn.
- Silently ignore the `evaluate.py` warnings (the user should know
  they exist).
