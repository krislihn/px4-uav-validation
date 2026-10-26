import glob
import os

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT_DIR = 'analysis'
FIG_DIR = os.path.join(OUT_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

rows = []
for path in sorted(glob.glob('logs/test_runs/*.csv')):
    df = pd.read_csv(path)
    need = {'t_s', 'rel_alt_m', 'north_m', 'east_m', 'vd', 'mode'}
    if not need.issubset(df.columns) or len(df) < 2:
        continue
    t = df['t_s']
    dt = t.diff().dropna()
    n = df['north_m']
    e = df['east_m']
    drift = ((n - n.iloc[0]) ** 2 + (e - e.iloc[0]) ** 2) ** 0.5
    modes = df['mode'].fillna('').value_counts().to_dict()
    rows.append({
        'file': os.path.basename(path),
        'samples': len(df),
        'duration_s': round(t.iloc[-1] - t.iloc[0], 2),
        'dt_mean_s': round(dt.mean(), 3),
        'dt_min_s': round(dt.min(), 3),
        'dt_max_s': round(dt.max(), 3),
        'alt_min_m': round(df['rel_alt_m'].min(), 3),
        'alt_max_m': round(df['rel_alt_m'].max(), 3),
        'alt_mean_m': round(df['rel_alt_m'].mean(), 3),
        'alt_std_m': round(df['rel_alt_m'].std(), 3),
        'drift_max_m': round(drift.max(), 3),
        'vz_max_abs_mps': round(df['vd'].abs().max(), 3),
        'modes': ';'.join(f'{k}:{v}' for k, v in modes.items()),
    })

summary = pd.DataFrame(rows)
summary.to_csv(os.path.join(OUT_DIR, 'summary.csv'), index=False)
print('=== summary.csv ===')
print(summary.to_string(index=False))

if not summary.empty:
    best = summary.sort_values('alt_max_m', ascending=False).iloc[0]['file']
    df = pd.read_csv(os.path.join('logs/test_runs', best))
    plt.figure(figsize=(10, 4.5))
    plt.plot(df['t_s'], df['rel_alt_m'], linewidth=1.5)
    plt.title(f'Relative altitude vs time - {best}')
    plt.xlabel('time (s)')
    plt.ylabel('relative altitude (m)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'altitude_curve.png'), dpi=150)
    plt.close()

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(df['t_s'], df['rel_alt_m'])
    axes[0].set_ylabel('altitude (m)')
    axes[1].plot(df['t_s'], df['vd'])
    axes[1].set_ylabel('vertical speed (m/s)')
    drift = ((df['north_m'] - df['north_m'].iloc[0]) ** 2
             + (df['east_m'] - df['east_m'].iloc[0]) ** 2) ** 0.5
    axes[2].plot(df['t_s'], drift)
    axes[2].set_ylabel('horizontal drift (m)')
    axes[2].set_xlabel('time (s)')
    for ax in axes:
        ax.grid(True, alpha=0.3)
    fig.suptitle(f'Flight kinematics - {best}')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'flight_kinematics.png'), dpi=150)
    plt.close(fig)

srows = []
for path in sorted(glob.glob('logs/test_runs/*_suite.csv')):
    df = pd.read_csv(path)
    if 'verdict' not in df.columns:
        continue
    srows.append({
        'file': os.path.basename(path),
        'passed': int((df['verdict'] == 'PASS').sum()),
        'total': len(df),
        'failed_cases': ';'.join(df.loc[df['verdict'] != 'PASS', 'case_id'].astype(str)),
    })

sdf = pd.DataFrame(srows)
sdf.to_csv(os.path.join(OUT_DIR, 'suite_summary.csv'), index=False)
print()
print('=== suite_summary.csv ===')
print(sdf.to_string(index=False))
