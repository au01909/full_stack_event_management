# EventEase - Event Management System

## Overview

EventEase is a Flask-based web application for managing events with a modern, visually appealing interface. The application provides comprehensive CRUD operations for events with advanced features like search, filtering, sorting, and tagging. It uses JSON file storage for data persistence and features a stunning glassmorphism design with gradient backgrounds, enhanced animations, and professional UI elements built with Bootstrap.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: HTML templates with Jinja2 templating engine
- **UI Framework**: Bootstrap 5 with enhanced dark theme and glassmorphism design
- **JavaScript**: Vanilla JavaScript with ES6 classes for client-side interactions
- **Styling**: Advanced CSS with gradient backgrounds, backdrop filters, and modern animations
- **Visual Design**: Glassmorphism effects, gradient overlays, enhanced card hover effects
- **Icons**: Font Awesome with gradient text effects and enhanced typography

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: MVC (Model-View-Controller)
- **CORS**: Enabled for API access
- **Middleware**: ProxyFix for deployment behind reverse proxies
- **Logging**: Built-in Python logging for debugging and monitoring

### Data Storage
- **Primary Storage**: JSON file-based persistence (`events_data.json`)
- **Rationale**: Simple, lightweight solution without external database dependencies
- **Data Model**: Event objects with UUID identifiers, timestamps, and metadata

## Key Components

### Models (`models.py`)
- **Event Class**: Core data model with fields for name, date, location, description, tags
- **Features**: UUID generation, timestamps, dictionary serialization/deserialization
- **Methods**: `to_dict()`, `from_dict()`, `update()`

### Data Management (`data_manager.py`)
- **DataManager Class**: Handles all data persistence operations
- **Features**: JSON file I/O, event CRUD operations, search/filter/sort functionality
- **Error Handling**: Graceful fallbacks for file operations and JSON parsing

### Routes (`routes.py`)
- **Web Routes**: Main dashboard interface (`/`)
- **API Endpoints**: RESTful API for event operations (`/api/events`)
- **Features**: Parameter-based filtering, sorting, and searching

### Utilities (`utils.py`)
- **Search Function**: Text-based search across event fields
- **Filter Function**: Tag-based filtering
- **Sort Function**: Multi-field sorting with date parsing
- **Date Utilities**: Date formatting and parsing helpers

### Frontend (`static/js/app.js`)
- **EventManager Class**: Client-side application logic
- **Features**: AJAX operations, form handling, real-time filtering
- **UI Interactions**: Modal management, toast notifications, debounced search

## Data Flow

1. **Request Flow**: Client → Flask Routes → DataManager → JSON Storage
2. **Response Flow**: JSON Storage → DataManager → Flask Routes → Template Rendering → Client
3. **API Flow**: Client JavaScript → Flask API → DataManager → JSON Response
4. **Search/Filter**: Client input → JavaScript filtering → Server-side processing → Updated UI

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: WSGI utilities and middleware

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme variant
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: No external JS frameworks

### Browser APIs
- **Fetch API**: For AJAX requests
- **Local Storage**: For client-side state persistence
- **DOM API**: For dynamic UI updates

## Deployment Strategy

### Current Setup
- **Entry Point**: `main.py` runs Flask development server
- **Host Configuration**: `0.0.0.0:5000` for container/cloud deployment
- **Debug Mode**: Enabled for development
- **Static Files**: Served by Flask in development

### Production Considerations
- **WSGI Server**: Ready for Gunicorn or uWSGI deployment
- **Proxy Support**: ProxyFix middleware configured for reverse proxy setup
- **Environment Variables**: Session secret configurable via environment
- **Data Persistence**: JSON file storage in application directory

### Scalability Notes
- **Current Limitation**: Single JSON file may not scale for large datasets
- **Future Enhancement**: Easy migration path to database storage (SQLite, PostgreSQL)
- **Session Management**: Flask sessions configured but minimal usage
- **Static Assets**: CDN-ready for external asset delivery