import os
import re
import subprocess
from datetime import date

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from fontTools.ttLib import TTCollection
import tempfile
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

_ttf = os.path.join(tempfile.gettempdir(), 'wqy_report.ttf')
TTCollection('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc').fonts[0].save(_ttf)
pdfmetrics.registerFont(TTFont('CJK', _ttf))
FONT = 'CJK'

STY_TITLE = ParagraphStyle('t', fontName=FONT, fontSize=20, leading=26, spaceAfter=4)
STY_SUB = ParagraphStyle('sub', fontName=FONT, fontSize=10, leading=14,
                         textColor=colors.HexColor('#555555'), spaceAfter=10)
STY_H2 = ParagraphStyle('h2', fontName=FONT, fontSize=14, leading=18,
                        spaceBefore=12, spaceAfter=6, textColor=colors.HexColor('#1F4E79'))
STY_BODY = ParagraphStyle('b', fontName=FONT, fontSize=10.5, leading=16)
STY_SMALL = ParagraphStyle('s', fontName=FONT, fontSize=8.5, leading=12,
                           textColor=colors.HexColor('#666666'))

summary = pd.read_csv('analysis/summary.csv')
phase_summary = pd.read_csv('analysis/phase_summary.csv')
condition_summary = pd.read_csv('analysis/suite_condition_summary.csv')
suites = pd.read_csv('analysis/suite_summary.csv')
last3 = suites.tail(3).reset_index(drop=True)
n_cases = len(pd.read_csv(os.path.join('logs/test_runs', last3.iloc[-1]['file'])))


def actual_of(rel_path, case_id):
    df = pd.read_csv(os.path.join('logs/test_runs', rel_path))
    row = df[df['case_id'] == case_id]
    return '' if row.empty else str(row.iloc[0]['actual'])


alts, drifts, herrs, aerrs = [], [], [], []
for f in last3['file']:
    m5 = re.search(r'alt ([\d.]+)-([\d.]+) m, drift ([\d.]+) m', actual_of(f, 'TC-05'))
    if m5:
        alts += [float(m5.group(1)), float(m5.group(2))]
        drifts.append(float(m5.group(3)))
    m6 = re.search(r'h_err=([\d.]+) m, alt_err=([\d.]+) m', actual_of(f, 'TC-06'))
    if m6:
        herrs.append(float(m6.group(1)))
        aerrs.append(float(m6.group(2)))

fixed = summary[summary['dt_mean_s'].round(2) == 1.00]
try:
    commit = subprocess.check_output(
        ['git', 'rev-parse', '--short=7', 'HEAD'], text=True).strip()
except Exception:
    commit = 'unknown'

story = []
story.append(Paragraph('PX4 无人机自主飞行与自动化测试平台', STY_TITLE))
story.append(Paragraph(
    f'数据与图表摘要 · 生成于 {date.today():%Y-%m-%d} · commit {commit}',
    STY_SUB,
))
story.append(Paragraph(
    '基于 PX4 SITL + Gazebo 的无人机仿真自主飞行与自动化测试平台。'
    '本页汇总真实运行产生的测试结果与遥测数据，所有指标均来自仓库中的 CSV 与运行日志。',
    STY_BODY))

story.append(Paragraph('一、关键指标（来自连续 3 轮测试）', STY_H2))
metrics = [
    ['指标', '数值', '数据来源'],
    ['测试用例', f'{n_cases} 项 × {len(last3)} 轮 = {n_cases * len(last3)} 次判定',
     'logs/test_runs/*_suite.csv'],
    ['判定结果', f'{int(last3["passed"].sum())}/{int(last3["total"].sum())} PASS', '同上'],
    ['悬停高度', f'{min(alts):.2f}–{max(alts):.2f} m（目标 2.5 m）', 'TC-05'],
    ['悬停水平漂移', f'≤ {max(drifts):.2f} m', 'TC-05'],
    ['航点水平误差', f'{min(herrs):.2f}–{max(herrs):.2f} m', 'TC-06'],
    ['航点高度误差', f'≤ {max(aerrs):.2f} m', 'TC-06'],
    ['遥测最大相对高度', f'{summary["alt_max_m"].max():.2f} m', '有效遥测汇总'],
    ['实际采样间隔范围',
     (f'{fixed["dt_min_s"].min():.2f}–{fixed["dt_max_s"].max():.2f} s' if len(fixed) else 'n/a'),
     'telemetry_logger.py'],
    ['遥测样本', f'{int(summary["samples"].sum())} 条 / {len(summary)} 份文件', 'analysis/summary.csv'],
    ['空中悬停 P95 水平漂移',
     f'{float(phase_summary.loc[phase_summary["phase"] == "airborne_hold", "drift_p95_m"].iloc[0]):.3f} m',
     'analysis/phase_summary.csv'],
]
table = Table(metrics, colWidths=[42 * mm, 78 * mm, 52 * mm])
table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), FONT),
    ('FONTSIZE', (0, 0), (-1, -1), 9.5),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DCE6F1')),
    ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
