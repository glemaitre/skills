# Probabl Skills

A set of skills to steer your AI-assisted machine learning experiments.
The skills help you:

- build your machine learning pipeline with core data science libraries
  (e.g. scikit-learn, skrub, skore, pandas, polars) while ensuring
  your agent follows correct methodologies
- evaluate and store your results so you can easily audit and get insights from them
- connect your agent to [Skore Hub](https://skore.probabl.ai/) to get a comprehensive view of
  your experiments and results
- iterate on your next experiments using insights from Skore diagnostics and your own
  feedback
- organize your workspace according to best practices for data science projects
  (e.g. cookiecutter template)

Probabl skills let you focus on the science while AI agents handle the implementation,
guided by two important ingredients: core data science libraries for maintainability  and
methodological best practices for running your machine learning experiments properly.

In practice, from a prompt such as:

```text
╭────────────────────────────────────────────────────────────────────────╮
│ > Given the context in the file `data/README.md` and the data located  │
│   in `data/`, let's build a first machine learning pipeline that will  │
│   serve as baseline for the next experiments that we are going to run  │
│   together.                                                            │
╰────────────────────────────────────────────────────────────────────────╯
```

you can expect your agent to start experimenting with you. The skills work well with
models such as Claude Opus and Sonnet and produce great results with smaller models such
as Qwen 3.6 30B or DeepSeek v4 Flash.

As for agent harnesses, we tested them with Claude Code, OpenCode, Cursor, and GitHub
Copilot and found no significant difference in terms of skill invocation.

## Install

You can install the skills using the `skore` CLI that you can install from PyPI or from
conda-forge and run the following command.

First install [skore-cli](https://github.com/probabl-ai/skore-cli):
```
# with pip
pip install skore-cli
# with uv
uv tool install skore-cli
# with pixi
pixi global install skore-cli
```

Then run the following command:

```bash
skore skills install
```

Install a smaller workflow pack by id when you do not need the full
companion:

```bash
skore skills install setup  # workspace, environment, git, export
skore skills install data_analysis  # data exploration
skore skills install model  # build, evaluate, smoke, audit
skore skills install loop   # triage, explore, model, build, smoke, evaluate, audit, backlog, export
skore skills install export  # notebooks and documentation site
```

`skore skills install ml-experimentation` remains the complete pack,
and the default `install` / `install all` behavior is unchanged.

You can use `uvx` or `pixi exec` to install the `skore` CLI and directly run the
command in an isolated environment:

```bash
uvx --from skore-cli skore skills install
```

or

```bash
pixi exec --spec skore-cli skore skills install
```

If you prefer `npx`, then you can use:

```bash
npx skills add probabl-ai/skills
```

### Alternative — Claude Code plugin marketplace

If you only use Claude Code and prefer the native plugin flow, this repo is
also a [Claude Code plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces):

```bash
/plugin marketplace add probabl-ai/skills
```

```bash
/plugin install probabl-skills@probabl-skills
```

`/plugin update` pulls new releases.

## Skills in detail

### Meta and setup actions

| Skill | Description |
| --- | --- |
| [triage-ml-task](skills/triage-ml-task/SKILL.md) | Session owner: list installed entry skills and ask which to run. |
| [review-ml-experiment](skills/review-ml-experiment/SKILL.md) | Gate the skore-check audit, then write one idea file per candidate. |
| [setup-ml-project](skills/setup-ml-project/SKILL.md) | Coordinate workspace, environment, and git setup. |
| [setup-workspace](skills/setup-workspace/SKILL.md) | Detect or scaffold the standard ML workspace layout. |
| [setup-python-env](skills/setup-python-env/SKILL.md) | Detect the env manager, persist managed vs user-managed, and bootstrap agent tools. |
| [setup-git](skills/setup-git/SKILL.md) | Initialize safe version control for an ML workspace. |
| [persist-ml-git](skills/persist-ml-git/SKILL.md) | Commit the current loop stage when git end-turn says invoke. |
| [model-ml-pipeline](skills/model-ml-pipeline/SKILL.md) | Coordinate build (pytest smoke), evaluation, and audit. |
| [export-ml-project](skills/export-ml-project/SKILL.md) | Coordinate executed notebooks and an offline MkDocs site. |
| [sync-ml-reports](skills/sync-ml-reports/SKILL.md) | Copy skore reports between local, Hub, and MLflow, and optionally switch the upload destination. |
| [choose-python-library](skills/choose-python-library/SKILL.md) | Resolve a library choice and add the selected dependency. |
| [plot-ml-figure](skills/plot-ml-figure/SKILL.md) | Pick pandas, seaborn, plotly, or matplotlib before writing figure code. |

### ML pipeline lifecycle

| Skill | Description |
| --- | --- |
| [explore-ml-data](skills/explore-ml-data/SKILL.md) | Explore the dataset before designing any model. |
| [research-ml-practice](skills/research-ml-practice/SKILL.md) | Literature research for an ML methodology concern. |
| [build-ml-pipeline](skills/build-ml-pipeline/SKILL.md) | Build a machine learning pipeline from the data source to the learner, including multi-tables engineering. |
| [evaluate-ml-pipeline](skills/evaluate-ml-pipeline/SKILL.md) | Evaluate a complex machine learning pipeline and get structured reports including metrics, plots, and diagnostics. |
| [smoke-test-ml-pipeline](skills/smoke-test-ml-pipeline/SKILL.md) | Stress test your machine learning pipeline on future data to make sure it works. |
| [audit-ml-pipeline](skills/audit-ml-pipeline/SKILL.md) | Once testing and the experiment are done, audit the model by loading a skore report and investigate. |

### Ideas and backlog

| Skill | Description |
| --- | --- |
| [manage-ml-backlog](skills/manage-ml-backlog/SKILL.md) | Record experiment outcomes and triage idea files into backlog rows. |
| [shape-user-idea](skills/shape-user-idea/SKILL.md) | Shape a user idea or a named artifact into one idea file after they confirm. |
| [search-ml-literature](skills/search-ml-literature/SKILL.md) | Search scientific and technical sources and write one idea file for the direction the user confirms. |

### Workspace and tooling

Breaking: catalog ids `python-env-manager` and `python-code-style` are
removed. Run `skore skills remove` on any leftover sidecars and
reinstall the setup pack.

| Skill | Description |
| --- | --- |
| [add-python-package](skills/add-python-package/SKILL.md) | Add a dependency, or ask the user when they manage the env. |
| [choose-python-library](skills/choose-python-library/SKILL.md) | Select optional libraries without reopening fixed stack choices. |
| [plot-ml-figure](skills/plot-ml-figure/SKILL.md) | Pick pandas, seaborn, plotly, or matplotlib before writing figure code. |
| [export-ml-notebook](skills/export-ml-notebook/SKILL.md) | Convert a jupytext percent file into an executed notebook. |
| [export-ml-site](skills/export-ml-site/SKILL.md) | Build an offline MkDocs documentation site from workspace markdown. |

Canonical package policy lives in the CLI (`skore_skills/data/python-stack.json`); `choose-python-library` resolves competing libraries.
