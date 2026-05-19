# Baseline Experiment File Location Report

## Investigation Summary

The requested file `experiments/01_baseline.py` does not exist in the repository.

## Repository Structure

The evaluation system in this repository uses a different architecture:

- **Evaluation runner:** `/Users/glemaitre/Documents/packages/skills/probabl-skills/eval/run.py`
- **Skill evaluations:** `/Users/glemaitre/Documents/packages/skills/probabl-skills/eval/<skill-name>/`
- **Python API evaluation cases:** `/Users/glemaitre/Documents/packages/skills/probabl-skills/eval/python-api/prompts.md`
- **Transcripts storage:** `/Users/glemaitre/Documents/packages/skills/probabl-skills/eval/python-api/transcripts/`

## Current State

- Baseline transcripts exist at: `/Users/glemaitre/Documents/packages/skills/probabl-skills/eval/python-api/transcripts/baseline/`
- Output directory for this run exists (empty): `/Users/glemaitre/Documents/packages/skills/probabl-skills/eval/python-api-workspace/iteration-1/eval-2/without_skill/run-1/outputs/`

## How to Generate Baseline Report

The evaluation system uses `eval/run.py` to generate transcripts from `prompts.md` case definitions. To regenerate the baseline evaluation:

```bash
python3 eval/run.py python-api baseline --no-skill
```

This will:
1. Read all cases from `eval/python-api/prompts.md`
2. Run each case against Claude Haiku 4.5 without a skill system prompt
3. Write transcript files to `eval/python-api/transcripts/baseline/`

## Note on project.get("01_baseline")

The `KeyError` from `project.get("01_baseline")` suggests that the skore.Project instance expects results to be stored/registered under that key. The baseline transcripts exist in the filesystem but may not be registered in the Project's internal state. Running the eval command or manually registering the existing baseline transcripts with the Project instance should resolve the KeyError.
