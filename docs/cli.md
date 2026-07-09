# CLI Reference

OpenAgent Eval ships a [Typer](https://typer.tiangolo.com)-based command line interface named `oaeval`.

## Global options

| Option | Description |
| --- | --- |
| `--version`, `-V` | Show the installed version and exit |
| `--help` | Show help for any command |

```bash
oaeval --version
oaeval --help
```

## `oaeval init`

Create a `config.yaml` with default settings in the current directory.

```bash
oaeval init
oaeval init --config eval.yaml --force
```

| Option | Description |
| --- | --- |
| `--config`, `-c` | Path to create (default `config.yaml`) |
| `--force`, `-f` | Overwrite an existing file without prompting |

## `oaeval run`

Run an evaluation pipeline using a configuration file.

```bash
oaeval run config.yaml
oaeval run config.yaml --output html --verbose
```

| Argument | Description |
| --- | --- |
| `config_path` | Path to the configuration file |

| Option | Description |
| --- | --- |
| `--output`, `-o` | Override output format: `terminal`, `markdown`, `html`, `json` |
| `--verbose`, `-v` | Enable verbose output |

## `oaeval report`

View a stored evaluation report.

```bash
oaeval report latest
oaeval report exp-001 --output html
```

| Argument | Description |
| --- | --- |
| `report_id` | Report ID, or `latest` for the most recent run |

| Option | Description |
| --- | --- |
| `--output`, `-o` | Output format (default `terminal`) |
| `--output-dir`, `-d` | Reports directory (default `./reports`) |

## `oaeval compare`

Compare two experiments side by side.

```bash
oaeval compare exp-001 exp-002
oaeval compare exp-001 exp-002 --metrics faithfulness answer_relevancy
```

| Argument | Description |
| --- | --- |
| `experiment_a` | First experiment ID or path |
| `experiment_b` | Second experiment ID or path |

| Option | Description |
| --- | --- |
| `--metrics`, `-m` | Specific metrics to compare (default: all) |
| `--output-dir`, `-d` | Reports directory (default `./reports`) |

## `oaeval list`

List previous evaluation runs.

```bash
oaeval list --limit 20
```

| Option | Description |
| --- | --- |
| `--limit`, `-l` | Number of evaluations to show (default `10`) |
| `--output`, `-o` | Filter by output format |
| `--output-dir`, `-d` | Reports directory (default `./reports`) |

## `oaeval doctor`

Check the environment, installed dependencies, and API key availability.

```bash
oaeval doctor --verbose
```

| Option | Description |
| --- | --- |
| `--verbose`, `-v` | Show detailed information |

Use this when something looks wrong after [installation](installation.md).

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Runtime or configuration error |
| `2` | Invalid CLI usage |

## Shell completion

`oaeval` is built on Typer and supports shell completion. Enable it for your shell:

```bash
# bash
eval "$(_OAeval_COMPLETE=bash_source oaeval)"

# zsh
eval "$(_OAeval_COMPLETE=zsh_source oaeval)"

# fish
_oaeval_completion fish | source
```

## Next steps

- Embed evaluations in tests via the [API Reference](api.md).
- See real commands in [Examples](examples.md).
