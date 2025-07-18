from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app, origins=["https://nesdan.vercel.app", "http://localhost:3000", "http://localhost:3001", "http://localhost:3002"], supports_credentials=True)

# Secret Key
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Keep it safe
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'location': self.location,
            'description': self.description
        }

# Initialize DB
with app.app_context():
    db.create_all()

# Hardcoded Admin
ADMIN = {
    "email": "admin@nesdan.org",
    "password": generate_password_hash("admin123")
}

# --- Token Auth Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow OPTIONS requests to pass through without token validation
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Token invalid or expired'}), 401
        return f(*args, **kwargs)
    return decorated
# --- Routes ---

# CORS Test Route
@app.route('/test-cors', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
def test_cors():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OPTIONS request received'}), 200
    return jsonify({
        'message': 'CORS test successful',
        'method': request.method,
        'origin': request.headers.get('Origin'),
        'headers': dict(request.headers)
    }), 200
    
# Login Route
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

# Get all events (public)
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([e.to_dict() for e in events]), 200

# Add event (protected)
@app.route('/events', methods=['POST', 'OPTIONS'])
@token_required
def add_event():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    new_event = Event(
        title=data["title"],
        date=data["date"],
        location=data["location"],
        description=data["description"]
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event added successfully!', 'event': new_event.to_dict()}), 201

@app.route('/events/<int:event_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_event(event_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': f'Event {event_id} deleted'}), 200

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
