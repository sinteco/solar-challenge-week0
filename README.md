# Solar Challenge - Week 0

This repository contains starter files and a basic continuous integration setup to reproduce the Python environment used for the project.

## Reproduce the environment

1. Create and activate a virtual environment (macOS / zsh shown):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Verify Python is available:

```bash
python --version
```

## GitHub Actions (CI)

A basic workflow is included at `.github/workflows/ci.yml`. It runs on push and pull requests and executes:

- Checkout
- Set up Python
- Upgrade pip
- `pip install -r requirements.txt`
- Print `python --version`

You can expand the workflow to run unit tests (see `.github/workflows/unittests.yml`).

## Merge `setup-task` into `main` via Pull Request

1. Push your branch to the remote:

```bash
git push origin setup-task
```

2. Open a Pull Request on GitHub from `setup-task` into `main` (or use the web UI).

3. Make sure CI passes on the PR. When all checks pass and reviews are complete, merge the PR.

## Suggested folder structure

```
├── .vscode/
│   └── settings.json
├── .github/
│   └── workflows
│       ├── unittests.yml
├── .gitignore
├── requirements.txt
├── README.md
 |------ src/
├── notebooks/
│   ├── __init__.py
│   └── README.md
├── tests/
│   ├── __init__.py
└── scripts/
    ├── __init__.py
    └── README.md
```

## Next steps (suggestions)

- Pin dependencies in `requirements.txt` or split into `requirements.txt` and `requirements-dev.txt`.
- Add a minimal unit test and enable it in the CI workflow.
- Add code style linters (flake8/ruff) to CI.
