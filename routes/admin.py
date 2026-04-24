# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from extensions import db
from models import Student, User, AcademicRecord
from utils import admin_required, calculate_combination_code
import logic
import json
import csv
import io
from werkzeug.security import generate_password_hash

# ✅ FIX: Use __name__ (double underscores) for proper blueprint registration
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin Dashboard - List all students and courses"""
    if current_user.role == 'Student':
        return redirect(url_for('student.portal'))
    
    students = Student.query.order_by(Student.name).all()
    courses = logic.COURSE_DATABASE
    
    return render_template('dashboard.html', students=students, user=current_user, courses=courses)


@admin_bp.route('/create_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    """Create a new Administrator account"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" already exists.', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        if email and '@' not in email:
            flash('Please enter a valid email address (or leave it blank).', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        try:
            hashed_pw = generate_password_hash(password, method='scrypt')
            new_user = User(username=username, password=hashed_pw, role='Administrator', email=email or None)
            db.session.add(new_user)
            db.session.commit()
            flash(f'Admin "{username}" created successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating admin: {str(e)}', 'danger')
        
        return redirect(url_for('admin.dashboard'))
    
    return render_template('create_admin.html')


@admin_bp.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    """Edit student profile and academic records"""
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        # Update basic info
        student.name = request.form.get('name', '').strip()
        student.gender = request.form.get('gender', 'M')
        student.combination = request.form.get('combination', '').strip()
        student.subsidiaries = int(request.form.get('subsidiaries', 0))
        
        # Update O-Level results
        o_subs = request.form.getlist('o_sub')
        o_grades = request.form.getlist('o_grade')
        o_data = {o_subs[i]: o_grades[i] for i in range(len(o_subs)) if o_subs[i] and o_grades[i]}
        student.o_level_json = json.dumps(o_data)
        
        # Update A-Level results
        a_subs = request.form.getlist('a_sub')
        a_grades = request.form.getlist('a_grade')
        a_data = {a_subs[i]: a_grades[i] for i in range(len(a_subs)) if a_subs[i] and a_grades[i]}
        student.a_level_json = json.dumps(a_data)
        
        # Recalculate combination code
        student.combination = calculate_combination_code(student)
        
        db.session.commit()
        flash(f'Student "{student.name}" updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # GET request - load form with existing data
    o_data = json.loads(student.o_level_json) if student.o_level_json else {}
    a_data = json.loads(student.a_level_json) if student.a_level_json else {}
    
    return render_template('edit_student.html', student=student, o_data=o_data, a_data=a_data)


@admin_bp.route('/student/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    """Add a new student profile"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', 'M')
        combination = request.form.get('combination', '').strip()
        class_level = request.form.get('class_level', 'S.5')
        
        if not name:
            flash('Student name is required.', 'danger')
            return redirect(url_for('admin.add_student'))
        
        # Build O-Level JSON
        o_subs = request.form.getlist('o_sub')
        o_grades = request.form.getlist('o_grade')
        o_data = {o_subs[i]: o_grades[i] for i in range(len(o_subs)) if o_subs[i] and o_grades[i]}
        
        # Build A-Level JSON
        a_subs = request.form.getlist('a_sub')
        a_grades = request.form.getlist('a_grade')
        a_data = {a_subs[i]: a_grades[i] for i in range(len(a_subs)) if a_subs[i] and a_grades[i]}
        
        new_student = Student(
            name=name,
            gender=gender,
            combination=combination,
            class_level=class_level,
            o_level_json=json.dumps(o_data),
            a_level_json=json.dumps(a_data),
            subsidiaries=int(request.form.get('subsidiaries', 0))
        )
        
        db.session.add(new_student)
        db.session.commit()
        flash(f'Student "{name}" added successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('add_student.html')


@admin_bp.route('/teacher/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_teacher():
    """Add a new teacher account (stored as User with role='Teacher')"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin.add_teacher'))
        
        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" already exists.', 'danger')
            return redirect(url_for('admin.add_teacher'))
        
        try:
            hashed_pw = generate_password_hash(password, method='scrypt')
            new_user = User(username=username, password=hashed_pw, role='Teacher')
            db.session.add(new_user)
            db.session.commit()
            flash(f'Teacher "{username}" added successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        
        return redirect(url_for('admin.dashboard'))
    
    return render_template('add_teacher.html')


@admin_bp.route('/analyze/<int:student_id>')
@login_required
@admin_required
def analyze(student_id):
    """Analyze a student's eligibility for courses"""
    student = Student.query.get_or_404(student_id)
    
    # Prepare student data for logic module
    s_data = {
        'a_levels': json.loads(student.a_level_json) if student.a_level_json else {},
        'o_levels': json.loads(student.o_level_json) if student.o_level_json else {},
        'gender': student.gender,
        'subs': student.subsidiaries
    }
    
    report, o_bonus = logic.get_student_report(s_data)
    
    return render_template('analysis.html', 
                          student=student, 
                          report=report, 
                          o_bonus=o_bonus,
                          active_course=None,
                          prediction=None)


@admin_bp.route('/predict/<int:student_id>/<course_code>')
@login_required
@admin_required
def predict(student_id, course_code):
    """Generate prediction for a specific course"""
    student = Student.query.get_or_404(student_id)
    
    s_data = {
        'a_levels': json.loads(student.a_level_json) if student.a_level_json else {},
        'o_levels': json.loads(student.o_level_json) if student.o_level_json else {},
        'gender': student.gender,
        'subs': student.subsidiaries
    }
    
    prediction = logic.predict_requirements(s_data, course_code)
    report, o_bonus = logic.get_student_report(s_data)
    
    return render_template('analysis.html',
                          student=student,
                          report=report,
                          o_bonus=o_bonus,
                          active_course=course_code,
                          prediction=prediction)


# ✅ ADD: Export Routes (Placeholder implementations)
@admin_bp.route('/export_csv/<course_code>')
@login_required
@admin_required
def export_csv(course_code):
    """Export eligible students for a course as CSV"""
    # Fetch all students
    students = Student.query.all()
    course = next((c for c in logic.COURSE_DATABASE if c['code'] == course_code), None)
    
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Combination', 'Gender', 'Weight', 'Status', 'Gap'])
    
    for s in students:
        s_data = {
            'a_levels': json.loads(s.a_level_json) if s.a_level_json else {},
            'o_levels': json.loads(s.o_level_json) if s.o_level_json else {},
            'gender': s.gender,
            'subs': s.subsidiaries
        }
        weight = logic.compute_weight_for_course(s_data['a_levels'], course, s.gender, s.subsidiaries)
        o_bonus = logic.calculate_olevel_bonus(s_data['o_levels'])
        total = weight + o_bonus
        cutoff = course['cutoffs'].get(s.gender, 40.0)
        status = 'Qualified' if total >= cutoff else ('Borderline' if cutoff - total <= 2 else 'Not Qualified')
        gap = round(cutoff - total, 1) if total < cutoff else 0
        
        writer.writerow([s.name, s.combination, s.gender, f'{total:.1f}', status, gap])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{course_code}_eligible_students.csv'
    )


@admin_bp.route('/export_pdf/<course_code>')
@login_required
@admin_required
def export_pdf(course_code):
    """Export eligible students for a course as PDF (placeholder)"""
    flash('PDF export coming soon. Using CSV instead.', 'info')
    return redirect(url_for('admin.export_csv', course_code=course_code))


@admin_bp.route('/export_report/<int:student_id>')
@login_required
@admin_required
def export_report(student_id):
    """Export full eligibility report for a student as CSV"""
    student = Student.query.get_or_404(student_id)
    
    s_data = {
        'a_levels': json.loads(student.a_level_json) if student.a_level_json else {},
        'o_levels': json.loads(student.o_level_json) if student.o_level_json else {},
        'gender': student.gender,
        'subs': student.subsidiaries
    }
    
    report, o_bonus = logic.get_student_report(s_data)
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['HCLV CareerNet - Eligibility Report', f'Student: {student.name}', f'Combination: {student.combination}', '', ''])
    writer.writerow(['Course', 'Code', 'Weight', 'Cutoff', 'Status', 'Gap'])
    
    for item in report:
        writer.writerow([item['course'], item['code'], item['weight'], item['cutoff'], item['status'], item['gap']])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{student.name.replace(" ", "_")}_report.csv'
    )