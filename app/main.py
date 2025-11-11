"""Streamlit dashboard main app for cross-country solar comparison.

Usage: streamlit run app/main.py

This app is intentionally data-agnostic: it will look for cleaned CSVs under `data/` with
the filenames `benin_clean.csv`, `togo_clean.csv`, `sierraleone_clean.csv`. If they are not
present the UI shows guidance.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Dict
from app import utils
import matplotlib.pyplot as plt


DEFAULT_PATHS: Dict[str, str] = {
    "Benin": "data/benin_clean.csv",
    "Togo": "data/togo_clean.csv",
    "SierraLeone": "data/sierraleone_clean.csv",
}


def sidebar_controls(paths: Dict[str, str]):
    st.sidebar.title("Controls")
    metric = st.sidebar.selectbox("Metric", ["GHI", "DNI", "DHI"], index=0)
    countries = st.sidebar.multiselect("Countries", list(paths.keys()), default=list(paths.keys()))
    sample_frac = st.sidebar.slider("Sample fraction (for faster rendering)", 0.01, 1.0, 0.2)
    run_tests = st.sidebar.button("Run statistical tests")
    st.sidebar.markdown("---")
    st.sidebar.markdown("Data files expected under `data/` like `benin_clean.csv`.")
    return metric, countries, sample_frac, run_tests


def main():
    st.set_page_config(page_title="Cross-country Solar Dashboard", layout="wide")
    st.title("Cross-country solar potential — Benin, Togo, Sierra Leone")
    st.markdown("Small interactive dashboard comparing GHI/DNI/DHI across countries.")

    metric, countries, sample_frac, run_tests = sidebar_controls(DEFAULT_PATHS)

    # Load data
    df_all = utils.load_cleaned_datasets({c: p for c, p in DEFAULT_PATHS.items() if c in countries})
    if df_all.empty:
        st.warning("No cleaned CSVs found in `data/`. Run the per-country EDA scripts to generate them or place cleaned CSVs in `data/` with expected filenames.")
        return

    # Optionally subsample for fast rendering
    if sample_frac < 1.0:
        df_display = df_all.groupby("country").sample(frac=sample_frac, random_state=0)
    else:
        df_display = df_all

    # Layout: left = controls + summary, right = visualizations
    left, right = st.columns([1, 2])

    with left:
        st.header("Summary")
        summary = utils.summary_table(df_all, ["GHI", "DNI", "DHI"]) if not df_all.empty else pd.DataFrame()
        st.dataframe(summary, use_container_width=True)

        if st.button("Save summary to outputs/compare/summary_table.md"):
            import os
            os.makedirs("outputs/compare", exist_ok=True)
            # reuse the writer script logic if present
            try:
                from scripts import write_summary_md as writer
                writer_main = getattr(writer, "__file__", None)
                st.success("If a writer script exists, use it; otherwise summary is visible here.")
            except Exception:
                st.info("Writer script not available in this environment; copy/paste the table or run `scripts/write_summary_md.py` locally.")

        if run_tests:
            st.subheader("Statistical tests on GHI")
            res, order_df = utils.run_ghi_tests(df_all)
            if res.get("anova"):
                st.write(f"ANOVA: F={res['anova']['F']:.4f}, p={res['anova']['p']:.4e}")
            else:
                st.write("ANOVA: not available")
            if res.get("kruskal"):
                st.write(f"Kruskal–Wallis: H={res['kruskal']['H']:.4f}, p={res['kruskal']['p']:.4e}")
            else:
                st.write("Kruskal–Wallis: not available")

    with right:
        st.header("Visualizations")
        st.subheader(f"{metric} boxplot by country")
        fig_box = utils.plot_boxplot(df_display, metric)
        st.pyplot(fig_box)

        st.subheader("Average metric ranking")
        fig_bar = utils.plot_avg_bar(df_all, metric)
        st.pyplot(fig_bar)

    st.markdown("---")
    st.markdown("Built with Streamlit — you can deploy this app on Streamlit Community Cloud by pointing to `app/main.py` and adding `requirements.txt` including `streamlit`. Ensure your cleaned CSVs are available in the deployed repo or loaded dynamically.")


if __name__ == "__main__":
    main()
