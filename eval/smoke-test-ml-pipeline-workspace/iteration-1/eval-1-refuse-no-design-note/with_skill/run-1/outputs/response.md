I cannot write the smoke test yet.

The skill's stop condition is explicit: **No smoke test without an approved design note + script.** The pairing rule is hard:

> `tests/smoke/test_NN_<short_name>.py` exists only when `journal/NN_<short_name>.md` is at least `approved` *and* `experiments/NN_<short_name>.py` exists with the matching stem.

I see that:
- `experiments/03_target_transform.py` exists ✓
- `journal/03_target_transform.md` does NOT exist ✗

The design note `journal/03_target_transform.md` must exist and be approved before the smoke test can be written. The design note establishes:
- The experiment's Question and Method (frozen sections in the journal)
- The Status.headline with the CV mean value (hardcoded as `CV_MAE_MEAN` in the smoke test)
- The experimental intent and success criteria

Per the skill's routing rule, you should route to **`iterate-ml-experiment`** to create and approve the design note before returning here to write the smoke test.
