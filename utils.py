from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user
import json

# --- HELPERS ---
def calculate_combination_code(student):
    if not student.a_level_json: return "N/A"
    subjects = json.loads(student.a_level_json)
    principals = []
    subsidiary_code = ""
    subs_map = {"Subsidiary ICT": "ICT", "Subsidiary Mathematics": "SM"}
    for subj in subjects:
        if subj in subs_map: subsidiary_code = subs_map[subj]
        elif subj != "General Paper": principals.append(subj[0].upper())
    if not principals: return "N/A"
    principals.sort()
    code = "".join(principals)
    if subsidiary_code: code += f"/{subsidiary_code}"
    return code

# --- DECORATORS ---
def su_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'SuperUser':
            flash('Super User privileges required.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['Administrator', 'SuperUser']:
            flash('Admin privileges required.')
            if current_user.is_authenticated and current_user.role == 'Student': return redirect(url_for('student.portal'))
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated