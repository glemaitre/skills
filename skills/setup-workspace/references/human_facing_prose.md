# Human-facing prose

Text in the **user project** must earn its place as data science:
what the pipeline or analysis is doing, what a figure/table/report
section shows for **this** data or experiment, or an insight,
caveat, or modelling implication.

It must **not**:

- describe the skills framework, skill ids, or HITL/gates
- mention `skore_skills`, `python -m …`, `cells run`, `site build`,
  `notebook convert`
- explain how an output was produced
- document API surface, version floors, or locator recipes

**Allowed exceptions** (machine contracts, not prose):

- `<!-- results-embed: <slug> -->`
- `# %%` / `# %% [markdown]` cell markers
- substitution tokens (`<stem>`, `<pkg>`, `REPORT_ID = "..."`)
  without a tutorial comment

Authoring hints belong in SKILL.md and `references/`, not in the
artifact. `python -m skore_skills style` is ruff only; it does not
rewrite comments.
