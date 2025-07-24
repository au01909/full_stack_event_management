from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
import logging

from app import app, db
from models import User, Event

# Configure logging
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Landing page - redirect to dashboard if logged in, otherwise show login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            errors.append('Username already exists')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        # Create new user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = bool(request.form.get('remember_me'))
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing their events"""
    # Get search and filter parameters
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'date')
    sort_order = request.args.get('order', 'asc')
    tag_filter = request.args.get('tag', '').strip()
    
    # Query user's events
    query = Event.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if search:
        query = query.filter(
            Event.name.ilike(f'%{search}%') |
            Event.location.ilike(f'%{search}%') |
            Event.description.ilike(f'%{search}%')
        )
    
    # Apply tag filter
    if tag_filter:
        query = query.filter(Event.tags.ilike(f'%{tag_filter}%'))
    
    # Apply sorting
    if sort_by == 'name':
        if sort_order == 'desc':
            query = query.order_by(Event.name.desc())
        else:
            query = query.order_by(Event.name.asc())
    elif sort_by == 'location':
        if sort_order == 'desc':
            query = query.order_by(Event.location.desc())
        else:
            query = query.order_by(Event.location.asc())
    else:  # date
        if sort_order == 'desc':
            query = query.order_by(Event.date.desc())
        else:
            query = query.order_by(Event.date.asc())
    
    events = query.all()
    
    # Convert to dict format for template
    events_data = [event.to_dict() for event in events]
    
    return render_template('dashboard.html', 
                         events=events_data,
                         user=current_user,
                         search=search,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         tag_filter=tag_filter)


@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new event"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            # Create new event
            event = Event(
                name=data['name'],
                date=data['date'],
                location=data['location'],
                description=data.get('description', ''),
                tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', ''),
                user_id=current_user.id
            )
            
            # Validate
            errors = event.validate()
            if errors:
                if request.is_json:
                    return jsonify({'success': False, 'errors': errors}), 400
                else:
                    for error in errors:
                        flash(error, 'danger')
                    return render_template('create_event.html')
            
            # Save to database
            db.session.add(event)
            db.session.commit()
            
            logger.info(f"Event created: {event.name} by user {current_user.username}")
            
            if request.is_json:
                return jsonify({'success': True, 'event': event.to_dict()})
            else:
                flash('Event created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            db.session.rollback()
            
            if request.is_json:
                return jsonify({'success': False, 'error': 'Failed to create event'}), 500
            else:
                flash('Failed to create event. Please try again.', 'danger')
                return render_template('create_event.html')
    
    return render_template('create_event.html')


@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Edit an existing event"""
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first()
    
    if not event:
        flash('Event not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            # Update event
            event.update_from_dict(data)
            
            # Validate
            errors = event.validate()
            if errors:
                if request.is_json:
                    return jsonify({'success': False, 'errors': errors}), 400
                else:
                    for error in errors:
                        flash(error, 'danger')
                    return render_template('edit_event.html', event=event.to_dict())
            
            # Save to database
            db.session.commit()
            
            logger.info(f"Event updated: {event.name} by user {current_user.username}")
            
            if request.is_json:
                return jsonify({'success': True, 'event': event.to_dict()})
            else:
                flash('Event updated successfully!', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            db.session.rollback()
            
            if request.is_json:
                return jsonify({'success': False, 'error': 'Failed to update event'}), 500
            else:
                flash('Failed to update event. Please try again.', 'danger')
                return render_template('edit_event.html', event=event.to_dict())
    
    return render_template('edit_event.html', event=event.to_dict())


@app.route('/events/delete/<int:event_id>', methods=['POST', 'DELETE'])
@login_required
def delete_event(event_id):
    """Delete an event"""
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first()
    
    if not event:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        else:
            flash('Event not found or you do not have permission to delete it.', 'danger')
            return redirect(url_for('dashboard'))
    
    try:
        event_name = event.name
        db.session.delete(event)
        db.session.commit()
        
        logger.info(f"Event deleted: {event_name} by user {current_user.username}")
        
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash(f'Event "{event_name}" deleted successfully!', 'success')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        db.session.rollback()
        
        if request.is_json:
            return jsonify({'success': False, 'error': 'Failed to delete event'}), 500
        else:
            flash('Failed to delete event. Please try again.', 'danger')
            return redirect(url_for('dashboard'))


# API Routes for AJAX calls
@app.route('/api/events')
@login_required
def api_get_events():
    """API endpoint to get user's events"""
    try:
        # Get filter parameters
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'date')
        sort_order = request.args.get('order', 'asc')
        tag_filter = request.args.get('tag', '').strip()
        
        # Query user's events
        query = Event.query.filter_by(user_id=current_user.id)
        
        # Apply filters (same logic as dashboard)
        if search:
            query = query.filter(
                Event.name.ilike(f'%{search}%') |
                Event.location.ilike(f'%{search}%') |
                Event.description.ilike(f'%{search}%')
            )
        
        if tag_filter:
            query = query.filter(Event.tags.ilike(f'%{tag_filter}%'))
        
        # Apply sorting
        if sort_by == 'name':
            query = query.order_by(Event.name.desc() if sort_order == 'desc' else Event.name.asc())
        elif sort_by == 'location':
            query = query.order_by(Event.location.desc() if sort_order == 'desc' else Event.location.asc())
        else:  # date
            query = query.order_by(Event.date.desc() if sort_order == 'desc' else Event.date.asc())
        
        events = query.all()
        events_data = [event.to_dict() for event in events]
        
        return jsonify({'success': True, 'events': events_data})
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch events'}), 500


@app.route('/api/events/<int:event_id>')
@login_required
def api_get_event(event_id):
    """API endpoint to get a specific event"""
    try:
        event = Event.query.filter_by(id=event_id, user_id=current_user.id).first()
        
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({'success': True, 'event': event.to_dict()})
        
    except Exception as e:
        logger.error(f"Error fetching event: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch event'}), 500


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403