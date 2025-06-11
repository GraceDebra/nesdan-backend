from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define Event model
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

# Create the database
with app.app_context():
    db.create_all()

# Routes
@app.route("/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events]), 200

@app.route("/events", methods=["POST"])
def add_event():
    data = request.get_json()
    new_event = Event(
        title=data["title"],
        date=data["date"],
        location=data["location"],
        description=data["description"]
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({"message": "Event added successfully!"}), 201

@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event is None:
        return jsonify({"error": "Event not found"}), 404
    
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Event deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
