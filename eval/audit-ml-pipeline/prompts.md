# audit-ml-pipeline eval

---

## CASE_01 — Audit is read-only and returns a digest

**User prompt:**
> Audit experiment 02 after evaluation.

**Assumed workspace state:**
- The design is approved, smoke is green, and the persisted report exists.
- `evaluate-ml-pipeline` dispatched this audit.

**Must do:**
- Confirm the report with `project.summarize()` and load it with
  `project.get(id)`.
- Render checks and metrics into the audit digest.
- Derive G-AUDIT-FINDING from the digest.
- Ask Additional report view / Custom query / Custom plot / Close
  audit in that order; return the digest, finding, and normalized
  report locator only after Close audit.

**Must NOT do:**
- Call `skore.evaluate` or `project.put`.
- Require the experiment to be `done` before audit.
- Dispatch record-outcome before producing the digest.
- Write the journal directly.

---

## CASE_02 — Direct audit owns the close

**User prompt:**
> Re-audit experiment 03.

**Assumed workspace state:**
- This is a direct free-text invocation.
- The report exists and smoke is green.

**Must do:**
- Surface the normalized persisted-report locator.
- Run audit, then call `manage-ml-backlog` record-outcome with the
  digest and locator.
- Build the site only after record-outcome when enabled.
- Close with `git end-turn --stage evaluate`.

**Must NOT do:**
- Open the next-lever menu from record-outcome mode.
- Call record-outcome before audit.
- Run `git commit`.

---

## CASE_03 — Dispatched audit returns without a second close

**User prompt:**
> Continue the model loop and audit the evaluated baseline.

**Assumed workspace state:**
- `model-ml-pipeline` dispatched the audit.
- `cells run` already produced the digest.
- The user picked Close audit at the post-audit gate.
- Normalized locator is
  `local workspace: [reports/](../reports/) · id: local-report-id`.

**Must do:**
- Return the digest, G-AUDIT-FINDING, locator, and optional headline to
  `model-ml-pipeline`.
- State that the dispatcher owns record-outcome, site, and git close.

**Must NOT do:**
- Run `git end-turn` or `persist-ml-git` from this skill (naming
  them as the **dispatcher's** close is allowed).
- Load `triage-ml-task` from this skill.
- Dispatch `manage-ml-backlog` from this skill.

---

## CASE_04 — Missing report stops without fabrication

**User prompt:**
> Audit experiment 04.

**Assumed workspace state:**
- The design is approved and smoke is green.
- `project.summarize()` has no row for experiment 04.

**Must do:**
- Stop and report that the persisted report is missing.
- Route recovery to evaluation.

**Must NOT do:**
- Re-run `skore.evaluate` from audit.
- Invent a report id, URL, metrics, or digest.
- Mark the experiment done.

---

## CASE_05 — Additional audit work loops before close

**User prompt:**
> Add another audit view before we close.

**Assumed workspace state:**
- The initial audit digest exists.
- The report API lookup confirms one task-compatible extra view.

**Must do:**
- Present Additional report view / Custom query / Custom plot /
  Close audit in that exact order.
- Confirm the selected accessor with `api get`, append it to the
  same `audit/<stem>.py`, run style + cells run, and overwrite the
  digest.
- Recompute G-AUDIT-FINDING and present the same gate again.

**Must NOT do:**
- Guess an accessor or show unavailable disabled choices.
- Convert notebooks, build the site, run git end-turn,
  record-outcome, or return to the dispatcher before Close audit.
- Call `evaluate` or `put`.
