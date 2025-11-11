"""Utility functions for the Streamlit dashboard.

This module contains data-loading, summary, statistical testing and plotting helpers.
The functions are small and documented so they can be reused both in the notebook and the app.
"""
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


def load_cleaned_datasets(paths: Dict[str, str]) -> pd.DataFrame:
    """Load cleaned CSVs into a single concatenated DataFrame.

    Parameters
    - paths: mapping country name -> csv path

    Returns
    - concatenated DataFrame with a 'country' column
    """
    dfs = []
    for country, p in paths.items():
        try:
            df = pd.read_csv(p)
        except FileNotFoundError:
            # skip missing files (app should handle missing data gracefully)
            continue
        df = df.copy()
        df["country"] = country
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def summary_table(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Return a summary table (mean, median, std) grouped by country for given metrics."""
    if df.empty:
        return pd.DataFrame()
    agg = df.groupby("country")[metrics].agg(["mean", "median", "std"]).round(4)
    # flatten columns
    agg.columns = [f"{m}_{stat}" for m, stat in agg.columns]
    return agg.reset_index()


def run_ghi_tests(df: pd.DataFrame) -> Tuple[dict, pd.DataFrame]:
    """Run ANOVA and Kruskal-Wallis on GHI grouped by country.

    Returns a dict with test statistics and p-values and the grouping order used.
    """
    result = {"anova": None, "kruskal": None}
    if df.empty or "GHI" not in df.columns:
        return result, pd.DataFrame()
    groups = [g["GHI"].dropna().values for _, g in df.groupby("country")]
    countries = [c for c, _ in df.groupby("country")]
    try:
        f_stat, p_anova = stats.f_oneway(*groups)
        result["anova"] = {"F": float(f_stat), "p": float(p_anova)}
    except Exception:
        result["anova"] = None
    try:
        h_stat, p_kruskal = stats.kruskal(*groups)
        result["kruskal"] = {"H": float(h_stat), "p": float(p_kruskal)}
    except Exception:
        result["kruskal"] = None
    # small DF for display
    order_df = df.groupby("country")["GHI"].mean().reset_index().sort_values("GHI", ascending=False)
    return result, order_df


def plot_boxplot(df: pd.DataFrame, metric: str, figsize=(8, 4)) -> plt.Figure:
    """Return a matplotlib Figure with a boxplot of metric by country."""
    fig, ax = plt.subplots(figsize=figsize)
    sns.boxplot(x="country", y=metric, data=df, palette="Set2", ax=ax)
    ax.set_title(f"{metric} distribution by country")
    ax.set_xlabel("")
    ax.set_ylabel(metric)
    plt.tight_layout()
    return fig


def plot_avg_bar(df: pd.DataFrame, metric: str, figsize=(6, 3)) -> plt.Figure:
    """Return a bar chart of average metric by country."""
    fig, ax = plt.subplots(figsize=figsize)
    avg = df.groupby("country")[metric].mean().sort_values(ascending=False)
    sns.barplot(x=avg.index, y=avg.values, palette="Set2", ax=ax)
    ax.set_ylabel(f"Average {metric}")
    ax.set_title(f"Average {metric} by country")
    for i, v in enumerate(avg.values):
        ax.text(i, v + 0.01 * max(avg.values), f"{v:.3f}", ha="center")
    plt.tight_layout()
    return fig
