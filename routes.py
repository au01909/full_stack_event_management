from flask import render_template, request, jsonify, flash, redirect, url_for
from app import app, data_manager
from utils import format_date_display
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page with event management interface"""
    try:
        # Get query parameters for filtering and sorting
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'date')
        sort_order = request.args.get('sort_order', 'asc')
        tag_filter = request.args.get('tag', '')
        
        # Get events with filters applied
        events = data_manager.get_all_events(
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            tag_filter=tag_filter
        )
        
        # Get statistics
        stats = data_manager.get_stats()
        
        return render_template('index.html', 
                             events=events, 
                             stats=stats,
                             search=search,
                             sort_by=sort_by,
                             sort_order=sort_order,
                             tag_filter=tag_filter,
                             format_date=format_date_display)
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        flash('Error loading events', 'error')
        return render_template('index.html', events=[], stats={})

# REST API Endpoints

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with optional filtering and sorting"""
    try:
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'date')
        sort_order = request.args.get('sort_order', 'asc')
        tag_filter = request.args.get('tag', '')
        
        events = data_manager.get_all_events(
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            tag_filter=tag_filter
        )
        
        return jsonify({
            'success': True,
            'events': [event.to_dict() for event in events],
            'total': len(events)
        })
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch events'}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Parse tags if provided as string
        if isinstance(data.get('tags'), str):
            data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        
        event, errors = data_manager.create_event(data)
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        return jsonify({
            'success': True,
            'event': event.to_dict(),
            'message': 'Event created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return jsonify({'success': False, 'error': 'Failed to create event'}), 500

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by ID"""
    try:
        event = data_manager.get_event(event_id)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({
            'success': True,
            'event': event.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch event'}), 500

@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Parse tags if provided as string
        if isinstance(data.get('tags'), str):
            data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        
        event, errors = data_manager.update_event(event_id, data)
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({
            'success': True,
            'event': event.to_dict(),
            'message': 'Event updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to update event'}), 500

@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        success = data_manager.delete_event(event_id)
        
        if not success:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Event deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete event'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get event statistics"""
    try:
        stats = data_manager.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch statistics'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    return render_template('index.html', events=[], stats={}), 404

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    flash('An error occurred', 'error')
    return render_template('index.html', events=[], stats={}), 500
