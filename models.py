from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='Student')
    theme_pref = db.Column(db.Text, default='{"type":"light"}')
    profile = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    gender = db.Column(db.String(1))
    combination = db.Column(db.String(50), default='N/A')
    o_level_json = db.Column(db.Text, default='{}')
    a_level_json = db.Column(db.Text, default='{}')
    subsidiaries = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    class_level = db.Column(db.String(10))
    campus_choices = db.Column(db.Text, default='[]')
    course_wishes = db.Column(db.Text, default='[]')
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    theme_pref = db.Column(db.Text, default='{"type":"light"}')
    records = db.relationship('AcademicRecord', backref='student_profile', lazy=True, cascade="all, delete-orphan")

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    website = db.Column(db.String(255))
    uni_type = db.Column(db.String(20))

class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)

class SiteTheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    variable_name = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(100))

class AcademicRecord(db.Model):
    """Stores individual subject grades per term/exam for charting"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    term = db.Column(db.String(30), nullable=False)
    exam_type = db.Column(db.String(10), nullable=False)  # BOT, MT, EOT
    subject = db.Column(db.String(50), nullable=False)
    paper_code = db.Column(db.String(20), default='FINAL')
    marks = db.Column(db.Integer)
    grade = db.Column(db.String(2))

class CustomPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))