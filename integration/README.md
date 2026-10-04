# Integration scenarios

A scenario is a seed workspace, an ordered list of user replies, a driver
file, and a filesystem snapshot after each reply. Manual replies work in
Claude Code, OpenCode, Cursor, GitHub Copilot, and Pi. `run` can also
launch Cursor Agent, Claude Code, OpenCode, or Pi on the spine.

Install the workflow pack named by the scenario, materialize the seed
into an empty folder, and open that folder in the harness. Paste one
reply, let the agent stop, then check the folder against that turn. A
check uses only that turn's `expect` block. It is the full snapshot, not
a delta from the previous turn.

Forks are alternate replies. Copy the workspace after the turn named by
`after`, then paste the fork instead of the next spine reply.

## Layout

```text
integration/scenarios/<id>/
├── README.md
├── SCENARIO.md
├── turns.json
├── forks.json
└── seed/
```

`turns.json` names the scenario, the workflow pack, the seed directory,
the driver file, and the turns. Each turn has `id`, `say`, optional
`checkpoint`, and `expect`. `forks.json` lists `id`, `after`, `say`, and
`expect`. The driver is copied to the workspace root. It lists the spine
choices that `run` treats as already authorized.

`expect` keys:

| Key | Meaning |
| --- | --- |
| `files` | Each relative path or glob matches at least one path. |
| `absent` | Each path or glob matches nothing. |
| `contains` | That exact file contains every substring. |
| `contains_any` | One file matching the glob contains every substring. |

Paths are POSIX and stay inside the workspace. Substring checks should
use filled cells, not scaffold placeholders. Stem slugs stay globbed
because the agent chooses them.

`validate` also checks the seed directory against the `setup-open` turn,
which is the untouched seed.

## Commands

```bash
python tools/integration_scenario.py validate
python tools/integration_scenario.py materialize <scenario> --dest PATH
python tools/integration_scenario.py prompt <scenario> --turn <id>
python tools/integration_scenario.py prompt <scenario> --fork <id>
python tools/integration_scenario.py check <scenario> --workspace PATH --turn <id>
python tools/integration_scenario.py run <scenario> --harness claude --workspace PATH
```

`prompt` writes the reply to stdout. Checkpoint turns also print a copy
reminder on stderr. `materialize` refuses a non-empty destination unless
`--force` is set. `run` materializes an absent or empty workspace, refuses
a non-empty one unless `--reuse-workspace` is set, and copies the driver
when a reused workspace does not already contain it.

## Automated run

`run` starts one harness and sends one prompt: read `SCENARIO.md` and
carry out that journey. It does not type later replies. `--interactive`
inherits the terminal so the normal TUI is visible and can be interrupted.
The default is headless: output is streamed and also saved.

```bash
python tools/integration_scenario.py run california-housing \
  --harness claude --workspace ../housing
python tools/integration_scenario.py run california-housing \
  --harness opencode --workspace ../housing --interactive
```

`--harness` is `cursor`, `claude`, `opencode`, or `pi`. GitHub Copilot
stays on the manual prompt and check flow. Optional `--model` is passed
through. `--timeout` defaults to 3600 seconds and then terminates the
process group. Ctrl-C does the same.

Each harness uses its existing login. Cursor Agent can use
`CURSOR_API_KEY`. This command does not install a CLI. `cursor` the
editor is not `cursor-agent`; install the Agent CLI from
<https://cursor.com/docs/cli> when `cursor-agent` is missing.

Headless flags are Claude `--print` with `stream-json`, OpenCode `run
--format json`, Cursor Agent `--print` with `stream-json`, and Pi
`--mode json`. Interactive runs omit those and show the TUI. Claude reads
the driver with `--append-system-prompt-file`. OpenCode receives it
through `OPENCODE_CONFIG_CONTENT`. Pi reads it with
`--append-system-prompt`. Cursor has no system-prompt file, so the runner
writes a root `AGENTS.md` marked `integration-scenario-runner`, refuses
to replace an existing file, and deletes only that wrapper afterward.

Approval flags apply only to the scenario workspace: Claude
`--permission-mode auto`, OpenCode `--auto`, Cursor Agent `--force` and
headless `--trust`, and Pi `--approve`. Pi `--approve` trusts
project-local files; Pi does not ask before every tool call. The scenario
may run package-manager commands such as `pixi`.

Logs land in `.transcripts/integration/<run-id>/`: headless `stdout.txt`
and `stderr.txt`, plus `result.json` with the harness, mode, duration,
exit status, and check errors. After a harness exit of 0, `run` checks
`iterate-stop`. A missing executable exits 127, timeout exits 124, and
interruption exits 130. A failing harness status is returned as-is and
skips that check. A passing harness with a failed final check exits 1.

The first scenario is [california-housing](scenarios/california-housing/README.md).
