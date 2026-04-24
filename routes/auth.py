# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, csrf
from models import User, Student, PasswordResetCode
from utils import calculate_combination_code
from email_service import send_reset_code_email
from datetime import datetime, timedelta
import secrets
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
    # If already authenticated, redirect to appropriate dashboard.
    # Exception: SuperUser can append `?su_edit=1` to render the page for editing.
    su_edit = request.args.get('su_edit') == '1'
    if current_user.is_authenticated and not (su_edit and current_user.role == 'SuperUser'):
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
    # Prevent authenticated users from registering again.
    # Exception: SuperUser can append `?su_edit=1` to render the page for editing.
    su_edit = request.args.get('su_edit') == '1'
    if current_user.is_authenticated and not (su_edit and current_user.role == 'SuperUser'):
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

# ============================================================
# Password reset (forgot password) flow
# ============================================================

RESET_CODE_TTL_MINUTES = 15
RESET_MAX_ATTEMPTS = 5


def _generate_reset_code() -> str:
    """Generate a cryptographically secure 6-digit numeric code."""
    return f"{secrets.randbelow(1_000_000):06d}"


def _find_user_by_email(email: str):
    """Find a User by email.

    Looks up against User.email (admins / SuperUsers) first, then falls back
    to Student.email for student accounts. Returns (user, recipient_email,
    display_name) or (None, None, None).
    """
    if not email:
        return None, None, None

    # 1. Direct lookup on the User table (admins / SuperUsers)
    user = User.query.filter(User.email.ilike(email)).first()
    if user:
        display = user.username
        # Prefer the student profile's name if present
        if user.profile and user.profile.name:
            display = user.profile.name
        return user, user.email, display

    # 2. Lookup via Student profile (students)
    student = Student.query.filter(Student.email.ilike(email)).first()
    if student and student.user_id:
        user = User.query.get(student.user_id)
        if user:
            return user, student.email, (student.name or user.username)

    return None, None, None


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Step 1: User submits email to receive a reset code."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email or '@' not in email:
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        user, recipient_email, display_name = _find_user_by_email(email)

        # Always show the same success message to prevent email enumeration,
        # but only actually send if the email is registered.
        if user and recipient_email:
            try:
                # Invalidate any prior unused codes for this user
                PasswordResetCode.query.filter_by(user_id=user.id, used=False).update({'used': True})

                code = _generate_reset_code()
                reset = PasswordResetCode(
                    user_id=user.id,
                    code_hash=generate_password_hash(code, method='scrypt', salt_length=16),
                    email=recipient_email,
                    expires_at=datetime.utcnow() + timedelta(minutes=RESET_CODE_TTL_MINUTES),
                    used=False,
                    attempts=0,
                )
                db.session.add(reset)
                db.session.commit()

                sent = send_reset_code_email(recipient_email, display_name, code)
                if not sent:
                    logger.error(f"Reset code generated but email failed for user {user.id}")
                    flash('We could not send the reset email right now. Please try again in a moment.', 'danger')
                    return redirect(url_for('auth.forgot_password'))

                session['pending_reset_id'] = reset.id
                session['pending_reset_email'] = recipient_email
                logger.info(f"Password reset code issued for user {user.id}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to issue reset code: {e}", exc_info=True)
                flash('Something went wrong. Please try again.', 'danger')
                return redirect(url_for('auth.forgot_password'))
        else:
            logger.info(f"Forgot-password request for unknown email: {email}")
            # Pretend a code was issued so we don't leak which emails exist.
            session['pending_reset_id'] = -1
            session['pending_reset_email'] = email

        flash('If that email is registered, a verification code has been sent.', 'info')
        return redirect(url_for('auth.verify_reset_code'))

    return render_template('forgot_password.html')


@auth_bp.route('/verify-reset-code', methods=['GET', 'POST'])
def verify_reset_code():
    """Step 2: User enters the 6-digit code from their email."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    pending_id = session.get('pending_reset_id')
    masked_email = session.get('pending_reset_email', '')
    if pending_id is None:
        flash('Please start a password reset first.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        code = (request.form.get('code') or '').strip()

        if not re.fullmatch(r'\d{6}', code):
            flash('Please enter the 6-digit code sent to your email.', 'danger')
            return redirect(url_for('auth.verify_reset_code'))

        # Decoy path: no real reset is pending
        if pending_id == -1:
            flash('Invalid or expired code. Please request a new one.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        reset = PasswordResetCode.query.get(pending_id)
        if not reset or reset.used or reset.expires_at < datetime.utcnow():
            flash('This code has expired. Please request a new one.', 'danger')
            session.pop('pending_reset_id', None)
            session.pop('pending_reset_email', None)
            return redirect(url_for('auth.forgot_password'))

        if reset.attempts >= RESET_MAX_ATTEMPTS:
            reset.used = True
            db.session.commit()
            flash('Too many incorrect attempts. Please request a new code.', 'danger')
            session.pop('pending_reset_id', None)
            session.pop('pending_reset_email', None)
            return redirect(url_for('auth.forgot_password'))

        if not check_password_hash(reset.code_hash, code):
            reset.attempts += 1
            db.session.commit()
            remaining = RESET_MAX_ATTEMPTS - reset.attempts
            flash(f'Incorrect code. You have {remaining} attempt(s) left.', 'danger')
            return redirect(url_for('auth.verify_reset_code'))

        # Code matches -- mark it as verified for the next step
        session['verified_reset_id'] = reset.id
        return redirect(url_for('auth.reset_password'))

    return render_template('verify_reset_code.html', email=masked_email)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Step 3: User chooses a new password after verifying the code."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    verified_id = session.get('verified_reset_id')
    if not verified_id:
        flash('Please verify your reset code first.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    reset = PasswordResetCode.query.get(verified_id)
    if not reset or reset.used or reset.expires_at < datetime.utcnow():
        flash('Your reset session has expired. Please start again.', 'danger')
        for k in ('pending_reset_id', 'pending_reset_email', 'verified_reset_id'):
            session.pop(k, None)
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.reset_password'))
        if new_password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password'))

        user = User.query.get(reset.user_id)
        if not user:
            flash('Account not found. Please contact support.', 'danger')
            return redirect(url_for('auth.login'))

        user.password = generate_password_hash(new_password, method='scrypt', salt_length=16)
        reset.used = True
        db.session.commit()

        for k in ('pending_reset_id', 'pending_reset_email', 'verified_reset_id'):
            session.pop(k, None)

        logger.info(f"Password reset completed for user {user.id}")
        flash('Your password has been reset. You can now sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
