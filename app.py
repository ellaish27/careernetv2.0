# app.py
from flask import Flask, render_template, redirect, url_for, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from extensions import db, login_manager, csrf
from models import User, Student, SiteContent, SiteTheme, University, AcademicRecord, CustomPage
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp
from routes.su import su_bp
from utils import calculate_combination_code
import logic
import os
import json
from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Trust the Replit proxy so Flask sees the real https scheme/host;
    # required for Secure cookies and CSRF to work correctly behind the proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # 1. Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 2. Register Blueprints
    app.register_blueprint(auth_bp)          # /login, /logout, /register
    app.register_blueprint(student_bp)       # /student/*
    app.register_blueprint(admin_bp)         # /admin/*
    app.register_blueprint(su_bp)            # /su/*

    # 3. Global Context Processor
    @app.context_processor
    def inject_settings():
        """Injects site settings, themes, and student combo code into all templates."""
        from flask_login import current_user
        
        # Query DB for live site settings
        site_content = {c.key: c.value for c in SiteContent.query.all()}
        site_theme = {t.variable_name: t.value for t in SiteTheme.query.all()}
        
        user_theme = None
        combination_code = None
        
        if current_user.is_authenticated:
            if current_user.role == 'Student':
                profile = Student.query.filter_by(user_id=current_user.id).first()
                if profile:
                    if profile.theme_pref:
                        user_theme = json.loads(profile.theme_pref)
                    combination_code = calculate_combination_code(profile)
            else:
                if current_user.theme_pref:
                    user_theme = json.loads(current_user.theme_pref)
                    
        return dict(
            site_content=site_content,
            site_theme=site_theme,
            user_theme=user_theme,
            combination_code=combination_code,
            custom_pages=CustomPage.query.filter_by(is_active=True).order_by(CustomPage.created_at.desc()).all(),
            now=datetime.utcnow()
        )

    # 4. Routes
    @app.route('/')
    def index():
        """Landing page for guests, dashboard redirect for authenticated users."""
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == 'Student':
                return redirect(url_for('student.portal'))
            return redirect(url_for('admin.dashboard'))
        # Build slideshow image list dynamically from static/school folder
        school_dir = os.path.join(app.static_folder, 'school')
        allowed_ext = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        slideshow_images = []
        if os.path.isdir(school_dir):
            for fname in sorted(os.listdir(school_dir)):
                if os.path.splitext(fname)[1].lower() in allowed_ext:
                    slideshow_images.append(
                        url_for('static', filename=f'school/{fname}')
                    )
        return render_template('landing.html', slideshow_images=slideshow_images)

    @app.route('/page/<slug>')
    def view_custom_page(slug):
        """Public route for SU-created pages (WordPress-style CMS)."""
        # Import here to prevent circular dependency during app startup
        from models import CustomPage
        page = CustomPage.query.filter_by(slug=slug, is_active=True).first_or_404()
        return render_template('page.html', page=page)

    @app.route('/get_options')
    def get_options():
        """Serves subject/course options to registration & settings forms."""
        path = os.path.join(os.path.dirname(__file__), 'data', 'options.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except Exception as e:
            app.logger.error(f"Failed to load options.json: {e}")
            return jsonify({}), 404

    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_json:
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('landing.html'), 404  # Fallback to landing

    return app


def init_db():
    """Initialize database and seed default data if empty."""
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Seed Site Content
        if not SiteContent.query.first():
            db.session.add_all([
                SiteContent(key='site_title', value='HCLV CareerNet'),
                SiteContent(key='welcome_text', value='Education for Service')
            ])
            db.session.commit()
            print("✅ Seeded default SiteContent")
            
        # Seed Site Theme
        if not SiteTheme.query.first():
            db.session.add_all([
                SiteTheme(variable_name='primary-color', value='#002147'),
                SiteTheme(variable_name='accent-color', value='#D4AF37'),
                SiteTheme(variable_name='font-family', value='Segoe UI')
            ])
            db.session.commit()
            print("✅ Seeded default SiteTheme")
            
        # Seed SuperUser
        if not User.query.first():
            from werkzeug.security import generate_password_hash
            default_su_username = os.environ.get('DEFAULT_SU_USERNAME', 'su2026')
            default_su_password = os.environ.get('DEFAULT_SU_PASSWORD')
            if not default_su_password:
                print("⚠️ Skipped default SuperUser creation: set DEFAULT_SU_PASSWORD to bootstrap securely.")
                return
            su = User(
                username=default_su_username, 
                password=generate_password_hash(default_su_password, method='scrypt'), 
                role='SuperUser'
            )
            db.session.add(su)
            db.session.commit()
            print(f"✅ Created default SuperUser: {default_su_username}")


if __name__ == '__main__':
    app = create_app()
    init_db()  # Ensure tables & defaults exist before running
    app.run(debug=True, host='0.0.0.0', port=5000)