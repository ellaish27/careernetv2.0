import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from models import AcademicRecord
import re

GRADE_POINTS = {'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'O': 1, 'F': 0, 'N/A': 0}
EXAM_TYPES = ['BOT', 'MT', 'EOT']
SUBJECT_COLORS = {
    'Physics': '#8b5cf6', 'Mathematics': '#10b981', 'Math': '#10b981',
    'Chemistry': '#ef4444', 'Biology': '#22c55e', 'History': '#6366f1',
    'Geography': '#14b8a6', 'Economics': '#f97316', 'General Paper': '#ec4899',
    'GP': '#ec4899', 'TD': '#f59e0b', 'Sub ICT': '#0ea5e9', 'Subsidiary ICT': '#0ea5e9',
    'Technical Drawing': '#f59e0b', 'Subsidiary Mathematics': '#64748b'
}
DEFAULT_COLOR = '#64748b'

def generate_performance_chart(student_id, term):
    """Generates progress line chart per subject across Term + Exam timeline."""
    query = AcademicRecord.query.filter_by(student_id=student_id, paper_code='FINAL')
    if term and term != 'ALL':
        query = query.filter_by(term=term)
    records = query.all()
    if not records:
        return _placeholder("No records available"), {}

    term_set = sorted({r.term for r in records if r.term}, key=_term_sort_key)
    timeline = []
    for t in term_set:
        for ex in EXAM_TYPES:
            timeline.append((t, ex))
    if not timeline:
        return _placeholder("No BOT/MT/EOT records found"), {}

    # Organize: {subject: {(term, exam_type): points}}
    subject_data = {}
    exam_stats = {ex: [] for ex in EXAM_TYPES}
    for rec in records:
        if rec.exam_type in EXAM_TYPES and rec.term:
            pts = GRADE_POINTS.get(rec.grade.upper() if rec.grade else 'N/A', 0)
            key = (rec.term, rec.exam_type)
            subject_data.setdefault(rec.subject, {})
            subject_data[rec.subject][key] = pts
            exam_stats[rec.exam_type].append(pts)

    subjects = sorted(subject_data.keys())
    x = np.arange(len(timeline))
    fig, ax = plt.subplots(figsize=(max(10, len(timeline) * 1.25), max(4.6, len(subjects) * 0.42)), dpi=120)

    for sub in subjects:
        points = [subject_data[sub].get(tp, np.nan) for tp in timeline]
        color = SUBJECT_COLORS.get(sub, DEFAULT_COLOR)
        ax.plot(x, points, marker='o', linewidth=2.2, label=sub, color=color, markersize=5)
        
        for i, p in enumerate(points):
            if not np.isnan(p):
                grade_label = _point_to_grade(p)
                ax.text(i, p + 0.18, grade_label, ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=color)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{t}\n{e}" for (t, e) in timeline], fontsize=8)
    ax.set_ylabel('Grade Points (A=6 → F=0)', fontsize=10)
    title_suffix = term if term and term != 'ALL' else 'All Terms'
    ax.set_title(f'Performance Trends by Subject ({title_suffix})', fontsize=14, fontweight='bold', pad=15)
    ax.set_ylim(-0.5, 6.5)
    ax.set_xlim(-0.25, len(timeline) - 0.75)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax.xaxis.grid(True, linestyle=':', alpha=0.2)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=8.5, frameon=False)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    stats = {}
    for ex in EXAM_TYPES:
        pts = exam_stats[ex]
        stats[ex] = {
            "count": len(pts),
            "average": (sum(pts) / len(pts)) if pts else None
        }
    return base64.b64encode(buf.getvalue()).decode('utf8'), stats


def _term_sort_key(term_label):
    match = re.search(r'S\.(\d+)\s*Term\s*(\d+)', term_label or '', flags=re.IGNORECASE)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (99, 99)


def _point_to_grade(points):
    grade_by_points = {6: 'A', 5: 'B', 4: 'C', 3: 'D', 2: 'E', 1: 'O', 0: 'F'}
    return grade_by_points.get(int(points), '')

def _placeholder(msg):
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.text(0.5, 0.5, msg, ha='center', va='center', fontsize=12, color='gray', style='italic')
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf8')