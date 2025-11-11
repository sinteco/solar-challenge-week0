# Solar Challenge - Week 0

[![CI](https://github.com/sinteco/solar-challenge-week0/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sinteco/solar-challenge-week0/actions/workflows/ci.yml)
[![Unittests](https://github.com/sinteco/solar-challenge-week0/actions/workflows/unittests.yml/badge.svg?branch=main)](https://github.com/sinteco/solar-challenge-week0/actions/workflows/unittests.yml)

This repository contains starter files, reproducible EDA notebooks and a basic continuous integration setup to make development and onboarding easier.

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

Quick test run (after installing requirements):

```bash
# run the small pytest smoke-tests
./.venv/bin/python -m pytest -q
```

## GitHub Actions (CI)

A basic workflow is included at `.github/workflows/ci.yml`. It runs on push and pull requests and executes:

- Checkout
- Set up Python
- Upgrade pip
- `pip install -r requirements.txt`
- Print `python --version`

You can expand the workflow to run unit tests (see `.github/workflows/unittests.yml`). The repo already includes a small pytest smoke-test that validates the summary writer using lightweight fixtures.

### How CI installs dependencies

The workflows run `pip install -r requirements.txt`. Make sure new Python dependencies are added to `requirements.txt` so CI can install them.

## Common commands & runnable examples

- Run the compare notebook headlessly (uses nbconvert/ExecutePreprocessor):

```bash
# execute and write an executed copy (uses project's kernels if installed)
jupyter nbconvert --to notebook --execute notebooks/compare_countries.ipynb \
  --output notebooks/compare_countries_executed.ipynb --ExecutePreprocessor.timeout=600 --ExecutePreprocessor.kernel_name=eda-sierraleone
```

- Run the quick compare summary script that prints mean/median/std and p-values:

```bash
./.venv/bin/python scripts/compare_countries_run.py
```

- Write the markdown summary to `outputs/compare/summary_table.md` (script):

```bash
./.venv/bin/python scripts/write_summary_md.py
```

- Execute an individual country EDA notebook using the helper runner (example):

```bash
python scripts/run_notebook.py --input notebooks/benin_eda.ipynb --output notebooks/benin_eda_executed.ipynb --kernel eda-benin
```

## Data & outputs (locations)

- `data/` — cleaned CSV files for each country (e.g. `data/benin_clean.csv`, `data/togo_clean.csv`, `data/sierraleone_clean.csv`). These are now tracked in the repo for small fixtures and reproducibility. Large production dumps should not be committed.
- `outputs/<country>/` — per-country output folder with generated PNGs and `report.txt` produced by the EDA scripts.
- `outputs/compare/summary_table.md` — cross-country summary extracted by `scripts/write_summary_md.py`.

## Streamlit dashboard (optional)

The project contains a small Streamlit app scaffold at `app/main.py` with a top-level entry `streamlit_app.py`. To run locally:

```bash
./.venv/bin/python -m streamlit run streamlit_app.py
```

When deploying to Streamlit Community Cloud, ensure `requirements.txt` includes `streamlit` and the cleaned CSVs are available in the repo (or the app downloads them at runtime).

## Contributing

- Use feature branches (e.g. `feat/your-feature`) and open a PR into `main`.
- Keep commits small and focused. Use messages like `feat(...)`, `fix(...)`, `chore(...)`.
- Add tests for new behavior; CI will run `pytest` as configured.
- If adding large data files, prefer to put them behind a download script or host them externally and reference them in the repo (do not commit very large binaries).

## Troubleshooting CI failures

- If CI reports ModuleNotFoundError for new packages, add them to `requirements.txt` and push a new commit. The workflows install that file during the job.

---

If you'd like, I can also:

- Add a dedicated `requirements-dev.txt` used by CI to keep runtime installs smaller.
- Add CI caching to speed up `pip install`.
- Create a short `CONTRIBUTING.md` with the PR checklist.
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
