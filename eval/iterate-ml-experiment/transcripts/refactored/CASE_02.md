# CASE_02 — Propose next (sourcing menu)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/iterate-ml-experiment/SKILL_v2.md` (575 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/JOURNAL.md` exists with 2 done rows in History:
  `01_baseline` (RMSE 0.094, done) and `02_text_encoder`
  (RMSE 0.087, done).
- Backlog has 3 rows (B1, B2, B3) from prior `iterate-from-skore`
  runs.
- `overview/summary.md` exists.]

What's next?
```

## Response

```
Sibling skills (open just-in-time when a step requires):
  - organize-ml-workspace, data-science-python-stack,
    python-env-manager, python-api, python-code-style,
    build-ml-pipeline, evaluate-ml-pipeline, test-ml-pipeline,
    smoke-test-ml-pipeline, iterate-from-skore / iterate-from-user
```

---

## Pre-flight

```
Pre-flight (iterate-ml-experiment):
- [x] `journal/JOURNAL.md` read this turn
      Evidence: Read journal/JOURNAL.md (this turn)
- [x] `Workspace decisions` block checked for pre-recorded gates
      Evidence: tabular, env_manager, package, cv_splitter: not recorded
- [x] Mode: iterate-propose
      Evidence: 2 done rows + Backlog present → § 1 → § 2
- [x] Last experiment + its status: 02_text_encoder (RMSE 0.087, done)
      Evidence: last row of JOURNAL.md History
- [ ] Sourcing menu: pending
- [ ] Config gates: n/a — iterate mode
- [ ] Design note: pending
- [ ] G-DESIGN: pending
- [ ] Three-skill chain: pending
- [ ] Smoke gate: pending
- [ ] Summary refresh: pending
```

---

## § 1 + § 2 — Propose next

You have **two done experiments** (baseline at 0.094, text encoder at 0.087 — a 7% improvement). The Backlog holds 3 forward candidates. Time to iterate.

**How would you like me to source the next experiment?**

```
  skore    — call `report.diagnosis()` on the 02_text_encoder run;
             convert each actionable finding into Backlog rows,
             summarize, re-present this menu.
  user     — you tell me what to try:
               (a) paste a scientific article URL,
               (b) point me at a GitHub issue / spec / reference repo,
               (c) describe the idea in free text.
  my-pick  — I synthesize 2–4 candidate ideas from JOURNAL.md +
             02_text_encoder's Implication; you pick one.
  B1, B2,  — promote a row from the Backlog directly.
  or B3

Backlog (pick by index):
<awaiting JOURNAL.md Backlog table — paste here once you confirm>
```

**Which would you prefer: `skore`, `user`, `my-pick`, or one of the Backlog rows (B1–B3)?**

Once you pick, I'll either enrich the Backlog (skore branch), draft a design note (user / my-pick / B<N> branch), or surface what you're asking via follow-up questions.
