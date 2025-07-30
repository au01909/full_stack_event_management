# EventFlow 🗓️

A modern event management web application built with Flask, PostgreSQL, and Redis, supporting real-time updates, user authentication, and dynamic modals for a seamless user experience.

---

## 🚀 Features

- 🔐 **User Authentication** (Login, Register, Logout)
- 👤 **User-Specific Events**: Events tied to logged-in users
- 📅 **Event CRUD Operations**:
  - Create, Edit, Delete, View
  - All through Bootstrap modals
- ⚡ **Live UI Updates** with Fetch API (no page reloads)
- 🧠 **Permissions** enforced: Only creators can edit/delete
- 🧾 **Logging**: All actions are logged for transparency
- 📦 **PostgreSQL**: Structured event/user data
- 💾 **Redis (Planned)**: For real-time pub/sub updates
- 🐳 **Docker-ready** deployment architecture

---

## 🧠 Tech Stack

| Layer             | Technology           |
|------------------|----------------------|
| Backend          | Flask + SQLAlchemy   |
| Frontend         | Bootstrap + JS       |
| Database         | PostgreSQL           |
| Real-time Layer  | Redis (via pub/sub)  |
| Auth             | Flask-Login          |
| Deployment       | Gunicorn, Docker     |
| ORM              | SQLAlchemy           |
| Logging          | Python's logging     |

## ✅ Setup & Run Locally

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/EventFlow.git
cd EventFlow
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

2. Configure Environment
Create .env file:

env
Copy
Edit
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret
DATABASE_URL=postgresql://user:password@localhost/eventflow

3. Run the App
bash
Copy
Edit
flask db init
flask db migrate
flask db upgrade
flask run


🔍 How It Works
🧾 Auth System
  Built using Flask-Login
  Routes: /login, /register, /logout
  Passwords hashed with werkzeug.security

📅 Events
  Stored in PostgreSQL
  Events have user_id foreign key
  Only owner can edit/delete
  Fetched dynamically using /api/events

⚡ Frontend Modals
  Bootstrap-based modals
  Event editing/deleting via JS fetch()
  Confirmation and loading spinners supported

🧠 Security
  Routes protected with @login_required
  Deletion checked against current_user.id

🛠️ Logging
  All actions (create/edit/delete) are logged with timestamps and user info

