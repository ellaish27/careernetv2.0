from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import University, SiteContent, SiteTheme, User, CustomPage
from utils import su_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import re

ALLOWED_SCHOOL_EXT = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
ALLOWED_IMG_EXT = {'jpg', 'jpeg', 'png', 'webp', 'gif', 'svg'}


def _school_dir():
    path = os.path.join(current_app.static_folder, 'school')
    os.makedirs(path, exist_ok=True)
    return path


def _uploads_dir():
    path = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(path, exist_ok=True)
    return path


def _list_dir_images(path, allowed):
    files = []
    if os.path.isdir(path):
        for fname in sorted(os.listdir(path)):
            ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
            if ext in allowed:
                files.append(fname)
    return files


def _list_school_images():
    return _list_dir_images(_school_dir(), ALLOWED_SCHOOL_EXT)


def _list_library_images():
    return _list_dir_images(_uploads_dir(), ALLOWED_IMG_EXT)


def _save_unique(file_storage, target_dir):
    """Save an uploaded file with a sanitized, non-colliding filename. Returns final filename."""
    safe_name = secure_filename(file_storage.filename or '')
    if not safe_name:
        return None
    base, dot, ex = safe_name.rpartition('.')
    dest = os.path.join(target_dir, safe_name)
    i = 2
    while os.path.exists(dest):
        safe_name = f"{base}-{i}.{ex}" if dot else f"{safe_name}-{i}"
        dest = os.path.join(target_dir, safe_name)
        i += 1
    file_storage.save(dest)
    return safe_name

# ✅ FIX: Use __name__ (double underscores) for proper blueprint registration
su_bp = Blueprint('su', __name__, url_prefix='/su')


def _slugify(text):
    base = re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')
    return base or "page"

@su_bp.route('/dashboard')
@login_required
@su_required
def dashboard():
    """SU Dashboard - Loads site settings for editing"""
    # Load existing content/theme so the form is pre-filled
    site_content = {c.key: c.value for c in SiteContent.query.all()}
    site_theme = {t.variable_name: t.value for t in SiteTheme.query.all()}
    pages = CustomPage.query.order_by(CustomPage.created_at.desc()).all()
    core_pages = [
        {"name": "Landing Page", "url": url_for("index"), "editable": "Live Edit"},
        {"name": "Login", "url": url_for("auth.login"), "editable": "Template"},
        {"name": "Registration", "url": url_for("auth.register"), "editable": "Template"},
        {"name": "Student Portal", "url": url_for("student.portal"), "editable": "App Data"},
        {"name": "Student Tracker", "url": url_for("student.tracker"), "editable": "App Data"},
        {"name": "Admin Dashboard", "url": url_for("admin.dashboard"), "editable": "App Data"},
        {"name": "SU Dashboard", "url": url_for("su.dashboard"), "editable": "Control Panel"},
    ]
    # Group all SiteContent keys by their prefix (e.g. landing_, site_, welcome_)
    all_content = SiteContent.query.order_by(SiteContent.key).all()
    grouped_content = {}
    for c in all_content:
        prefix = c.key.split('_', 1)[0] if '_' in c.key else 'general'
        grouped_content.setdefault(prefix, []).append(c)

    library_images = _list_library_images()
    return render_template(
        'su_dashboard.html',
        site_content=site_content,
        site_theme=site_theme,
        pages=pages,
        core_pages=core_pages,
        school_images=_list_school_images(),
        grouped_content=grouped_content,
        library_images=library_images
    )


@su_bp.route('/upload_school_image', methods=['POST'])
@login_required
@su_required
def upload_school_image():
    """Upload one or more images into static/school for the landing slideshow."""
    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        flash('No file selected.', 'warning')
        return redirect(url_for('su.dashboard') + '#slideshow-panel')

    saved, skipped = 0, 0
    target_dir = _school_dir()
    for f in files:
        if not f or not f.filename:
            continue
        ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
        if ext not in ALLOWED_SCHOOL_EXT:
            skipped += 1
            continue
        safe_name = secure_filename(f.filename)
        dest = os.path.join(target_dir, safe_name)
        # avoid overwriting existing files
        base, dot, ex = safe_name.rpartition('.')
        i = 2
        while os.path.exists(dest):
            safe_name = f"{base}-{i}.{ex}"
            dest = os.path.join(target_dir, safe_name)
            i += 1
        f.save(dest)
        saved += 1

    msg = f'Uploaded {saved} image(s).'
    if skipped:
        msg += f' Skipped {skipped} unsupported file(s).'
    flash(msg, 'success' if saved else 'warning')
    return redirect(url_for('su.dashboard') + '#slideshow-panel')


@su_bp.route('/delete_school_image', methods=['POST'])
@login_required
@su_required
def delete_school_image():
    """Delete a school slideshow image by filename."""
    filename = request.form.get('filename', '')
    safe = secure_filename(filename)
    if not safe:
        flash('Invalid filename.', 'danger')
        return redirect(url_for('su.dashboard') + '#slideshow-panel')
    path = os.path.join(_school_dir(), safe)
    if os.path.isfile(path):
        os.remove(path)
        flash(f'Deleted {safe}.', 'success')
    else:
        flash('File not found.', 'warning')
    return redirect(url_for('su.dashboard') + '#slideshow-panel')

