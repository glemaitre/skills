# CASE_06 — Compare past experiments (read-only)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/iterate-ml-experiment/SKILL.md` (1296 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/JOURNAL.md` has both rows in History with Headline
  results.
- `journal/01_baseline.md` (done, RMSE 0.094) and
  `journal/02_text_encoder.md` (done, RMSE 0.087) both exist.
- Both reports in the skore Project under their stems.]

Compare 01_baseline and 02_text_encoder for me. How does the new
one stack up?
```

## Response

```
Pre-flight (iterate-ml-experiment):
- [ ] Sibling SKILL.md files opened **this turn**
      Evidence: Read .agents/skills/evaluate-ml-pipeline/SKILL.md (this turn)
- [ ] `journal/JOURNAL.md` read this turn
      Evidence: Read journal/JOURNAL.md (this turn)
- [ ] `Workspace decisions` block in JOURNAL.md Status checked
      Evidence: n/a — compare is read-only; no new gates
- [ ] Mode: Compare (read-only, no new artifact)
      Evidence: user request "compare 01_baseline and 02_text_encoder"
- [ ] Last experiment + its status known
      Evidence: 02_text_encoder, done, RMSE 0.087
- [ ] In iterate mode, sourcing menu: n/a — read-only mode
      Evidence: n/a — compare is not a new-experiment request
- [ ] Sourcing strategy: n/a — read-only
      Evidence: n/a
- [ ] Strategy skill dispatched: n/a — read-only
      Evidence: n/a
- [ ] Bootstrap gates: n/a — not bootstrap
      Evidence: n/a
- [ ] Design note drafted: n/a — read-only
      Evidence: n/a
- [ ] User approval of design note: n/a — read-only
      Evidence: n/a
- [ ] Post-approval implementation chain: n/a — read-only
      Evidence: n/a
- [ ] Skill(python-api) consulted: n/a — read-only, no new symbols
      Evidence: n/a
- [ ] Run gate: n/a — read-only
      Evidence: n/a
```

---

## Headline Comparison

| Experiment | Intent | Headline Result |
|---|---|---|
| **01_baseline** | Skrub tabular pipeline + default learner (scikit-learn RF) | RMSE 0.094 ± ? (5-fold CV) |
| **02_text_encoder** | Add text-feature encoding to baseline pipeline | RMSE 0.087 ± ? (5-fold CV) |

**Gain:** 0.087 vs 0.094 = **~7.4% relative improvement** from adding the text encoder.

---

## Deeper read available

To inspect residuals, slice metrics, calibration, or other per-fold stability in either report, I can route to `evaluate-ml-pipeline` and pull the full diagnostic — one report at a time. Would you like me to:

- **Dive into 02_text_encoder's report** (the winner) — check if the improvement is stable across folds and where the gains concentrate?
- **Compare residual patterns** between the two — does the text encoder fix a particular failure mode from baseline?
- **Leave it here** — the headline improvement looks solid; move to the next iteration?

Let me know which; otherwise I'll stop here and await your next move.
