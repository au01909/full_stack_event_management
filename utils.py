from typing import List
from datetime import datetime
from models import Event

def search_events(events: List[Event], search_term: str) -> List[Event]:
    """Search events by name, location, or description"""
    if not search_term:
        return events
    
    search_term = search_term.lower().strip()
    filtered_events = []
    
    for event in events:
        # Search in name, location, description, and tags
        searchable_text = ' '.join([
            event.name.lower(),
            event.location.lower(),
            event.description.lower(),
            ' '.join(event.tags).lower()
        ])
        
        if search_term in searchable_text:
            filtered_events.append(event)
    
    return filtered_events

def filter_events(events: List[Event], tag_filter: str) -> List[Event]:
    """Filter events by tag"""
    if not tag_filter:
        return events
    
    tag_filter = tag_filter.lower().strip()
    return [event for event in events if tag_filter in [tag.lower() for tag in event.tags]]

def sort_events(events: List[Event], sort_by: str = 'date', sort_order: str = 'asc') -> List[Event]:
    """Sort events by specified field and order"""
    reverse = sort_order.lower() == 'desc'
    
    try:
        if sort_by == 'name':
            return sorted(events, key=lambda x: x.name.lower(), reverse=reverse)
        elif sort_by == 'location':
            return sorted(events, key=lambda x: x.location.lower(), reverse=reverse)
        elif sort_by == 'created_at':
            return sorted(events, key=lambda x: x.created_at, reverse=reverse)
        elif sort_by == 'updated_at':
            return sorted(events, key=lambda x: x.updated_at, reverse=reverse)
        else:  # default to date
            return sorted(events, key=lambda x: parse_date_for_sorting(x.date), reverse=reverse)
    except Exception:
        # Fallback to name sorting if there's an error
        return sorted(events, key=lambda x: x.name.lower(), reverse=reverse)

def parse_date_for_sorting(date_str: str) -> datetime:
    """Parse date string for sorting, with fallback for invalid dates"""
    try:
        # Handle various date formats
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        # Return a default date for invalid formats (far in future for desc, past for asc)
        return datetime.min

def format_date_display(date_str: str) -> str:
    """Format date string for display"""
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        else:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%B %d, %Y')
    except ValueError:
        return date_str  # Return original if parsing fails

def validate_event_data(data: dict) -> List[str]:
    """Validate event data and return list of errors"""
    errors = []
    
    # Required fields
    required_fields = ['name', 'date', 'location']
    for field in required_fields:
        if not data.get(field, '').strip():
            errors.append(f"{field.title()} is required")
    
    # Date validation
    if data.get('date'):
        try:
            datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            errors.append("Invalid date format")
    
    # Length validations
    if len(data.get('name', '')) > 100:
        errors.append("Event name must be less than 100 characters")
    
    if len(data.get('location', '')) > 200:
        errors.append("Location must be less than 200 characters")
    
    if len(data.get('description', '')) > 1000:
        errors.append("Description must be less than 1000 characters")
    
    return errors
