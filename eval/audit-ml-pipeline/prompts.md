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
- Return the digest and normalized report locator to the caller.

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

**Must do:**
- Return the digest, locator, and optional headline to
  `model-ml-pipeline`.
- State that the dispatcher owns record-outcome, site, and git close.

**Must NOT do:**
- Run a second `git end-turn`.
- Load triage after returning to the dispatcher.
- Dispatch `manage-ml-backlog` before returning.

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
