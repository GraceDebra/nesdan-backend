from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Keep this secret

# Hardcoded admin credentials (use a DB in production)
ADMIN = {
    "email": "admin@nesdan.org",
    "password": generate_password_hash("admin123")  # hashed password
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data["email"] == ADMIN["email"] and check_password_hash(ADMIN["password"], data["password"]):
        token = jwt.encode({
            'email': data["email"],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Protect admin routes (e.g., event add/delete)
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        return f(*args, **kwargs)
    return decorated
