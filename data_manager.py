import json
import os
import logging
from typing import Dict, List, Optional
from models import Event
from utils import search_events, filter_events, sort_events

class DataManager:
    """Manages event data persistence using JSON file storage"""
    
    def __init__(self, data_file: str = "events_data.json"):
        self.data_file = data_file
        self.events: Dict[str, Event] = {}
        self.logger = logging.getLogger(__name__)
    
    def initialize_storage(self):
        """Initialize storage and load existing data"""
        try:
            if os.path.exists(self.data_file):
                self.load_events()
            else:
                self.save_events()
            self.logger.info(f"Data storage initialized with {len(self.events)} events")
        except Exception as e:
            self.logger.error(f"Error initializing storage: {e}")
            self.events = {}
    
    def load_events(self):
        """Load events from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.events = {
                    event_id: Event.from_dict(event_data)
                    for event_id, event_data in data.items()
                }
            self.logger.debug(f"Loaded {len(self.events)} events from {self.data_file}")
        except FileNotFoundError:
            self.events = {}
            self.logger.info("No existing data file found, starting with empty events")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON data: {e}")
            self.events = {}
        except Exception as e:
            self.logger.error(f"Error loading events: {e}")
            self.events = {}
    
    def save_events(self):
        """Save events to JSON file"""
        try:
            data = {
                event_id: event.to_dict()
                for event_id, event in self.events.items()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Saved {len(self.events)} events to {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error saving events: {e}")
            raise
    
    def create_event(self, event_data: Dict) -> tuple[Optional[Event], List[str]]:
        """Create a new event"""
        try:
            event = Event(
                name=event_data.get('name', ''),
                date=event_data.get('date', ''),
                location=event_data.get('location', ''),
                description=event_data.get('description', ''),
                tags=event_data.get('tags', [])
            )
            
            # Validate event
            errors = event.validate()
            if errors:
                return None, errors
            
            # Check for duplicate names
            for existing_event in self.events.values():
                if existing_event.name.lower() == event.name.lower():
                    return None, ["An event with this name already exists"]
            
            self.events[event.id] = event
            self.save_events()
            self.logger.info(f"Created event: {event.name} (ID: {event.id})")
            return event, []
            
        except Exception as e:
            self.logger.error(f"Error creating event: {e}")
            return None, ["Failed to create event"]
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        return self.events.get(event_id)
    
    def update_event(self, event_id: str, event_data: Dict) -> tuple[Optional[Event], List[str]]:
        """Update an existing event"""
        try:
            if event_id not in self.events:
                return None, ["Event not found"]
            
            event = self.events[event_id]
            
            # Update fields
            update_fields = {}
            for field in ['name', 'date', 'location', 'description', 'tags']:
                if field in event_data:
                    update_fields[field] = event_data[field]
            
            event.update(**update_fields)
            
            # Validate updated event
            errors = event.validate()
            if errors:
                return None, errors
            
            # Check for duplicate names (excluding current event)
            for existing_id, existing_event in self.events.items():
                if (existing_id != event_id and 
                    existing_event.name.lower() == event.name.lower()):
                    return None, ["An event with this name already exists"]
            
            self.save_events()
            self.logger.info(f"Updated event: {event.name} (ID: {event.id})")
            return event, []
            
        except Exception as e:
            self.logger.error(f"Error updating event: {e}")
            return None, ["Failed to update event"]
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            if event_id not in self.events:
                return False
            
            event_name = self.events[event_id].name
            del self.events[event_id]
            self.save_events()
            self.logger.info(f"Deleted event: {event_name} (ID: {event_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting event: {e}")
            return False
    
    def get_all_events(self, search: Optional[str] = None, sort_by: str = 'date', 
                       sort_order: str = 'asc', tag_filter: Optional[str] = None) -> List[Event]:
        """Get all events with optional filtering and sorting"""
        try:
            events_list = list(self.events.values())
            
            # Apply search filter
            if search:
                events_list = search_events(events_list, search)
            
            # Apply tag filter
            if tag_filter:
                events_list = filter_events(events_list, tag_filter)
            
            # Apply sorting
            events_list = sort_events(events_list, sort_by, sort_order)
            
            return events_list
            
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get statistics about events"""
        try:
            total_events = len(self.events)
            all_tags = set()
            for event in self.events.values():
                all_tags.update(event.tags)
            
            return {
                'total_events': total_events,
                'unique_tags': len(all_tags),
                'all_tags': sorted(list(all_tags))
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {'total_events': 0, 'unique_tags': 0, 'all_tags': []}
