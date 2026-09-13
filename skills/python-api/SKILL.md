---
name: python-api
description: >
  Look up the public API of a Python package against the *installed
  version* and cache what's worth keeping. Shapes: (0) cache hit
  under `scratch/api/<lib>/<version>/`; (1) `python -m skore_skills
  api get <dotted>` / `api version <pkg>`; (3) WebSearch + WebFetch
  of versioned docs for narrative ("how", "which", "what does X
  return when Y"). Never write a symbol from training-data memory —
  recognition is not a lookup.

  TRIGGER — any of:
  - About to name a symbol (function / class / method / arg) in code.
  - User asks "what's the signature of X?", "what's in module Y?",
    "how do I call X?", "which of A/B should I use?".
  - User asks "what does X return when <condition>?" (Shape 3).
  - Another workflow skill (`build-ml-pipeline`,
    `evaluate-ml-pipeline`, `iterate-from-skore`,
    `smoke-test-ml-pipeline`) says "consult the API skill".
  - About to reach for a library's "obvious" pattern from memory.

  SKIP when: the signature is obvious from a call site you just
  read in this turn; the work is filesystem / shell only (no
  Python symbols); a `scratch/api/<lib>/<version>/<topic>.md`
  cache file already answers the question (still a Shape 0
  consultation — you just don't fetch).

  HOW TO USE: resolve the package version with
  `python -m skore_skills api version <pkg>`. List
  `scratch/api/<lib>/<version>/`. Then pick the shape. For a
  signature, run `python -m skore_skills api get <dotted.path>`
  (the CLI writes the cache). Narrative findings use versioned
  WebSearch / WebFetch (Shape 3). **Never `python -c`.** Stack
  orientation: `references/stack_orientation.md`. Named traps:
  `references/named_traps.md`.
---

# python-api

Discover the public API of any installed Python package, cache what
matters, never trust training-data memory.

Three durable rules:

1. **Lookup against the installed version, never memory.**
2. **Cache to `scratch/api/<lib>/<version>/<topic>.md`** (the CLI
   writes this on `api get`).
3. **Bundled `references/` ≠ workspace cache.**

## This-turn contract (including no-tools evals)

Checklist boxes are only `[x]`, `[ ]`, or `[n/a]`.

**A cache hit is never `BLOCKED`.** If
`scratch/api/<lib>/<version>/<topic>.md` is already on disk, Read
it. If it answers the user's question, treat it as authoritative
regardless of how short it is. Do not grade its completeness, refresh
it, or re-run `api get` unless the user explicitly asks for a refresh
or the requested fact is absent.

**When tools are missing, still write the plan.** Name
`python -m skore_skills api version <pkg>` and
`python -m skore_skills api get <dotted>`, plus the cache path.
`BLOCKED` means: do **not** emit the looked-up fact (signature,
arg list, return type, import, call).

**Do not preview the memory answer.** Quote signatures only after
the CLI or cache file exists.

**Never `python -c`.** Refuse that form; propose `api get` /
`api version` instead. That refusal is not `BLOCKED`.

**When `run_skore_skills` exists, run the CLI this turn.** Do not
write `scratch/<ts>_*.py` probe scripts. Do not use `run_python`
for lookups.

**Named traps are leads, not lookups.** Confirm with `api get`
before treating a rename as installed. Load
`references/named_traps.md` on demand.

## What kind of question? → Shape

| Question | Shape |
|---|---|
| File already under `scratch/api/<lib>/<version>/` | **0** cache hit — Read it |
| "What's the signature / docstring of X?" | **1** `python -m skore_skills api get <dotted>` |
| "What version is installed?" | `python -m skore_skills api version <pkg>` |
| "What's in module Y?" / open-ended `dir` | **1** on the module, or Shape 3 docs |
| "How / which / what does X return when Y?" | **3** versioned WebSearch + WebFetch |

Cache topic for `api get pkg.foo.Bar` is
`scratch/api/<pkg>/<version>/pkg_foo_Bar.md` (dots → underscores).

**Shape 3:** signatures do not answer dispatch-under-argument.
Until a version-pinned docs page is fetched (not `/latest/` or
`/stable/` as the cached source), that dispatch is BLOCKED unless
the cache already holds the narrative. No WebFetch this turn →
plan the query and stop.

Optional LSP hover: `references/shape1b_lsp_setup.md`. Prefer
`api get` when tools exist.

## Stop conditions

- No symbols from memory.
- No inline `python -c`, including one-line `__version__` checks.
- No `scratch/<ts>_*.py` lookup probes — the CLI is Shape 1.
- Lookup failure ≠ artifact missing (`Project.get` is by **id**,
  not key — see named traps). Never re-run an experiment to
  "fix" a KeyError before `summarize()`.
- Do not cache `/latest/` or `/stable/` URLs as the source of
  truth.

## Pre-flight (emit before lookup)

```
- [ ] Version resolved: `python -m skore_skills api version <pkg>`
      Evidence: CLI stdout | workspace state already names the version
- [ ] Cache listed: scratch/api/<lib>/<version>/
      Evidence: list_dir / Read | workspace state
- [ ] Shape picked: 0 / 1 / 3
- [ ] Command: python -m skore_skills api get <dotted>
      Evidence: run_skore_skills this turn | BLOCKED plan (no tools)
- [ ] Cache path named: scratch/api/<lib>/<version>/<topic>.md
```

## Companion skills

Callers (`build-ml-pipeline`, `evaluate-ml-pipeline`, …) consult
this skill before naming stack symbols. After lookup, return to
the caller.

## References (load on demand)

- `references/named_traps.md`
- `references/stack_orientation.md`
- `references/bootstrap_cache.md`
- `references/shape1b_lsp_setup.md`
- `references/skrub_interop.md`
