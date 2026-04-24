# routes/student.py
from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash, send_file, current_app, make_response
from flask_login import login_required, current_user
from extensions import db
from models import Student, AcademicRecord, University
from utils import calculate_combination_code
import logic
import json
import os
import io
import charts  # Import our chart generation module

# ✅ FIX: Use __name__ (double underscores) for proper blueprint registration
student_bp = Blueprint('student', __name__, url_prefix='/student')

# ---- PUJAB booklet preview (image-rendered, download-restricted) ----
PUJAB_PDF_PATH = os.path.join('data', 'private', '(PUJAB) 2022-2023.pdf')


def _pujab_doc():
    """Open the PUJAB PDF lazily; returns (doc, page_count) or (None, 0)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None, 0
    if not os.path.exists(PUJAB_PDF_PATH):
        return None, 0
    doc = fitz.open(PUJAB_PDF_PATH)
    return doc, doc.page_count


@student_bp.route('/pujab-preview/page/<int:page>.png')
@login_required
def pujab_preview_page(page):
    """Render a single PUJAB page to PNG. Auth-gated; never exposes raw PDF."""
    doc, count = _pujab_doc()
    if doc is None or page < 1 or page > count:
        abort(404)
    try:
        # 2x zoom for crisp on-screen rendering without making downloads useful
        mat = __import__('fitz').Matrix(2.0, 2.0)
        pix = doc.load_page(page - 1).get_pixmap(matrix=mat, alpha=False)
        png_bytes = pix.tobytes('png')
    finally:
        doc.close()

    resp = make_response(png_bytes)
    resp.headers['Content-Type'] = 'image/png'
    # Force inline display, discourage caching/saving
    resp.headers['Content-Disposition'] = 'inline'
    resp.headers['Cache-Control'] = 'private, no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp


@student_bp.route('/portal')
@login_required
def portal():
    """Student Dashboard - Career eligibility report"""
    if current_user.role != 'Student':
        return redirect(url_for('admin.dashboard'))
    
    profile = Student.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return render_template('student_portal.html', student=None)
    
    # Prepare student data for logic module
    s_data = {
        'a_levels': json.loads(profile.a_level_json) if profile.a_level_json else {},
        'o_levels': json.loads(profile.o_level_json) if profile.o_level_json else {},
        'gender': profile.gender,
        'subs': profile.subsidiaries
    }
    
    report, o_bonus = logic.get_student_report(s_data)
    return render_template('student_portal.html', student=profile, report=report, o_bonus=o_bonus)


@student_bp.route('/about_institutions')
@login_required
def about_institutions():
    """List all universities for student reference"""
    universities = University.query.order_by(University.uni_type, University.name).all()
    return render_template('student/about_institutions.html', universities=universities)


@student_bp.route('/weighting_system')
@login_required
def weighting_system():
    """Explain the admission weighting calculation"""
    return render_template('student/weighting_system.html')


@student_bp.route('/how_to_apply')
@login_required
def how_to_apply():
    """Guide students through the application process"""
    doc, page_count = _pujab_doc()
    if doc is not None:
        doc.close()
    return render_template('student/how_to_apply.html', pujab_page_count=page_count)


@student_bp.route('/about_careers')
@login_required
def about_careers():
    """General careers office information"""
    return render_template('student/about_careers.html')


@student_bp.route('/my_courses')
@login_required
def my_courses():
    """Show eligibility for the student's selected course wishes plus alternative
    courses they're qualified for based on current weights."""
    if current_user.role != 'Student':
        return redirect(url_for('admin.dashboard'))

    profile = Student.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return render_template('student/my_courses.html', student=None)

    final_records = AcademicRecord.query.filter_by(student_id=profile.id, paper_code='FINAL').all()
    a_levels = {r.subject: r.grade for r in final_records}
    if not a_levels and profile.a_level_json:
        a_levels = json.loads(profile.a_level_json)

    s_data = {
        'a_levels': a_levels,
        'o_levels': json.loads(profile.o_level_json) if profile.o_level_json else {},
        'gender': profile.gender,
        'subs': profile.subsidiaries
    }
    full_report, o_bonus = logic.get_student_report(s_data)

    wishes_raw = json.loads(profile.course_wishes) if profile.course_wishes else []
    wishes_lower = [str(w).strip().lower() for w in wishes_raw]

    def is_wished(item):
        return (item['course'].lower() in wishes_lower) or (item['code'].lower() in wishes_lower)

    selected = [r for r in full_report if is_wished(r)]
    alternatives = [r for r in full_report
                    if r['status'] in ('Qualified', 'Borderline') and not is_wished(r)]

    return render_template(
        'student/my_courses.html',
        student=profile,
        selected=selected,
        alternatives=alternatives,
        wishes_raw=wishes_raw,
        a_levels=a_levels,
        o_bonus=o_bonus
    )