story.append(table)

story.append(Paragraph('二、飞行数据图表', STY_H2))
img1 = 'analysis/figures/altitude_curve.png'
img2 = 'analysis/figures/flight_kinematics.png'
if os.path.exists(img1):
    story.append(Image(img1, width=170 * mm, height=76 * mm))
if os.path.exists(img2):
    story.append(Spacer(1, 4))
    story.append(Image(img2, width=170 * mm, height=136 * mm))

story.append(Paragraph('三、P95 与条件对比', STY_H2))
story.append(Paragraph(
    'P95 表示排序后的第 95 百分位，用来说明接近尾部的风险水平，'
    '同时避免单个极端样本完全主导结论。',
    STY_BODY,
))
phase_rows = [['飞行阶段', '文件数', '样本数', '高度 P95 (m)',
               '漂移 P95 (m)', '|垂直速度| P95 (m/s)']]
for _, r in phase_summary.iterrows():
    phase_rows.append([
        r['phase'], int(r['files']), int(r['samples']),
        f'{r["alt_p95_m"]:.3f}', f'{r["drift_p95_m"]:.3f}',
        f'{r["vz_abs_p95_mps"]:.3f}',
    ])
phase_table = Table(phase_rows, colWidths=[38 * mm, 20 * mm, 22 * mm,
                                          30 * mm, 30 * mm, 32 * mm])
phase_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), FONT),
    ('FONTSIZE', (0, 0), (-1, -1), 8.5),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DCE6F1')),
    ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(phase_table)
story.append(Spacer(1, 6))
phase_img = 'analysis/figures/phase_comparison.png'
if os.path.exists(phase_img):
    story.append(Image(phase_img, width=170 * mm, height=63 * mm))

story.append(PageBreak())
condition_rows = [['测试条件', '运行数', '判定数', '通过', '通过率']]
for _, r in condition_summary.iterrows():
    condition_rows.append([
        r['condition'], int(r['runs']), int(r['decisions']),
        int(r['passed']), f'{r["pass_rate_pct"]:.1f}%',
    ])
condition_table = Table(condition_rows, colWidths=[72 * mm, 25 * mm,
                                                  25 * mm, 22 * mm, 28 * mm])
condition_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), FONT),
    ('FONTSIZE', (0, 0), (-1, -1), 8.5),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2EFDA')),
    ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(condition_table)
story.append(Spacer(1, 6))
condition_img = 'analysis/figures/condition_comparison.png'
if os.path.exists(condition_img):
    story.append(Image(condition_img, width=140 * mm, height=84 * mm))

story.append(Paragraph('四、测试运行汇总（最近 3 轮）', STY_H2))
rows = [['运行文件', '通过/总数', '失败用例']]
for _, r in last3.iterrows():
    rows.append([r['file'], f'{int(r["passed"])}/{int(r["total"])}',
                 str(r['failed_cases']) if isinstance(r['failed_cases'], str) else ''])
run_table = Table(rows, colWidths=[92 * mm, 30 * mm, 50 * mm])
run_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), FONT),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2EFDA')),
    ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(run_table)

story.append(Paragraph('五、数据文件说明', STY_H2))
story.append(Paragraph(
    'logs/test_runs/*_telemetry.csv：定频遥测（时间、位置、速度、姿态、解锁状态、飞行模式）<br/>'
    'logs/test_runs/*_first_flight.csv：首次真实飞行记录（59 条）<br/>'
    'logs/test_runs/*_suite.csv / *.log：测试套件判定结果与运行日志<br/>'
    'analysis/summary.csv：每份遥测的最大值、P95 与数据质量检查<br/>'
    'analysis/phase_summary.csv：按飞行阶段汇总的 P95 指标<br/>'
    'analysis/suite_summary.csv：全部套件运行的历史汇总<br/>'
    'analysis/suite_condition_summary.csv：按失败特征分组的通过率', STY_BODY))

story.append(Paragraph('六、局限与未决问题', STY_H2))
story.append(Paragraph(
    '1) 航点水平误差稳定在 0.92–0.93 m，疑为飞控「到位接受半径」，尚未验证（known_issues 1.13）。<br/>'
    '2) 2026-10-25 一份旧数据存在 68 秒采样空档，不可用于统计（1.14）。<br/>'
    '3) 首次连接偶发挂起，需要先清理残留连接再运行（1.10）。<br/>'
    '4) 全部结果为 SITL 仿真，未包含 HITL 或真机实验。', STY_BODY))
story.append(Spacer(1, 8))
story.append(Paragraph(
    '说明：以上数值均由仓库内真实 CSV / 日志计算，未做任何修饰或补造。', STY_SMALL))

out = 'analysis/PX4_项目数据与图表.pdf'
SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                  topMargin=16 * mm, bottomMargin=14 * mm,
                  title='PX4 UAV Data and Figures').build(story)
print('saved', out)
