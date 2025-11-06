#!/usr/bin/env python3
"""Quick runner to compute summary table and statistical tests for GHI/DNI/DHI across countries and print results to terminal.
"""
import pandas as pd
from scipy import stats

paths = {
    'Benin': 'data/benin_clean.csv',
    'Togo': 'data/togo_clean.csv',
    'SierraLeone': 'data/sierraleone_clean.csv',
}

dfs = {}
for country, p in paths.items():
    df = pd.read_csv(p)
    df['country'] = country
    dfs[country] = df

# Concatenate selecting metrics if present
metrics = ['GHI','DNI','DHI']
all_available = {c: dfs[c][metrics].dropna(how='all') for c in dfs}

# Summary table
summary_rows = []
for country, df in all_available.items():
    row = {'country': country}
    for m in metrics:
        if m in df.columns:
            row[f'{m}_mean'] = df[m].mean()
            row[f'{m}_median'] = df[m].median()
            row[f'{m}_std'] = df[m].std()
        else:
            row[f'{m}_mean'] = row[f'{m}_median'] = row[f'{m}_std'] = None
    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows).set_index('country')
print('\nSummary table (mean, median, std)')
print(summary_df.round(4))

# Statistical tests on GHI
samples = [dfs[c]['GHI'].dropna().values for c in dfs]
country_order = list(dfs.keys())
print('\nCountries (order):', country_order)
try:
    f_stat, p_anova = stats.f_oneway(*samples)
    print(f'ANOVA: F={f_stat:.4f}, p={p_anova:.4e}')
except Exception as e:
    print('ANOVA failed:', e)

try:
    h_stat, p_kruskal = stats.kruskal(*samples)
    print(f'Kruskal-Wallis: H={h_stat:.4f}, p={p_kruskal:.4e}')
except Exception as e:
    print('Kruskal-Wallis failed:', e)

# Ranking by average GHI
avg_ghi = summary_df['GHI_mean'].sort_values(ascending=False)
print('\nAverage GHI ranking:')
print(avg_ghi.round(4))
