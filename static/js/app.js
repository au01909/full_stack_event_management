// EventEase - Main JavaScript Application
class EventManager {
    constructor() {
        this.currentEventId = null;
        this.isEditing = false;
        this.toastContainer = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.createToastContainer();
        this.loadEvents();
    }

    setupEventListeners() {
        // Search and filter events
        document.getElementById('searchInput').addEventListener('input', this.debounce(() => {
            this.applyFilters();
        }, 300));

        document.getElementById('sortBy').addEventListener('change', () => {
            this.applyFilters();
        });

        document.getElementById('sortOrder').addEventListener('change', () => {
            this.applyFilters();
        });

        document.getElementById('tagFilter').addEventListener('change', () => {
            this.applyFilters();
        });

        // Event form submission
        document.getElementById('eventForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEventSubmit();
        });

        // Delete confirmation
        document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
            this.confirmDelete();
        });

        // Modal events
        document.getElementById('eventModal').addEventListener('hidden.bs.modal', () => {
            this.resetEventForm();
        });
    }

    createToastContainer() {
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'toast-container';
        document.body.appendChild(this.toastContainer);
    }

    showToast(message, type = 'success') {
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        this.toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    applyFilters() {
        const search = document.getElementById('searchInput').value;
        const sortBy = document.getElementById('sortBy').value;
        const sortOrder = document.getElementById('sortOrder').value;
        const tag = document.getElementById('tagFilter').value;

        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (sortBy) params.append('sort_by', sortBy);
        if (sortOrder) params.append('sort_order', sortOrder);
        if (tag) params.append('tag', tag);

        // Update URL without page reload
        const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
        window.history.pushState({}, '', newUrl);

        this.loadEvents();
    }

    async loadEvents() {
        try {
            const params = new URLSearchParams(window.location.search);
            const response = await fetch('/api/events?' + params.toString());
            const data = await response.json();

            if (data.success) {
                this.renderEvents(data.events);
            } else {
                throw new Error(data.error || 'Failed to load events');
            }
        } catch (error) {
            console.error('Error loading events:', error);
            this.showToast('Failed to load events', 'danger');
        }
    }

    renderEvents(events) {
        const container = document.getElementById('eventsContainer');
        
        if (events.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="card">
                        <div class="card-body text-center py-5">
                            <i class="fas fa-calendar-times fa-3x text-muted mb-3"></i>
                            <h4>No Events Found</h4>
                            <p class="text-muted">
                                ${document.getElementById('searchInput').value || document.getElementById('tagFilter').value ? 
                                    'No events match your current filters. Try adjusting your search criteria.' : 
                                    'Get started by creating your first event!'}
                            </p>
                            <button class="btn btn-primary" onclick="openEventModal()">
                                <i class="fas fa-plus me-2"></i>Create Your First Event
                            </button>
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        const eventsHtml = events.map(event => this.renderEventCard(event)).join('');
        container.innerHTML = eventsHtml;
        
        // Add fade-in animation
        container.classList.add('fade-in-up');
        setTimeout(() => container.classList.remove('fade-in-up'), 300);
    }

    renderEventCard(event) {
        const formattedDate = this.formatDate(event.date);
        const createdDate = this.formatDate(event.created_at);
        const tags = event.tags || [];
        const description = event.description || '';
        
        return `
            <div class="col-lg-6 col-xl-4 mb-4">
                <div class="card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="card-title mb-0">${this.escapeHtml(event.name)}</h6>
                        <div class="dropdown">
                            <button class="btn btn-outline-secondary btn-sm" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="editEvent('${event.id}')">
                                    <i class="fas fa-edit me-2"></i>Edit
                                </a></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="deleteEvent('${event.id}', '${this.escapeHtml(event.name)}')">
                                    <i class="fas fa-trash me-2"></i>Delete
                                </a></li>
                            </ul>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <small class="text-muted d-block">
                                <i class="fas fa-calendar me-1"></i>${formattedDate}
                            </small>
                            <small class="text-muted d-block">
                                <i class="fas fa-map-marker-alt me-1"></i>${this.escapeHtml(event.location)}
                            </small>
                        </div>
                        
                        ${description ? `<p class="card-text">${this.escapeHtml(description.substring(0, 150))}${description.length > 150 ? '...' : ''}</p>` : ''}
                        
                        ${tags.length > 0 ? `
                        <div class="mb-2">
                            ${tags.map(tag => `<span class="badge bg-secondary me-1">${this.escapeHtml(tag)}</span>`).join('')}
                        </div>
                        ` : ''}
                    </div>
                    <div class="card-footer text-muted">
                        <small>Created ${createdDate}</small>
                    </div>
                </div>
            </div>
        `;
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            const options = {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            return date.toLocaleDateString('en-US', options);
        } catch (error) {
            return dateString;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async handleEventSubmit() {
        const form = document.getElementById('eventForm');
        const submitBtn = document.getElementById('eventSubmitBtn');
        const spinner = document.getElementById('submitSpinner');
        const btnText = document.getElementById('submitBtnText');

        // Clear previous validation
        this.clearFormValidation();

        // Get form data
        const formData = new FormData(form);
        const eventData = {
            name: formData.get('name').trim(),
            date: formData.get('date'),
            location: formData.get('location').trim(),
            description: formData.get('description').trim(),
            tags: formData.get('tags').trim()
        };

        // Client-side validation
        const errors = this.validateEventData(eventData);
        if (errors.length > 0) {
            this.displayFormErrors(errors);
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        btnText.textContent = this.isEditing ? 'Updating...' : 'Creating...';

        try {
            const url = this.isEditing ? `/api/events/${this.currentEventId}` : '/api/events';
            const method = this.isEditing ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            });

            const data = await response.json();

            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
                modal.hide();
                
                this.showToast(data.message || (this.isEditing ? 'Event updated successfully' : 'Event created successfully'));
                this.loadEvents();
                this.updateStats();
            } else {
                if (data.errors) {
                    this.displayFormErrors(data.errors);
                } else {
                    throw new Error(data.error || 'Failed to save event');
                }
            }
        } catch (error) {
            console.error('Error saving event:', error);
            this.showToast('Failed to save event', 'danger');
        } finally {
            // Reset loading state
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
            btnText.textContent = this.isEditing ? 'Update Event' : 'Create Event';
        }
    }

    validateEventData(data) {
        const errors = [];

        if (!data.name) {
            errors.push({ field: 'name', message: 'Event name is required' });
        } else if (data.name.length > 100) {
            errors.push({ field: 'name', message: 'Event name must be less than 100 characters' });
        }

        if (!data.date) {
            errors.push({ field: 'date', message: 'Event date is required' });
        }

        if (!data.location) {
            errors.push({ field: 'location', message: 'Event location is required' });
        } else if (data.location.length > 200) {
            errors.push({ field: 'location', message: 'Location must be less than 200 characters' });
        }

        if (data.description && data.description.length > 1000) {
            errors.push({ field: 'description', message: 'Description must be less than 1000 characters' });
        }

        return errors;
    }

    displayFormErrors(errors) {
        const form = document.getElementById('eventForm');
        form.classList.add('was-validated');

        // Clear previous errors
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');

        // Display new errors
        errors.forEach(error => {
            let fieldName, message;
            
            if (typeof error === 'string') {
                // Handle simple string errors
                message = error;
                // Try to guess field from message
                if (error.toLowerCase().includes('name')) fieldName = 'name';
                else if (error.toLowerCase().includes('date')) fieldName = 'date';
                else if (error.toLowerCase().includes('location')) fieldName = 'location';
                else if (error.toLowerCase().includes('description')) fieldName = 'description';
            } else {
                fieldName = error.field;
                message = error.message;
            }

            if (fieldName) {
                const field = form.querySelector(`[name="${fieldName}"]`);
                const feedback = field?.parentElement.querySelector('.invalid-feedback');
                
                if (field && feedback) {
                    field.classList.add('is-invalid');
                    feedback.textContent = message;
                }
            }
        });
    }

    clearFormValidation() {
        const form = document.getElementById('eventForm');
        form.classList.remove('was-validated');
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
    }

    resetEventForm() {
        const form = document.getElementById('eventForm');
        form.reset();
        this.clearFormValidation();
        this.currentEventId = null;
        this.isEditing = false;
        
        document.getElementById('eventModalTitle').textContent = 'Add New Event';
        document.getElementById('submitBtnText').textContent = 'Create Event';
    }

    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                // Update stats display
                const statsElements = document.querySelectorAll('.card-title');
                if (statsElements.length >= 2) {
                    statsElements[0].textContent = data.stats.total_events || 0;
                    statsElements[1].textContent = data.stats.unique_tags || 0;
                }
                
                // Update tag filter dropdown
                this.updateTagFilter(data.stats.all_tags || []);
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    updateTagFilter(tags) {
        const tagFilter = document.getElementById('tagFilter');
        const currentValue = tagFilter.value;
        
        // Clear existing options except "All Tags"
        tagFilter.innerHTML = '<option value="">All Tags</option>';
        
        // Add new tag options
        tags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = tag;
            if (tag === currentValue) {
                option.selected = true;
            }
            tagFilter.appendChild(option);
        });
    }

    async confirmDelete() {
        const deleteBtn = document.getElementById('confirmDeleteBtn');
        const spinner = document.getElementById('deleteSpinner');
        
        deleteBtn.disabled = true;
        spinner.classList.remove('d-none');

        try {
            const response = await fetch(`/api/events/${this.currentEventId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
                modal.hide();
                
                this.showToast(data.message || 'Event deleted successfully');
                this.loadEvents();
                this.updateStats();
            } else {
                throw new Error(data.error || 'Failed to delete event');
            }
        } catch (error) {
            console.error('Error deleting event:', error);
            this.showToast('Failed to delete event', 'danger');
        } finally {
            deleteBtn.disabled = false;
            spinner.classList.add('d-none');
        }
    }
}

// Global functions for event handling
let eventManager;

document.addEventListener('DOMContentLoaded', () => {
    eventManager = new EventManager();
});

function openEventModal() {
    eventManager.resetEventForm();
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    modal.show();
}

async function editEvent(eventId) {
    try {
        const response = await fetch(`/api/events/${eventId}`);
        const data = await response.json();

        if (data.success) {
            const event = data.event;
            
            // Populate form
            document.getElementById('eventName').value = event.name;
            document.getElementById('eventDate').value = event.date;
            document.getElementById('eventLocation').value = event.location;
            document.getElementById('eventDescription').value = event.description || '';
            document.getElementById('eventTags').value = (event.tags || []).join(', ');

            // Set editing state
            eventManager.currentEventId = eventId;
            eventManager.isEditing = true;
            
            document.getElementById('eventModalTitle').textContent = 'Edit Event';
            document.getElementById('submitBtnText').textContent = 'Update Event';

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('eventModal'));
            modal.show();
        } else {
            throw new Error(data.error || 'Failed to load event');
        }
    } catch (error) {
        console.error('Error loading event for editing:', error);
        eventManager.showToast('Failed to load event for editing', 'danger');
    }
}

function deleteEvent(eventId, eventName) {
    eventManager.currentEventId = eventId;
    document.getElementById('deleteEventName').textContent = eventName;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('sortBy').value = 'date';
    document.getElementById('sortOrder').value = 'asc';
    document.getElementById('tagFilter').value = '';
    
    // Clear URL parameters
    window.history.pushState({}, '', window.location.pathname);
    
    eventManager.loadEvents();
}

function refreshEvents() {
    eventManager.loadEvents();
    eventManager.updateStats();
    eventManager.showToast('Events refreshed successfully');
}
