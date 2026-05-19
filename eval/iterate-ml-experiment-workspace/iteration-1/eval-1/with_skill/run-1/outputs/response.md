# Response to "What's next?"

**Read state:** `journal/JOURNAL.md` confirms 2 done rows in History:
- `01_baseline`: RMSE 0.094 (done)
- `02_text_encoder`: RMSE 0.087 (done)

**Backlog:** 3 items (B1, B2, B3) from prior `iterate-from-skore` runs.

**Summary:** The text encoder improved the baseline (RMSE 0.087 vs 0.094). The backlog has three candidates sourced from the baseline's diagnostic report. Now we decide what to try next.

---

## How would you like me to source the next experiment?

I'm ready to propose the third iteration. Here are your sourcing options:

**skore** — Call `report.diagnosis()` on the 02_text_encoder run (the latest); convert each actionable finding into new rows in the Backlog below, summarize, and re-present this menu.

**user** — You tell me what to try, one of three ways:
  - (a) paste a scientific article URL — I read it,
  - (b) point me at a GitHub issue / spec / reference repo,
  - (c) describe the idea in free text.

**my-pick** — I synthesize 2-4 candidate ideas from JOURNAL.md + the text encoder's Implication; you pick one.

**B<N>** — Promote a row from the Backlog table directly.

---

## Backlog (pick by index):

| # | Item | Source |
|---|---|---|
| B1 | Feature engineering: polynomial interactions | skore:02_text_encoder |
| B2 | Hyperparameter tuning: increase regularization | skore:02_text_encoder |
| B3 | Alternative encoder: try GRU instead of LSTM | skore:02_text_encoder |

---

Which option would you prefer?
