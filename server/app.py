from flask import Flask, request, jsonify, session, send_from_directory, g
import sqlite3
import os
import time
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jsonschema import validate, ValidationError

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data.db')

app = Flask(__name__, static_folder='..', static_url_path='/')
# Use an environment-provided secret in production. Fallback for local dev only.
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')
# Session cookie security settings (adjust `SESSION_COOKIE_SECURE` to True in production)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
)
# Restrict CORS to local dev origins to reduce CSRF risk in demos
allowed_origins = [
    'http://localhost:5500', 'http://127.0.0.1:5500',
    'http://localhost:5501', 'http://127.0.0.1:5501'
]
CORS(app, supports_credentials=True, origins=allowed_origins)

# Flask-Limiter setup (per-IP limits)
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
limiter.init_app(app)

# Simple in-memory rate limiting for login attempts: {ip: [timestamps...]}
login_attempts = {}
LOGIN_WINDOW = 60  # seconds
LOGIN_MAX_ATTEMPTS = 6

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin.html')
def admin_page():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/api/contact', methods=['POST'])
@limiter.limit("10 per minute")
def api_contact():
    data = request.get_json() or request.form

    # JSON schema for request validation
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 2},
            "email": {"type": "string", "format": "email"},
            "message": {"type": "string", "minLength": 10}
        },
        "required": ["name", "email", "message"]
    }

    try:
        # validate will raise ValidationError on failure
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({'ok': False, 'error': 'Invalid input: ' + str(e.message)}), 400

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()

    db = get_db()
    db.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', (name, email, message))
    db.commit()
    return jsonify({'ok': True, 'message': 'Form Submitted Successfully'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or request.form
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({'ok': False, 'error': 'Missing credentials'}), 400

    # Rate limit by remote address
    ip = request.remote_addr or 'unknown'
    now = time.time()
    attempts = login_attempts.get(ip, [])
    # drop old attempts
    attempts = [t for t in attempts if now - t < LOGIN_WINDOW]
    if len(attempts) >= LOGIN_MAX_ATTEMPTS:
        return jsonify({'ok': False, 'error': 'Too many login attempts. Try again later.'}), 429

    row = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
    if not row or not check_password_hash(row['password_hash'], password):
        # record failed attempt
        attempts.append(now)
        login_attempts[ip] = attempts
        return jsonify({'ok': False, 'error': 'Invalid credentials'}), 401

    # success: reset attempts and set session
    login_attempts.pop(ip, None)
    session['user'] = username
    return jsonify({'ok': True})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({'ok': True})

def auth_required():
    return 'user' in session

@app.route('/api/submissions', methods=['GET'])
def api_submissions():
    if not auth_required():
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
    rows = query_db('SELECT id, name, email, message, created_at FROM contacts ORDER BY id DESC')
    results = [dict(r) for r in rows]
    return jsonify({'ok': True, 'submissions': results})


@app.route('/api/change-password', methods=['POST'])
def api_change_password():
    if not auth_required():
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
    data = request.get_json() or request.form
    old = (data.get('old_password') or '').strip()
    new = (data.get('new_password') or '').strip()
    if not old or not new or len(new) < 8:
        return jsonify({'ok': False, 'error': 'Password rules: minimum length 8 characters.'}), 400
    user = session.get('user')
    row = query_db('SELECT * FROM users WHERE username = ?', (user,), one=True)
    if not row or not check_password_hash(row['password_hash'], old):
        return jsonify({'ok': False, 'error': 'Old password incorrect.'}), 401
    db = get_db()
    db.execute('UPDATE users SET password_hash = ? WHERE username = ?', (generate_password_hash(new), user))
    db.commit()
    return jsonify({'ok': True, 'message': 'Password changed'})

if __name__ == '__main__':
    # Run on port 5501 to avoid conflicting with static server on 5500
    app.run(host='0.0.0.0', port=5501, debug=True)
