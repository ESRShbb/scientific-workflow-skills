# Developer guide

[English README](README.md) · [中文首页](README.zh-CN.md) · [日本語 README](README.ja.md)

## Repository layout

Each folder under `skills/` is an independently usable skill. Its `SKILL.md` is the entrypoint; scripts and references support the operations described there. The `scientific-figure-format` skill provides review methods and has no software driver.

Keep instructions general and concise. Use synthetic fixtures for public tests. Keep private research inputs and proprietary application binaries out of the repository. See [repository guidance](AGENTS.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

## Run checks

Python 3.10+ is required. No third-party package is needed for the synthetic tests.

```sh
python -B scripts/validate.py
```

On Windows, `py -3 -B scripts/validate.py` can select Python 3 explicitly.

The runner checks skill entrypoints, local Markdown links and Python syntax, then runs each script test suite in a separate process. GitHub Actions runs the same checks on Windows and Linux. Tests generate their own fixtures and do not launch proprietary applications.

A script test passing establishes only the behavior it exercises. Native operation, visual quality and scientific review need their own evidence. The maintainer's existing observations and capability boundaries are recorded in [VALIDATION.md](VALIDATION.md).

## Documentation

Keep the English, Chinese and Japanese READMEs aligned around purpose, installation, everyday examples and required software. Put installation details in [INSTALLATION.md](INSTALLATION.md). Keep implementation details and development history out of the introductory pages.
