import glob
import os

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT_DIR = 'analysis'
FIG_DIR = os.path.join(OUT_DIR, 'figures')
MAX_DT_S = 5.0
os.makedirs(FIG_DIR, exist_ok=True)


def p95(series):
    return round(series.quantile(0.95), 3)


rows = []
phase_samples = {
    'ground_hold': [],
    'airborne_hold': [],
    'takeoff': [],
    'landing': [],
}
for path in sorted(glob.glob('logs/test_runs/*.csv')):
    df = pd.read_csv(path)
    need = {'t_s', 'rel_alt_m', 'north_m', 'east_m', 'vd', 'mode'}
    if not need.issubset(df.columns) or len(df) < 2:
        continue
    t = df['t_s']
    dt = t.diff().dropna()
    if dt.max() > MAX_DT_S:
        print(
            f'skip {os.path.basename(path)}: '
            f'telemetry gap {dt.max():.2f} s > {MAX_DT_S:.1f} s'
        )
        continue
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
        'alt_p95_m': p95(df['rel_alt_m']),
        'drift_max_m': round(drift.max(), 3),
        'drift_p95_m': p95(drift),
        'vz_max_abs_mps': round(df['vd'].abs().max(), 3),
        'vz_abs_p95_mps': p95(df['vd'].abs()),
        'modes': ';'.join(f'{k}:{v}' for k, v in modes.items()),
    })

    mode = df['mode'].fillna('').astype(str).str.upper()
    is_hold = mode.str.contains('HOLD')
    phase_masks = {
        'ground_hold': is_hold & (df['rel_alt_m'] < 0.2),
        'airborne_hold': is_hold & (df['rel_alt_m'] >= 2.0),
        'takeoff': mode.str.contains('TAKEOFF'),
        'landing': mode.str.contains('LAND'),
    }
    for phase, mask in phase_masks.items():
        for index in df.index[mask]:
            phase_samples[phase].append({
                'file': os.path.basename(path),
                'rel_alt_m': float(df.at[index, 'rel_alt_m']),
                'drift_m': float(drift.at[index]),
                'vz_abs_mps': float(abs(df.at[index, 'vd'])),
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

phase_rows = []
for phase, samples in phase_samples.items():
    if not samples:
        continue
    phase_df = pd.DataFrame(samples)
    phase_rows.append({
        'phase': phase,
        'files': phase_df['file'].nunique(),
        'samples': len(phase_df),
        'alt_p95_m': p95(phase_df['rel_alt_m']),
        'drift_p95_m': p95(phase_df['drift_m']),
        'vz_abs_p95_mps': p95(phase_df['vz_abs_mps']),
    })

phase_summary = pd.DataFrame(phase_rows)
phase_summary.to_csv(os.path.join(OUT_DIR, 'phase_summary.csv'), index=False)
print()
print('=== phase_summary.csv ===')
print(phase_summary.to_string(index=False))

if not phase_summary.empty:
    phase_order = ['ground_hold', 'airborne_hold', 'takeoff', 'landing']
    phase_summary['order'] = phase_summary['phase'].map(
        {name: index for index, name in enumerate(phase_order)}
    )
    phase_summary = phase_summary.sort_values('order')
    colors = ['#4c78a8', '#f58518', '#54a24b', '#e45756']
    plot_metrics = [
        ('alt_p95_m', 'P95 relative altitude (m)'),
        ('drift_p95_m', 'P95 horizontal drift (m)'),
        ('vz_abs_p95_mps', 'P95 absolute vertical speed (m/s)'),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
    labels = phase_summary['phase'].str.replace('_', ' ')
    for ax, (column, title) in zip(axes, plot_metrics):
        bars = ax.bar(labels, phase_summary[column],
                      color=colors[:len(phase_summary)])
        ax.set_title(title)
        ax.grid(True, axis='y', alpha=0.3)
        ax.tick_params(axis='x', rotation=15)
        for bar, samples in zip(bars, phase_summary['samples']):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f'n={samples}',
                    ha='center', va='bottom', fontsize=8)
    fig.suptitle('Telemetry comparison by flight phase')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'phase_comparison.png'), dpi=150)
    plt.close(fig)

srows = []
for path in sorted(glob.glob('logs/test_runs/*_suite.csv')):
    df = pd.read_csv(path)
    if 'verdict' not in df.columns:
        continue
    passed = int((df['verdict'] == 'PASS').sum())
    failed = set(df.loc[df['verdict'] != 'PASS', 'case_id'].astype(str))
    if len(df) < 7:
        condition = 'incomplete_run'
    elif not failed:
        condition = 'clean_pass'
    elif {'TC-05', 'TC-06'}.issubset(failed):
        condition = 'state_contamination'
    elif failed == {'TC-05'}:
        condition = 'hover_window_failure'
    else:
        condition = 'other_failure'
    srows.append({
        'file': os.path.basename(path),
        'condition': condition,
        'passed': passed,
        'total': len(df),
        'pass_rate_pct': round(100 * passed / len(df), 1),
        'failed_cases': ';'.join(sorted(failed)),
    })

sdf = pd.DataFrame(srows)
sdf.to_csv(os.path.join(OUT_DIR, 'suite_summary.csv'), index=False)
print()
print('=== suite_summary.csv ===')
print(sdf.to_string(index=False))

complete = sdf[sdf['condition'] != 'incomplete_run']
condition_summary = (
    complete.groupby('condition', as_index=False)
    .agg(runs=('file', 'count'),
         decisions=('total', 'sum'),
         passed=('passed', 'sum'))
)
condition_summary['pass_rate_pct'] = (
    100 * condition_summary['passed'] / condition_summary['decisions']
).round(1)
condition_summary.to_csv(
    os.path.join(OUT_DIR, 'suite_condition_summary.csv'),
    index=False,
)
print()
print('=== suite_condition_summary.csv ===')
print(condition_summary.to_string(index=False))

if not condition_summary.empty:
    display_names = {
        'clean_pass': 'Clean full suite',
        'hover_window_failure': 'Hover-window failure',
        'state_contamination': 'State contamination',
        'other_failure': 'Other failure',
    }
    condition_summary['label'] = (
        condition_summary['condition'].map(display_names)
    )
    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(
        condition_summary['label'],
        condition_summary['pass_rate_pct'],
        color=['#54a24b', '#f58518', '#e45756'][:len(condition_summary)],
    )
    ax.set_ylim(0, 110)
    ax.set_ylabel('Pass rate (%)')
    ax.set_title('Test-suite pass rate by observed condition')
    ax.grid(True, axis='y', alpha=0.3)
    for bar, row in zip(bars, condition_summary.itertuples()):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 2,
                f'{row.pass_rate_pct:.1f}%\n'
                f'{row.passed}/{row.decisions}, {row.runs} run(s)',
                ha='center', va='bottom', fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'condition_comparison.png'), dpi=150)
    plt.close(fig)
