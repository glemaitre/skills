# Release process

This document describes how to release the `skore-skills` package and the
skills catalog. You need write access to `probabl-ai/skills` and to the PyPI
project.

Releases use semantic versioning:

- Major and minor releases are numbered `X.Y.0`.
- Patch releases are numbered `X.Y.Z`.

Publishing a GitHub Release creates the source tarball that
`skore skills install` downloads from `probabl-ai/skills`. The installer reads
`releases/latest`, then downloads `/repos/probabl-ai/skills/tarball/{tag}` and
copies each skill from the paths in `.catalog.json`. The same release publishes
the `skore-skills` wheel and sdist to PyPI.

## One-time setup

Before the first publish:

1. On PyPI, add a trusted publisher for `skore-skills`. Use a pending publisher
   when the project does not exist yet.
   - Owner: `probabl-ai`
   - Repository: `skills`
   - Workflow: `release.yml`
   - Environment: `release`
2. On GitHub, create an environment named `release`. Add required reviewers
   when PyPI publishing should wait for approval.

The skills tarball is available as soon as the GitHub Release is published.
PyPI publishing waits on the `release` environment when that environment has
required reviewers.

## Cutting a release

1. Run `pixi run check`.
2. Bump the version with `pixi run bump-major`, `pixi run bump-minor`, or
   `pixi run bump-patch`. Review the diff and merge that commit.
   [`tools/bump_version.py`](tools/bump_version.py) writes the version into
   `.catalog.json`, `pyproject.toml`, `pixi.toml`, and the plugin manifests.
   It leaves commits and tags to you.
3. Create a [GitHub Release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
   whose tag is exactly that version, for example `0.8.0`. GitHub can create
   the tag and the release together. The tag must match `[project].version` in
   `pyproject.toml` and `version` in `.catalog.json`.

[`.github/workflows/release.yml`](.github/workflows/release.yml) builds the
package and publishes it to PyPI.

conda-forge is updated from the PyPI release outside this repository.