@student_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Student account settings (theme, profile)"""
    student = current_user.profile
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('student.portal'))

    # Parse current theme for pre-filling the form
    current_theme = json.loads(student.theme_pref) if student.theme_pref else {"type": "light"}

    if request.method == 'POST':
        action = request.form.get('action', 'update_theme')
        if action != 'update_theme':
            flash('This settings action is not enabled yet.', 'warning')
            return redirect(url_for('student.settings'))

        try:
            allowed = {'light', 'dark', 'neon', 'glass', 'aurora', 'sunset', 'custom'}
            theme_type = (request.form.get('theme_type', 'light') or 'light').strip()
            if theme_type not in allowed:
                theme_type = 'light'

            theme_data = {'type': theme_type}

            if theme_type == 'custom':
                bg = request.form.get('theme_bg') or request.form.get('custom_bg') or '#ffffff'
                text = request.form.get('theme_text') or request.form.get('custom_text') or '#333333'
                font = request.form.get('theme_font') or request.form.get('font_family') or 'Segoe UI'
                theme_data.update({'bg': bg, 'text': text, 'font': font})
            else:
                # allow font preference for all themes
                font = request.form.get('theme_font') or request.form.get('font_family')
                if font:
                    theme_data['font'] = font

            student.theme_pref = json.dumps(theme_data)
            db.session.commit()
            flash('✅ Theme preferences saved successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error saving settings: {str(e)}', 'danger')

        return redirect(url_for('student.settings'))

    return render_template('settings.html', student=student, current_theme=current_theme)


@student_bp.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    """
    Journey Tracker - Multi-subject grade entry + chart visualization.
    POST: Saves grades for all subjects in one term/exam.
    GET: Renders form + chart container.
    """
    su_preview = current_user.role == 'SuperUser'
    if current_user.role not in ['Student', 'SuperUser']:
        return abort(403)

    student = Student.query.filter_by(user_id=current_user.id).first() if current_user.role == 'Student' else None
    if current_user.role == 'Student' and not student:
        return abort(404)

    # ==========================================
    # HANDLE GRADE SUBMISSION (MULTI-SUBJECT FORM)
    # ==========================================
    if request.method == 'POST':
        if current_user.role != 'Student':
            flash('Preview mode: SuperUser cannot save individual student grades here.', 'warning')
            return redirect(url_for('student.tracker'))

        term = request.form.get('term', '').strip()
        exam_type = request.form.get('exam_type', '').strip()
        
        # Get subjects this student offers from their registration
        subjects_list = list(json.loads(student.a_level_json).keys()) if student.a_level_json else []
        
        if not subjects_list:
            flash('No subjects found for this student. Please contact admin.', 'warning')
            return redirect(url_for('student.tracker'))
        
        records_saved = 0
        # Loop through subjects by index to match form inputs (grade_1, grade_2, etc.)
        for i, subject_name in enumerate(subjects_list, start=1):
            grade = request.form.get(f'grade_{i}', '').strip().upper()
            
            # Only save if a grade was actually selected (non-empty)
            if grade and grade in ['A', 'B', 'C', 'D', 'E', 'O', 'F', 'N/A']:
                # Remove old record if exists (prevents duplicates on re-save)
                AcademicRecord.query.filter_by(
                    student_id=student.id,
                    term=term,
                    exam_type=exam_type,
                    subject=subject_name,
                    paper_code='FINAL'
                ).delete()
                
                # Insert new record
                db.session.add(AcademicRecord(
                    student_id=student.id,
                    term=term,
                    exam_type=exam_type,
                    subject=subject_name,
                    paper_code='FINAL',
                    grade=grade
                ))
                records_saved += 1
        
        if records_saved > 0:
            try:
                db.session.commit()
                flash(f'✅ Successfully saved {records_saved} grades for {term} ({exam_type}).', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving grades: {str(e)}', 'danger')
        else:
            flash('No valid grades selected to save.', 'warning')
        
        return redirect(url_for('student.tracker'))

    # ==========================================
    # RENDER PAGE WITH FORM DATA (GET Request)
    # ==========================================
    # Determine allowed terms based on student class level
    if student:
        class_level = student.class_level or "S.5"
        if "S.6" in class_level:
            allowed_terms = ["ALL", "S.6 Term 1", "S.6 Term 2", "S.6 Term 3"]
        else:
            allowed_terms = [
                "ALL",
                "S.5 Term 1", "S.5 Term 2", "S.5 Term 3",
                "S.6 Term 1", "S.6 Term 2", "S.6 Term 3"
            ]
    else:
        allowed_terms = [
            "ALL",
            "S.5 Term 1", "S.5 Term 2", "S.5 Term 3",
            "S.6 Term 1", "S.6 Term 2", "S.6 Term 3"
        ]

    # Get subjects offered by student (for form dropdowns)
    offered_subjects = list(json.loads(student.a_level_json).keys()) if (student and student.a_level_json) else []
    
    # Load Grade Options from options.json (fallback to defaults)
    options_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'options.json')
    a_grades = ['A', 'B', 'C', 'D', 'E', 'O', 'F']  # Default fallback
    try:
        if os.path.exists(options_path):
            with open(options_path, 'r', encoding='utf-8') as f:
                opts = json.load(f)
                a_grades = opts.get('a_grades', a_grades)
    except Exception as e:
        # Log error but don't break the page
        pass

    return render_template(
        'student/journey_tracker.html', 
        student=student, 
        allowed_terms=allowed_terms,
        offered_subjects=offered_subjects, 
        a_grades=a_grades,
        su_preview=su_preview
    )


@student_bp.route('/tracker/chart/<term>')
@login_required
def get_term_chart(term):
    """
    AJAX endpoint: Returns Base64 PNG chart + stats for the selected term.
    Chart shows: X=Exam Type (BOT/MT/EOT), Y=Grade Points, Lines=Subjects
    """
    if current_user.role not in ['Student', 'SuperUser']:
        return jsonify({}), 403

    if current_user.role == 'SuperUser':
        return jsonify({
            'image': None,
            'stats': {},
            'term': term,
            'preview': True
        })

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({}), 404
    
    try:
        # Call the Python chart generator (charts.py)
        img_base64, stats = charts.generate_performance_chart(student.id, term)
        return jsonify({
            'image': img_base64,
            'stats': stats,
            'term': term  # Echo back for frontend confirmation
        })
    except Exception as e:
        # Return placeholder on error
        return jsonify({
            'image': None,
            'stats': {},
            'error': str(e)
        }), 500


@student_bp.route('/predict')
@login_required
def predict():
    """
    AJAX endpoint: Returns eligibility report using grades from AcademicRecord table.
    Used for real-time prediction updates on the portal.
    """
    if current_user.role != 'Student':
        return jsonify({}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({}), 404
    
    # Use grades from the tracker (AcademicRecord) if available, else fall back to registration data
    final_records = AcademicRecord.query.filter_by(
        student_id=student.id, 
        paper_code='FINAL'
    ).all()
    
    calculated_a_levels = {r.subject: r.grade for r in final_records}
    
    # If no tracker records, use registration data as fallback
    if not calculated_a_levels and student.a_level_json:
        calculated_a_levels = json.loads(student.a_level_json)
    
    student_data = {
        'a_levels': calculated_a_levels,
        'o_levels': json.loads(student.o_level_json) if student.o_level_json else {},
        'gender': student.gender,
        'subs': student.subsidiaries
    }
    
    report, o_bonus = logic.get_student_report(student_data)
    return jsonify({
        'report': report, 
        'current_grades': calculated_a_levels,
        'o_bonus': o_bonus
    })