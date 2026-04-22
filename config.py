import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hclv.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'

    # Allow session cookie inside the Replit preview iframe (cross-site context)
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    # CSRF tweaks so the token works behind the Replit proxy
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = False
