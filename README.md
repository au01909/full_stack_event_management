📅 EventFlow – Scalable Event Management App
EventFlow is a full-stack event management platform built using Flask, PostgreSQL, Redis, and Bootstrap. It supports user registration, login, and real-time CRUD operations on user-specific events via modals and asynchronous JavaScript. Designed for scalability and modern UX, EventFlow is perfect for personal use, small teams, or academic portfolios.

🚀 Features
🔐 User Authentication

Secure login/register via Flask-Login

Passwords hashed using Werkzeug

📅 Event CRUD (Create, Read, Update, Delete)

Users can manage their own events

Bootstrap modals and Fetch API for dynamic UI updates

Confirm delete dialogs with loading spinners

⚡ Real-Time UX

JS Fetch API for updating the UI without full page reloads

Spinner + toast feedback for user actions

🧠 Permissions & Logging

Events are tied to logged-in users only

All major actions logged with timestamps

🗃️ Database & Storage

PostgreSQL used via SQLAlchemy ORM

Redis ready for future real-time enhancements (e.g. live event feeds)

🐳 Deployment-Ready

Dockerfile + requirements.txt for easy setup

Scalable backend logic separated in blueprints

🧰 Tech Stack
Layer	Technology
Frontend	HTML, Bootstrap 5, JavaScript (Fetch API)
Backend	Python Flask (Blueprints, SQLAlchemy, Flask-Login)
Database	PostgreSQL (user & event models)
Real-time Prep	Redis (pub/sub hooks ready)
Deployment	Docker, Gunicorn, Nginx


🧪 Setup Instructions
🧱 Local Setup (Dev)
bash
Copy
Edit
# Clone the repo
git clone https://github.com/your-username/eventflow.git
cd eventflow

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # on Windows use venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL DB
createdb eventflow_db

# Run migrations
flask db upgrade

# Start the app
flask run
🐳 Docker Deployment
bash
Copy
Edit
# Build Docker image
docker build -t eventflow .

# Run container (configure ENV vars in Dockerfile or docker-compose)
docker run -p 8000:8000 eventflow
Add Nginx for production reverse proxy and SSL.

🌐 Core Endpoints
Method	Endpoint	Description
GET	/	Dashboard (auth required)
POST	/register	Register new user
POST	/login	Login user
GET	/logout	Logout user
POST	/events/create	Create new event
POST	/events/edit/<id>	Edit event
DELETE	/api/events/<id>	Delete event via JS API
