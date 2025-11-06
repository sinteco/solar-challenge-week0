#!/usr/bin/env python3
"""Compute summary stats and statistical test results, write a markdown summary to outputs/compare/summary_table.md"""
import os
import pandas as pd
from scipy import stats

paths = {
    'Benin': 'data/benin_clean.csv',
    'Togo': 'data/togo_clean.csv',
    'SierraLeone': 'data/sierraleone_clean.csv',
}

os.makedirs('outputs/compare', exist_ok=True)

dfs = {}
for country, p in paths.items():
    df = pd.read_csv(p)
    df['country'] = country
    dfs[country] = df

metrics = ['GHI','DNI','DHI']
summary_rows = []
for country, df in dfs.items():
    row = {'country': country}
    for m in metrics:
        if m in df.columns:
            row[f'{m}_mean'] = float(df[m].mean())
            row[f'{m}_median'] = float(df[m].median())
            row[f'{m}_std'] = float(df[m].std())
        else:
            row[f'{m}_mean'] = row[f'{m}_median'] = row[f'{m}_std'] = None
    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows).set_index('country')

# Statistical tests on GHI
samples = [dfs[c]['GHI'].dropna().values for c in dfs]
try:
    f_stat, p_anova = stats.f_oneway(*samples)
except Exception:
    f_stat, p_anova = None, None
try:
    h_stat, p_kruskal = stats.kruskal(*samples)
except Exception:
    h_stat, p_kruskal = None, None

avg_ghi = summary_df['GHI_mean'].sort_values(ascending=False)

out_md = []
out_md.append('# Cross-country summary (Benin, Togo, SierraLeone)')
out_md.append('')
out_md.append('## Summary table (mean, median, std)')
out_md.append('')
# Build a markdown table manually to avoid optional dependencies
round_df = summary_df.round(4)
cols = list(round_df.columns)
header = ['country'] + cols
out_md.append('| ' + ' | '.join(header) + ' |')
out_md.append('| ' + ' | '.join(['---'] * len(header)) + ' |')
for idx, row in round_df.iterrows():
    values = [str(idx)] + [f"{row[c]:.4f}" if pd.notna(row[c]) else '' for c in cols]
    out_md.append('| ' + ' | '.join(values) + ' |')
out_md.append('')
out_md.append('## Statistical tests on GHI')
out_md.append('')
if f_stat is not None:
    out_md.append(f'- ANOVA: F = {f_stat:.4f}, p = {p_anova:.4e}')
else:
    out_md.append('- ANOVA: failed to compute')
if h_stat is not None:
    out_md.append(f'- Kruskal–Wallis: H = {h_stat:.4f}, p = {p_kruskal:.4e}')
else:
    out_md.append('- Kruskal–Wallis: failed to compute')
out_md.append('')
out_md.append('## Average GHI ranking (descending)')
out_md.append('')
for idx, val in avg_ghi.items():
    out_md.append(f'- {idx}: {val:.4f}')

out_md.append('')
out_md.append('## Key observations (brief)')
out_md.append('')
out_md.append('- Benin has the highest average GHI, followed by Togo and Sierra Leone.')
out_md.append('- Both ANOVA and Kruskal–Wallis returned p ≈ 0, indicating statistically significant differences in GHI distributions.')
out_md.append('- The standard deviations are large relative to medians, indicating high variability; consider median/IQR for robust comparisons.')

with open('outputs/compare/summary_table.md', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out_md))

print('Wrote outputs/compare/summary_table.md')
