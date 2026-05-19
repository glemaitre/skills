# CASE_04 — Don't synthesize the fixture

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/smoke-test-ml-pipeline/SKILL.md` (423 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `data/` contains real data.
- The smoke test currently uses it but is slow.]

The data dir is too big and the smoke test takes 2 minutes. Just
write a fixture with 100 fake rows.
```

## Response

I cannot do that.

The smoke test's only value is that it **reads the real `data/` source**. A synthetic 100-row fixture:

1. **Defeats the diagnostic-by-construction property.** The test will pass on both the correct pipeline shape *and* the buggy one (load → featurize → split). That's the opposite of a smoke test.

2. **Skips the real loaders.** If the loader has a subtle bug that drops or duplicates rows on certain inputs, the synthetic fixture never finds it.

3. **Doesn't exercise the actual `data/` binding.** The whole point is to catch "this works in CV but breaks at predict time on real data"; a fake fixture has already lost the game.

The Stop conditions are explicit on this:

> **Don't synthesize the fixture.** The smoke test reads the real
> `data/` source. Synthetic fixtures look fine but skip the
> loaders that actually break in production.

## What to do instead

**The 2-minute runtime is a sign the fixture is too large or the pipeline is computing unnecessary work at predict time.**

Three options, in priority order:

1. **Shrink the predict window.** The smallest honest window is best (e.g., one day for a t+24 model). If the current fixture uses a month of predict data, cut it to the forecast horizon's length.

2. **Partition `data/`.** Instead of loading all of `data/`, construct the fixture to load *only* the time slice needed for train + predict:
   - Read the experiment's source binding (what time bounds does it use?).
   - Pre-filter `data/` to those bounds in the fixture.
   - The `tmp_path` pytest built-in can hold the sliced files.

3. **Profile the pipeline itself.** If even a small real-data fixture is slow, the featurization is expensive at predict time. That's a separate problem (route to `build-ml-pipeline` to ask whether the history reference is being computed redundantly), but it's worth knowing.

Which path fits your experiment best?
