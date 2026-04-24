import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import io
import base64
from models import AcademicRecord
import re

GRADE_POINTS = {'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'O': 1, 'F': 0, 'N/A': 0}
EXAM_TYPES = ['BOT', 'MT', 'EOT']

# Polished, accessible palette (avoid red/green clash for color-blind users)
SUBJECT_COLORS = {
    'Physics': '#7c3aed', 'Mathematics': '#0ea5e9', 'Math': '#0ea5e9',
    'Chemistry': '#ef4444', 'Biology': '#16a34a', 'History': '#6366f1',
    'Geography': '#0d9488', 'Economics': '#f97316', 'General Paper': '#db2777',
    'GP': '#db2777', 'TD': '#f59e0b', 'Sub ICT': '#0284c7',
    'Subsidiary ICT': '#0284c7', 'Technical Drawing': '#f59e0b',
    'Subsidiary Mathematics': '#475569',
}
DEFAULT_PALETTE = ['#1d4ed8', '#dc2626', '#059669', '#9333ea', '#ea580c',
                   '#0891b2', '#be185d', '#65a30d', '#475569', '#7c2d12']

# Background bands for grade ranges (helps the eye read the chart at a glance)
GRADE_BANDS = [
    (5.5, 6.5, '#dcfce7', 'A'),   # green
    (4.5, 5.5, '#ecfccb', 'B'),
    (3.5, 4.5, '#fef9c3', 'C'),   # yellow
    (2.5, 3.5, '#ffedd5', 'D'),
    (1.5, 2.5, '#fee2e2', 'E'),   # light red
    (-0.5, 1.5, '#fecaca', 'O/F'),
]


def _color_for(subject, idx):
    return SUBJECT_COLORS.get(subject, DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)])


