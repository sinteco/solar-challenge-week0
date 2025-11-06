# scripts/

This folder contains small utility scripts used by the EDA pipeline and the Streamlit app.

- `write_summary_md.py` — writer script that computes a summary and writes `outputs/compare/summary_table.md`.

Usage:

```bash
# run writer using the project's venv
./.venv/bin/python scripts/write_summary_md.py
```

If you deploy the Streamlit app to Streamlit Community Cloud, include the required CSV files in the repo or modify the app to download them at runtime.
