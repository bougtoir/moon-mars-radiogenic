"""Minimal OMML (native Word equation) writer for python-docx.

Syntax inside math spans:
  x_i      -> subscript        x_i^a     -> sub+superscript
  x^a      -> superscript      {ab}      -> multi-char argument
  frac{a,b}-> stacked fraction (use sparingly in display eqs)
Everything else is emitted as math runs; unicode Greek letters are kept
as-is (native OMML stores them as literal characters).
"""
from docx.oxml import parse_xml
from docx.oxml.ns import qn
import re

M_NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'


def _esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _r(t):
    return f'<m:r><m:t xml:space="preserve">{_esc(t)}</m:t></m:r>'


def _sSub(b, e):
    return f'<m:sSub><m:e>{b}</m:e><m:sub>{e}</m:sub></m:sSub>'


def _sSup(b, e):
    return f'<m:sSup><m:e>{b}</m:e><m:sup>{e}</m:sup></m:sSup>'


def _sSubSup(b, s, e):
    return f'<m:sSubSup><m:e>{b}</m:e><m:sub>{s}</m:sub><m:sup>{e}</m:sup></m:sSubSup>'


def _frac(n, d):
    return f'<m:f><m:num>{n}</m:num><m:den>{d}</m:den></m:f>'


def _arg(expr, i):
    if i < len(expr) and expr[i] == '{':
        j = expr.index('}', i)
        return expr[i + 1:j], j + 1
    return expr[i], i + 1


def _tok(expr):
    items = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if expr.startswith('frac{', i):
            depth = 0
            j = i + 4
            while j < len(expr):
                if expr[j] == '{':
                    depth += 1
                elif expr[j] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = expr[i + 5:j]
            depth = 0
            k = inner.index(',')
            n, d = inner[:k], inner[k + 1:]
            items.append(('frac', (n.strip(), d.strip())))
            i = j + 1
        elif c == '_':
            a, i = _arg(expr, i + 1)
            items.append(('sub', a))
        elif c == '^':
            a, i = _arg(expr, i + 1)
            items.append(('sup', a))
        else:
            items.append(('r', c))
            i += 1
    return items


def _emit(items):
    frag = []  # entries: ('xml', s) or ('sSub', base, e)
    run = ''

    def flush():
        nonlocal run
        if run:
            frag.append(('xml', _r(run)))
            run = ''

    for t, v in items:
        if t == 'r':
            run += v
            continue
        flush()
        if t == 'frac':
            n, d = v
            frag.append(('xml', _frac(_emit(_tok(n)), _emit(_tok(d)))))
            continue
        base = frag.pop()[1] if frag else ''
        if t == 'sub':
            frag.append(('sSub', base, _r(v)))
        else:  # sup
            if frag and frag[-1][0] == 'sSub':
                _, b, e = frag.pop()
                frag.append(('xml', _sSubSup(b, e, _r(v))))
            else:
                frag.append(('xml', _sSup(base, _r(v))))
    flush()
    return ''.join(x[1] for x in frag)


def omath(expr):
    return f'<m:oMath>{_emit(_tok(expr))}</m:oMath>'


def add_display_eq(paragraph, expr):
    """Append a centred display equation (m:oMathPara) to a paragraph."""
    xml = (f'<m:oMathPara {M_NS}>'
           f'<m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr>'
           f'{omath(expr)}</m:oMathPara>')
    paragraph._p.append(parse_xml(xml))


def add_inline_eq(paragraph, expr):
    """Append an inline equation (m:oMath) to a paragraph."""
    paragraph._p.append(parse_xml(f'<m:oMath {M_NS}>{_emit(_tok(expr))}</m:oMath>'))


def add_mixed_paragraph(doc, text, style=None):
    """Add a paragraph; segments wrapped in \u27e6 \u27e7 become inline OMML."""
    p = doc.add_paragraph(style=style)
    parts = re.split(r'\u27e6(.*?)\u27e7', text)
    for k, seg in enumerate(parts):
        if not seg:
            continue
        if k % 2 == 0:
            p.add_run(seg)
        else:
            add_inline_eq(p, seg)
    return p


def count_omml(docx_path):
    import zipfile, re as _re
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read('word/document.xml').decode('utf8')
    return len(_re.findall(r'<m:oMath[ >]', xml)), len(_re.findall(r'<m:oMathPara', xml))