# ✅ FIX: Added the missing route causing the BuildError
@su_bp.route('/manage_universities', methods=['GET', 'POST'])
@login_required
@su_required
def manage_universities():
    """Manage Universities - Add/Delete"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            if not University.query.filter_by(name=name).first():
                new_uni = University(
                    name=name, 
                    uni_type=request.form.get('type'), 
                    website=request.form.get('website')
                )
                db.session.add(new_uni)
                db.session.commit()
                flash('University added successfully.', 'success')
            else:
                flash('University already exists.', 'warning')
                
        elif action == 'delete':
            uni_id = request.form.get('uni_id')
            uni = University.query.get(uni_id)
            if uni:
                db.session.delete(uni)
                db.session.commit()
                flash('University deleted.', 'warning')
                
        return redirect(url_for('su.manage_universities'))

    universities = University.query.order_by(University.name).all()
    return render_template('su_universities.html', universities=universities)

@su_bp.route('/save_content', methods=['POST'])
@login_required
@su_required
def save_content():
    """AJAX: Update Site Content (Title, Welcome Text)"""
    data = request.get_json()
    for key, value in data.items():
        if key == 'csrf_token': continue
        item = SiteContent.query.filter_by(key=key).first()
        if item:
            item.value = value
        else:
            db.session.add(SiteContent(key=key, value=value))
    db.session.commit()
    return jsonify({'status': 'success'})

@su_bp.route('/save_theme', methods=['POST'])
@login_required
@su_required
def save_theme():
    """AJAX: Update Site Theme (Colors, Font)"""
    data = request.get_json()
    for key, value in data.items():
        if key == 'csrf_token': continue
        item = SiteTheme.query.filter_by(variable_name=key).first()
        if item:
            item.value = value
        else:
            db.session.add(SiteTheme(variable_name=key, value=value))
    db.session.commit()
    return jsonify({'status': 'success'})


@su_bp.route('/create_page', methods=['POST'])
@login_required
@su_required
def create_page():
    """Create a new custom CMS page."""
    title = request.form.get('title', '').strip()
    if not title:
        flash('Page title is required.', 'danger')
        return redirect(url_for('su.dashboard'))

    base_slug = _slugify(title)
    slug = base_slug
    suffix = 2
    while CustomPage.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    page = CustomPage(title=title, slug=slug, content=f"<p>{title}</p>", is_active=True)
    db.session.add(page)
    db.session.commit()
    flash('Page created successfully.', 'success')
    return redirect(url_for('su.dashboard'))


@su_bp.route('/pages/edit/<int:page_id>', methods=['POST'])
@login_required
@su_required
def edit_page(page_id):
    """Edit an existing custom CMS page."""
    page = CustomPage.query.get_or_404(page_id)
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not title:
        flash('Page title is required.', 'danger')
        return redirect(url_for('su.dashboard'))

    if not content:
        flash('Page content cannot be empty.', 'danger')
        return redirect(url_for('su.dashboard'))

    page.title = title
    page.content = content
    db.session.commit()
    flash('Page updated successfully.', 'success')
    return redirect(url_for('su.dashboard'))


@su_bp.route('/delete_page/<int:page_id>', methods=['POST'])
@login_required
@su_required
def delete_page(page_id):
    """Delete a custom CMS page."""
    page = CustomPage.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully.', 'success')
    return redirect(url_for('su.dashboard'))

@su_bp.route('/create_user', methods=['POST'])
@login_required
@su_required
def create_user():
    """Create new Admin/SuperUser account"""
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('su.dashboard'))

    if role not in ['Administrator', 'SuperUser']:
        flash('Invalid role selected.', 'danger')
        return redirect(url_for('su.dashboard'))

    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
    else:
        hashed_pw = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {username} created as {role}.', 'success')
    return redirect(url_for('su.dashboard'))

@su_bp.route('/delete_content', methods=['POST'])
@login_required
@su_required
def delete_content():
    """AJAX: Delete a SiteContent key."""
    data = request.get_json() or {}
    key = (data.get('key') or '').strip()
    if not key:
        return jsonify({'status': 'error', 'message': 'Missing key'}), 400
    item = SiteContent.query.filter_by(key=key).first()
    if not item:
        return jsonify({'status': 'error', 'message': 'Key not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'status': 'success'})


@su_bp.route('/upload_image', methods=['POST'])
@login_required
@su_required
def upload_image():
    """Upload an image to the general library (static/uploads/).
    Supports both regular AJAX and TinyMCE's images_upload_url contract:
    returns JSON {"location": "<absolute URL>"} on success.
    """
    f = request.files.get('file') or request.files.get('image') or request.files.get('images')
    if not f or not f.filename:
        return jsonify({'error': 'No file provided'}), 400
    ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
    if ext not in ALLOWED_IMG_EXT:
        return jsonify({'error': f'Unsupported file type .{ext}'}), 400
    final_name = _save_unique(f, _uploads_dir())
    if not final_name:
        return jsonify({'error': 'Could not save file'}), 400
    location = url_for('static', filename=f'uploads/{final_name}', _external=True)
    return jsonify({'location': location, 'filename': final_name,
                    'url': url_for('static', filename=f'uploads/{final_name}')})


@su_bp.route('/delete_image', methods=['POST'])
@login_required
@su_required
def delete_image():
    """AJAX: Delete an image from the library (static/uploads/)."""
    data = request.get_json(silent=True) or request.form
    filename = (data.get('filename') or '').strip()
    safe = secure_filename(filename)
    if not safe:
        return jsonify({'status': 'error', 'message': 'Invalid filename'}), 400
    path = os.path.join(_uploads_dir(), safe)
    if not os.path.isfile(path):
        return jsonify({'status': 'error', 'message': 'Not found'}), 404
    os.remove(path)
    return jsonify({'status': 'success'})


@su_bp.route('/list_images', methods=['GET'])
@login_required
@su_required
def list_images():
    """AJAX: Returns the current image library as JSON."""
    files = [{'name': n, 'url': url_for('static', filename=f'uploads/{n}')}
             for n in _list_library_images()]
    return jsonify({'images': files})
