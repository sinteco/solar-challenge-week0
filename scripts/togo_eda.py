#!/usr/bin/env python3
"""
EDA script for Togo dataset — copied from benin_eda.py and adjusted for file paths.
"""
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


def ensure_dirs():
    Path("data").mkdir(exist_ok=True)
    Path("outputs/togo").mkdir(parents=True, exist_ok=True)


def load_data():
    candidates = [
        Path("data/togo.csv"),
        Path("data/togo_clean.csv"),
        Path("notebooks/data/togo_clean.csv"),
        Path("notebooks/data/togo.csv"),
    ]
    for p in candidates:
        if p.exists():
            print(f"Loading {p}")
            df = pd.read_csv(p, parse_dates=["Timestamp"] if "Timestamp" in pd.read_csv(p, nrows=1).columns else None)
            return df
    raise FileNotFoundError("No togo CSV found in expected locations. Put raw data at data/togo.csv")


def summary_stats(df):
    num = df.select_dtypes(include=[np.number])
    desc = num.describe().transpose()
    return desc


def missing_report(df):
    total = len(df)
    na = df.isna().sum()
    pct = (na / total) * 100
    report = pd.DataFrame({"missing_count": na, "missing_pct": pct})
    cols_over_5 = report[report["missing_pct"] > 5].sort_values("missing_pct", ascending=False)
    return report, cols_over_5


def flag_outliers_zscore(df, cols):
    df = df.copy()
    outlier_cols = []
    for c in cols:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            z = np.abs(stats.zscore(df[c].dropna()))
            mask = False
            if len(z) > 0:
                mask = np.abs(stats.zscore(df[c].fillna(df[c].median()))) > 3
            else:
                mask = np.zeros(len(df), dtype=bool)
            df[f"{c}_zflag"] = mask
            outlier_cols.append((c, int(mask.sum())))
    zflags = [col for col in df.columns if col.endswith("_zflag")]
    if zflags:
        df["any_z_outlier"] = df[zflags].any(axis=1)
    else:
        df["any_z_outlier"] = False
    return df, outlier_cols


def impute_median(df, cols):
    df = df.copy()
    medians = {}
    for c in cols:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            med = df[c].median()
            medians[c] = med
            df[c] = df[c].fillna(med)
    return df, medians


def save_report(text, filename="outputs/togo/report.txt"):
    with open(filename, "w") as f:
        f.write(text)