def generate_performance_chart(student_id, term):
    """Generate a polished progress line chart per subject across Term + Exam timeline.

    Returns (base64_png, stats_dict).
    """
    query = AcademicRecord.query.filter_by(student_id=student_id, paper_code='FINAL')
    if term and term != 'ALL':
        query = query.filter_by(term=term)
    records = query.all()
    if not records:
        return _placeholder("No grades recorded yet — add some on the form above."), {}

    term_set = sorted({r.term for r in records if r.term}, key=_term_sort_key)
    timeline = [(t, ex) for t in term_set for ex in EXAM_TYPES]
    if not timeline:
        return _placeholder("No BOT / MT / EOT records found for this term."), {}

    # Organize: {subject: {(term, exam_type): points}}
    subject_data = {}
    exam_stats = {ex: [] for ex in EXAM_TYPES}
    for rec in records:
        if rec.exam_type in EXAM_TYPES and rec.term:
            pts = GRADE_POINTS.get(rec.grade.upper() if rec.grade else 'N/A', 0)
            subject_data.setdefault(rec.subject, {})[(rec.term, rec.exam_type)] = pts
            exam_stats[rec.exam_type].append(pts)

    subjects = sorted(subject_data.keys())
    x = np.arange(len(timeline))

    # Figure / axis ----------------------------------------------------------
    fig_w = max(10.5, len(timeline) * 1.35)
    fig_h = max(5.0, 4.6 + len(subjects) * 0.18)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=120,
                           facecolor='#ffffff')
    ax.set_facecolor('#f8fafc')

    # Grade-band shading -----------------------------------------------------
    xmin, xmax = -0.4, len(timeline) - 0.6
    for low, high, color, label in GRADE_BANDS:
        ax.add_patch(Rectangle((xmin, low), xmax - xmin, high - low,
                               facecolor=color, edgecolor='none',
                               alpha=0.55, zorder=0))
        # right-side label
        ax.text(xmax + 0.05, (low + high) / 2, label,
                va='center', ha='left', fontsize=8.5, color='#475569',
                fontweight='bold', alpha=0.85, zorder=1)

    # Plot each subject as a smooth line -------------------------------------
    for idx, sub in enumerate(subjects):
        points = np.array([subject_data[sub].get(tp, np.nan) for tp in timeline],
                          dtype=float)
        color = _color_for(sub, idx)
        # subtle shadow line behind for depth
        ax.plot(x, points, color=color, alpha=0.18, linewidth=6.5, zorder=2,
                solid_capstyle='round')
        # main line
        ax.plot(x, points, marker='o', markersize=7, linewidth=2.4,
                label=sub, color=color, zorder=3,
                markeredgecolor='white', markeredgewidth=1.2)

        # value labels (grade letter)
        for i, p in enumerate(points):
            if not np.isnan(p):
                ax.annotate(_point_to_grade(p),
                            xy=(i, p), xytext=(0, 9),
                            textcoords='offset points',
                            ha='center', fontsize=8, fontweight='bold',
                            color=color,
                            bbox=dict(boxstyle='round,pad=0.18',
                                      facecolor='white', edgecolor=color,
                                      linewidth=0.6, alpha=0.9), zorder=4)

    # Axes / styling ---------------------------------------------------------
    ax.set_xticks(x)
    ax.set_xticklabels([f"{_short_term(t)}\n{e}" for (t, e) in timeline],
                       fontsize=8.5, color='#1e293b')
    ax.set_ylabel('Grade Points  (A=6  →  F=0)', fontsize=10.5,
                  color='#334155', fontweight='semibold')

    title_suffix = term if term and term != 'ALL' else 'All Terms'
    ax.set_title(f'Academic Performance Trend — {title_suffix}',
                 fontsize=15, fontweight='bold', pad=16, color='#0f172a')

    ax.set_ylim(-0.5, 6.7)
    ax.set_xlim(xmin, xmax + 0.35)
    ax.set_yticks([0, 1, 2, 3, 4, 5, 6])
    ax.set_yticklabels(['F (0)', 'O (1)', 'E (2)', 'D (3)', 'C (4)', 'B (5)', 'A (6)'],
                       fontsize=8.5, color='#475569')
    ax.yaxis.grid(True, linestyle='--', alpha=0.35, color='#94a3b8')
    ax.xaxis.grid(False)
    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)
    for spine in ('left', 'bottom'):
        ax.spines[spine].set_color('#cbd5e1')

    # Term separators — vertical dotted lines between terms
    if len(term_set) > 1:
        for i in range(1, len(term_set)):
            ax.axvline(i * len(EXAM_TYPES) - 0.5, color='#94a3b8',
                       linestyle=':', alpha=0.6, zorder=1)

    # Legend — outside on the right, below the band labels
    leg = ax.legend(loc='upper left', bbox_to_anchor=(1.045, 1.0),
                    fontsize=9, frameon=True, framealpha=0.95,
                    facecolor='white', edgecolor='#e2e8f0',
                    title='Subjects', title_fontsize=10)
    leg.get_title().set_color('#0f172a')

    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

    stats = {}
    for ex in EXAM_TYPES:
        pts = exam_stats[ex]
        stats[ex] = {
            'count': len(pts),
            'average': (sum(pts) / len(pts)) if pts else None,
        }
    return base64.b64encode(buf.getvalue()).decode('utf8'), stats


# ---- helpers ---------------------------------------------------------------

def _term_sort_key(term_label):
    match = re.search(r'S\.(\d+)\s*Term\s*(\d+)', term_label or '', flags=re.IGNORECASE)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (99, 99)


def _short_term(term_label):
    """Compact term label e.g. 'S.5 Term 1' -> 'S5 T1'."""
    m = re.search(r'S\.?(\d+)\s*Term\s*(\d+)', term_label or '', flags=re.IGNORECASE)
    if m:
        return f"S{m.group(1)} T{m.group(2)}"
    return term_label or ''


def _point_to_grade(points):
    grade_by_points = {6: 'A', 5: 'B', 4: 'C', 3: 'D', 2: 'E', 1: 'O', 0: 'F'}
    return grade_by_points.get(int(round(points)), '')


def _placeholder(msg):
    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=120, facecolor='#ffffff')
    ax.set_facecolor('#f8fafc')
    ax.text(0.5, 0.55, '📊', ha='center', va='center', fontsize=42, color='#94a3b8')
    ax.text(0.5, 0.28, msg, ha='center', va='center',
            fontsize=12, color='#475569', style='italic')
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf8')
