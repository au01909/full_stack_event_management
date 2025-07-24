from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with events
    events = db.relationship('Event', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)  # Store as comma-separated string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'location': self.location,
            'description': self.description,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
    
    @classmethod
    def from_dict(cls, data, user_id):
        """Create Event from dictionary with user_id"""
        event = cls(
            name=data['name'],
            date=data['date'],
            location=data['location'],
            description=data['description'],
            tags=','.join(data.get('tags', [])),
            user_id=user_id
        )
        return event
    
    def update_from_dict(self, data):
        """Update event fields from dictionary"""
        self.name = data.get('name', self.name)
        self.date = data.get('date', self.date)
        self.location = data.get('location', self.location)
        self.description = data.get('description', self.description)
        self.tags = ','.join(data.get('tags', [])) if data.get('tags') else self.tags
        self.updated_at = datetime.utcnow()
    
    def validate(self):
        """Validate event data and return list of errors"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Event name is required")
        
        if not self.date or not self.date.strip():
            errors.append("Event date is required")
        else:
            try:
                datetime.fromisoformat(self.date.replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid date format")
        
        if not self.location or not self.location.strip():
            errors.append("Event location is required")
        
        if len(self.name) > 200:
            errors.append("Event name must be less than 200 characters")
        
        if len(self.location) > 200:
            errors.append("Location must be less than 200 characters")
        
        if self.description and len(self.description) > 1000:
            errors.append("Description must be less than 1000 characters")
        
        return errors
    
    def __repr__(self):
        return f'<Event {self.name}>'