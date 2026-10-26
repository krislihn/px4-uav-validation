import os
import re
import tempfile

from fontTools.ttLib import TTCollection
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

_ttf = os.path.join(tempfile.gettempdir(), 'wqy_docs.ttf')
TTCollection('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc').fonts[0].save(_ttf)
pdfmetrics.registerFont(TTFont('CJK', _ttf))
FONT = 'CJK'

S_TITLE = ParagraphStyle('t', fontName=FONT, fontSize=20, leading=26, spaceAfter=10)
S_H2 = ParagraphStyle('h2', fontName=FONT, fontSize=15, leading=20,
                      spaceBefore=12, spaceAfter=6, textColor=colors.HexColor('#1F4E79'))
S_H3 = ParagraphStyle('h3', fontName=FONT, fontSize=12.5, leading=17,
                      spaceBefore=8, spaceAfter=4, textColor=colors.HexColor('#2E5C8A'))
S_BODY = ParagraphStyle('b', fontName=FONT, fontSize=10, leading=16, spaceAfter=4)
S_BULLET = ParagraphStyle('bu', fontName=FONT, fontSize=10, leading=16,
                          leftIndent=12, spaceAfter=2)
S_CODE = ParagraphStyle('code', fontName=FONT, fontSize=8, leading=11,
                        backColor=colors.HexColor('#F2F2F2'), borderPadding=4,
                        leftIndent=6, spaceBefore=2, spaceAfter=6)
S_CELL = ParagraphStyle('cell', fontName=FONT, fontSize=8, leading=11)


def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def parse(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    blocks, i = [], 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s:
            i += 1
            continue
        if s.startswith('```'):
            j, code = i + 1, []
            while j < len(lines) and not lines[j].strip().startswith('```'):
                code.append(lines[j])
                j += 1
            blocks.append(('code', '\n'.join(code)))
            i = j + 1
            continue
        if s.startswith('!['):
            m = re.search(r'\((.*?)\)', s)
            if m:
                blocks.append(('image', m.group(1)))
            i += 1
            continue
        m = re.match(r'^(#{1,4})\s+(.*)$', s)
        if m:
            blocks.append(('h%d' % min(len(m.group(1)), 3), m.group(2)))
            i += 1
            continue
        if s.startswith('|') and i + 1 < len(lines):
            sep_cells = [c.strip() for c in lines[i + 1].strip().strip('|').split('|')]
            if sep_cells and all(c and set(c.replace(' ', '')) <= set('-:') for c in sep_cells):
                rows = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                    if not all(set(c.replace(' ', '')) <= set('-:') for c in cells):
                        rows.append(cells)
                    i += 1
                blocks.append(('table', rows))
                continue
        if s.startswith('- '):
            blocks.append(('bullet', s[2:]))
            i += 1
            continue
        if s.startswith('> '):
            blocks.append(('bullet', s[2:]))
            i += 1
            continue
        blocks.append(('p', s))
        i += 1
    return blocks


def build_block(block):
    kind, value = block
    if kind == 'h1':
        return [Paragraph(esc(value), S_TITLE)]
    if kind == 'h2':
        return [Paragraph(esc(value), S_H2)]
    if kind == 'h3':
        return [Paragraph(esc(value), S_H3)]
    if kind == 'bullet':
        return [Paragraph('• ' + esc(value), S_BULLET)]
    if kind == 'code':
        return [Paragraph(esc(value).replace('\n', '<br/>'), S_CODE)]
    if kind == 'image':
        if os.path.exists(value):
            pw, ph = PILImage.open(value).size
            w = 160 * mm
            return [Image(value, width=w, height=w * ph / pw), Spacer(1, 6)]
        return []
    if kind == 'table':
        rows = value
        if not rows:
            return []
        ncol = max(len(r) for r in rows)
        data = [[Paragraph(esc(c), S_CELL) for c in (r + [''] * (ncol - len(r)))]
                for r in rows]
        width = 172 * mm / ncol
        t = Table(data, colWidths=[width] * ncol, repeatRows=1)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DCE6F1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return [t, Spacer(1, 6)]
    return [Paragraph(esc(value), S_BODY)]


story = []
sources = [('README.md', '项目说明'), ('docs/technical_report.md', '技术报告'),
           ('docs/summary_en.md', 'English Summary')]
for idx, (path, name) in enumerate(sources):
    if idx > 0:
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
    for block in parse(path):
        story.extend(build_block(block))

out = 'analysis/PX4_项目完整文档.pdf'
SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                  topMargin=16 * mm, bottomMargin=14 * mm,
                  title='PX4 UAV Project Document').build(story)
print('saved', out)
