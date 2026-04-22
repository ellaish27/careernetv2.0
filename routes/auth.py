# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, csrf
from models import User, Student
from utils import calculate_combination_code
import json
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ✅ FIX: Use __name__ for proper blueprint registration
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login with secure password verification.
    Redirects to role-specific dashboard on success.
    """
    # If already authenticated, redirect to appropriate dashboard
    if current_user.is_authenticated:
        if current_user.role == 'SuperUser':
            return redirect(url_for('su.dashboard'))
        elif current_user.role == 'Student':
            return redirect(url_for('student.portal'))
        else:
            return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Basic validation
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Find user by username (case-insensitive for better UX)
        user = User.query.filter(
            User.username.ilike(username)
        ).first()
        
        # Verify credentials securely
        if user and check_password_hash(user.password, password):
            login_user(user)
            
            # Log successful login (for audit purposes)
            logger.info(f"User '{username}' logged in successfully.")
            
            # Redirect based on role
            if user.role == 'SuperUser':
                return redirect(url_for('su.dashboard'))
            elif user.role == 'Student':
                return redirect(url_for('student.portal'))
            else:  # Administrator or other roles
                return redirect(url_for('admin.dashboard'))
        else:
            # Log failed attempt (without revealing which field was wrong)
            logger.warning(f"Failed login attempt for username: '{username}'")
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out current user and redirect to login page."""
    username = current_user.username
    logout_user()
    logger.info(f"User '{username}' logged out.")
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle student registration with multi-step form data.
    Creates User + Student profile in a single transaction.
    """
    # Prevent authenticated users from registering again
    if current_user.is_authenticated:
        flash('You are already logged in.', 'warning')
        return redirect(url_for('student.portal') if current_user.role == 'Student' else url_for('admin.dashboard'))
    
    if request.method == 'POST':
        try:
            # 1. Extract and validate basic account info
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            last_name = request.form.get('last_name', '').strip()
            first_name = request.form.get('first_name', '').strip()
            
            # Username validation
            if not username:
                flash('Username is required.', 'danger')
                return redirect(url_for('auth.register'))
            
            if len(username) < 3 or len(username) > 20:
                flash('Username must be between 3 and 20 characters.', 'danger')
                return redirect(url_for('auth.register'))
            
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                flash('Username can only contain letters, numbers, and underscores.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Check for existing username (case-insensitive)
            if User.query.filter(User.username.ilike(username)).first():
                flash('Username already exists. Please choose another.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Password validation
            if not password or len(password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Name validation
            if not last_name or not first_name:
                flash('Both first and last name are required.', 'danger')
                return redirect(url_for('auth.register'))
            
            # 2. Create User Account
            hashed_pw = generate_password_hash(password, method='scrypt', salt_length=16)
            new_user = User(
                username=username,
                password=hashed_pw,
                role='Student'  # All registrations are students by default
            )
            db.session.add(new_user)
            db.session.flush()  # Get the user ID without committing yet
            
            # 3. Parse and validate form lists
            courses = [c.strip() for c in request.form.getlist('courses') if c.strip()]
            campuses = [c.strip() for c in request.form.getlist('campuses') if c.strip()]
            a_principals = [s.strip() for s in request.form.getlist('a_principal') if s.strip()]
            a_subsidiary = request.form.get('a_subsidiary', '').strip()
            o_subjects = request.form.getlist('o_subjects')
            o_grades = request.form.getlist('o_grades')
            
            # Build A-Level JSON (General Paper is always included)
            a_level_data = {"General Paper": "N/A"}
            for sub in a_principals:
                if sub:  # Only add non-empty subjects
                    a_level_data[sub] = "N/A"  # Grades set by admin later
            if a_subsidiary:
                a_level_data[a_subsidiary] = "N/A"
            
            # Build O-Level JSON (pair subjects with grades)
            o_level_data = {}
            for i in range(min(len(o_subjects), len(o_grades))):
                sub = o_subjects[i].strip()
                grade = o_grades[i].strip()
                if sub and grade:
                    o_level_data[sub] = grade
            
            # Build Theme JSON from hidden inputs
            theme_type = request.form.get('theme_type', 'light').strip()
            theme_data = {"type": theme_type}
            if theme_type == 'custom':
                theme_data.update({
                    "bg": request.form.get('theme_bg', '#ffffff'),
                    "text": request.form.get('theme_text', '#333333'),
                    "font": request.form.get('theme_font', 'Segoe UI')
                })
            
            # 4. Create Student Profile
            full_name = f"{last_name} {first_name}".strip()
            class_level = request.form.get('class', '').strip()
            gender = request.form.get('gender', 'M')  # Default to Male if not specified
            
            new_profile = Student(
                name=full_name,
                user_id=new_user.id,
                gender=gender,
                class_level=class_level,
                combination="",  # Will be calculated below
                course_wishes=json.dumps(courses[:10]),  # Limit to 10 courses
                campus_choices=json.dumps(campuses[:4]),  # Limit to 4 campuses
                a_level_json=json.dumps(a_level_data),
                o_level_json=json.dumps(o_level_data),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                theme_pref=json.dumps(theme_data),
                subsidiaries=int(request.form.get('subsidiaries', 0))
            )
            
            db.session.add(new_profile)
            db.session.commit()  # Commit user + profile together
            
            # 5. Calculate and save combination code
            try:
                new_profile.combination = calculate_combination_code(new_profile)
                db.session.commit()
            except Exception as calc_error:
                logger.warning(f"Could not calculate combination for student {new_profile.id}: {calc_error}")
                new_profile.combination = "Pending"
                db.session.commit()
            
            # 6. Auto-login and redirect
            login_user(new_user)
            logger.info(f"New student registered: {username} (ID: {new_user.id})")
            flash('Registration successful! Welcome to HCLV CareerNet.', 'success')
            return redirect(url_for('student.portal'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error for username '{request.form.get('username', 'unknown')}': {str(e)}", exc_info=True)
            flash('Registration failed. Please try again or contact support.', 'danger')
            return redirect(url_for('auth.register'))
    
    # GET request - render registration form
    return render_template('register.html')


@auth_bp.route('/api/check-username', methods=['POST'])
def check_username_availability():
    """AJAX endpoint to check if username is available (for real-time validation)."""
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 400
    
    username = request.json.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3 or len(username) > 20:
        return jsonify({'available': False, 'message': 'Username must be 3-20 characters'})
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'available': False, 'message': 'Only letters, numbers, and underscores allowed'})
    
    exists = User.query.filter(User.username.ilike(username)).first() is not None
    return jsonify({
        'available': not exists,
        'message': 'Username available' if not exists else 'Username already taken'
    })