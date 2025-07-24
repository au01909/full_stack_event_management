from datetime import datetime
from typing import Dict, List, Optional
import uuid

class Event:
    """Event model class for managing event data"""
    
    def __init__(self, name: str, date: str, location: str, description: str = "", tags: Optional[List[str]] = None, event_id: Optional[str] = None):
        self.id = event_id or str(uuid.uuid4())
        self.name = name
        self.date = date
        self.location = location
        self.description = description
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'location': self.location,
            'description': self.description,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """Create event from dictionary"""
        event = cls(
            name=data['name'],
            date=data['date'],
            location=data['location'],
            description=data.get('description', ''),
            tags=data.get('tags', []),
            event_id=data.get('id')
        )
        event.created_at = data.get('created_at', event.created_at)
        event.updated_at = data.get('updated_at', event.updated_at)
        return event
    
    def update(self, **kwargs):
        """Update event fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
    
    def validate(self) -> List[str]:
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
        
        if len(self.name) > 100:
            errors.append("Event name must be less than 100 characters")
        
        if len(self.location) > 200:
            errors.append("Location must be less than 200 characters")
        
        if len(self.description) > 1000:
            errors.append("Description must be less than 1000 characters")
        
        return errors