def make_plots(df):
    outdir = Path("outputs/togo")
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df = df.sort_values("Timestamp")

    ts_cols = [c for c in ["GHI", "DNI", "DHI", "Tamb"] if c in df.columns]
    if ts_cols and "Timestamp" in df.columns:
        plt.figure(figsize=(12, 6))
        for c in ts_cols:
            plt.plot(df["Timestamp"], df[c], label=c, alpha=0.8)
        plt.legend()
        plt.title("Time series of irradiance and temperature")
        plt.xlabel("Timestamp")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.savefig(outdir / "timeseries_ghi_dni_dhi_tamb.png")
        plt.close()

    if "Timestamp" in df.columns:
        df["month"] = df["Timestamp"].dt.month
        monthly = df.groupby("month")[ts_cols].mean()
        if not monthly.empty:
            monthly.plot(kind="bar", figsize=(10, 5))
            plt.title("Average by month")
            plt.tight_layout()
            plt.savefig(outdir / "monthly_avg.png")
            plt.close()

    corr_cols = [c for c in ["GHI", "DNI", "DHI", "ModA", "ModB", "Tamb"] if c in df.columns]
    if corr_cols:
        corr = df[corr_cols].corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
        plt.title("Correlation heatmap")
        plt.tight_layout()
        plt.savefig(outdir / "correlation_heatmap.png")
        plt.close()

    if "GHI" in df.columns:
        for v in ["WS", "WSgust", "WD"]:
            if v in df.columns:
                plt.figure(figsize=(6, 4))
                sns.scatterplot(x=df[v], y=df["GHI"], alpha=0.4)
                plt.title(f"{v} vs GHI")
                plt.tight_layout()
                plt.savefig(outdir / f"scatter_{v}_vs_GHI.png")
                plt.close()

    if "RH" in df.columns:
        if "Tamb" in df.columns:
            plt.figure(figsize=(6, 4))
            sns.scatterplot(x=df["RH"], y=df["Tamb"], alpha=0.4)
            plt.title("RH vs Tamb")
            plt.tight_layout()
            plt.savefig(outdir / "scatter_RH_vs_Tamb.png")
            plt.close()
        if "GHI" in df.columns:
            plt.figure(figsize=(6, 4))
            sns.scatterplot(x=df["RH"], y=df["GHI"], alpha=0.4)
            plt.title("RH vs GHI")
            plt.tight_layout()
            plt.savefig(outdir / "scatter_RH_vs_GHI.png")
            plt.close()

    if "WD" in df.columns and "WS" in df.columns:
        wd = df["WD"].dropna()
        ws = df.loc[wd.index, "WS"].fillna(0)
        bins = np.arange(0, 360, 30)
        inds = np.digitize(wd % 360, bins)
        counts = [ws[inds == i].mean() for i in range(1, len(bins)+1)]
        angles = np.deg2rad(bins + 15)
        plt.figure(figsize=(6, 6))
        ax = plt.subplot(111, polar=True)
        ax.bar(angles, counts, width=np.deg2rad(30), bottom=0.0)
        ax.set_title("Wind rose (mean WS per direction bin)")
        plt.tight_layout()
        plt.savefig(outdir / "wind_rose.png")
        plt.close()

    if "GHI" in df.columns:
        plt.figure(figsize=(6, 4))
        sns.histplot(df["GHI"].dropna(), bins=50)
        plt.title("Histogram of GHI")
        plt.tight_layout()
        plt.savefig(outdir / "hist_GHI.png")
        plt.close()
    if "WS" in df.columns:
        plt.figure(figsize=(6, 4))
        sns.histplot(df["WS"].dropna(), bins=50)
        plt.title("Histogram of WS")
        plt.tight_layout()
        plt.savefig(outdir / "hist_WS.png")
        plt.close()

    if "Cleaning" in df.columns and "ModA" in df.columns and "ModB" in df.columns:
        gp = df.groupby("Cleaning")[ ["ModA", "ModB"] ].mean()
        gp.plot(kind="bar", figsize=(8, 4))
        plt.title("Average ModA & ModB by Cleaning flag")
        plt.tight_layout()
        plt.savefig(outdir / "cleaning_impact.png")
        plt.close()

    if "GHI" in df.columns and "Tamb" in df.columns:
        size_col = "RH" if "RH" in df.columns else ("BP" if "BP" in df.columns else None)
        plt.figure(figsize=(8, 6))
        if size_col:
            sns.scatterplot(x=df["Tamb"], y=df["GHI"], size=df[size_col], legend=False, alpha=0.5)
        else:
            sns.scatterplot(x=df["Tamb"], y=df["GHI"], alpha=0.5)
        plt.title("GHI vs Tamb (bubble size = RH or BP)")
        plt.tight_layout()
        plt.savefig(outdir / "bubble_GHI_Tamb.png")
        plt.close()


def main():
    ensure_dirs()
    df = load_data()
    orig = df.copy()
    desc = summary_stats(df)
    missing, over5 = missing_report(df)
    key_cols = ["GHI", "DNI", "DHI", "ModA", "ModB", "WS", "WSgust"]
    df_flagged, outlier_summary = flag_outliers_zscore(df, key_cols)
    df_imputed, medians = impute_median(df_flagged, key_cols)
    clean_path = Path("data/togo_clean.csv")
    df_imputed.to_csv(clean_path, index=False)
    make_plots(df_imputed)
    lines = []
    lines.append("Togo EDA Report\n")
    lines.append("--- Summary statistics (numeric) ---\n")
    lines.append(desc.to_string())
    lines.append("\n--- Missing value report (count and pct) ---\n")
    lines.append(missing.to_string())
    lines.append("\n--- Columns with >5% missing ---\n")
    lines.append(over5.to_string())
    lines.append("\n--- Outlier summary (Z-score |z|>3) ---\n")
    for c, cnt in outlier_summary:
        lines.append(f"{c}: {cnt} flagged\n")
    lines.append("\n--- Median imputations applied ---\n")
    for k, v in medians.items():
        lines.append(f"{k}: median={v}\n")
    report_text = "\n".join(lines)
    save_report(report_text)
    print(report_text)


if __name__ == "__main__":
    main()
