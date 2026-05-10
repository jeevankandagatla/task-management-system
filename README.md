# Smart Task Management System

A comprehensive task management application built with Python (Flask), PostgreSQL, and modern web technologies.

## Features

- **Authentication**: Secure user registration, login, and logout.
- **REST API**: Full CRUD operations for tasks (Title, Description, Priority, Status).
- **PostgreSQL Integration**: Persistent data storage with structured relations.
- **Analytics Module**: Real-time stats (Total, Completed, Pending, %) powered by Pandas & NumPy.
- **WebSockets**: Live notifications when tasks are added, updated, or deleted.
- **Premium UI**: Clean, responsive dashboard design.

## Technical Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-SocketIO
- **Database**: PostgreSQL
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML5, CSS3 (Modern design), Vanilla JavaScript

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   - Ensure PostgreSQL is installed and running.
   - Create a database named `task_db`.
   - Update the `SQLALCHEMY_DATABASE_URI` in `app.py` if your credentials differ from the default (`postgresql://postgres:postgres@localhost/task_db`).

3. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:5000`.

## Project Structure

- `app.py`: Main entry point and API routes.
- `models.py`: SQLAlchemy database models.
- `analytics.py`: Data processing logic using Pandas/NumPy.
- `templates/`: HTML templates (Dashboard, Login, Register).
- `static/`: CSS styling and JavaScript logic.

## Scalability Note

This application is designed with a clear separation of concerns. To scale:
- **Backend**: Use Gunicorn or uWSGI for production serving.
- **WebSockets**: Use Redis as a message broker for horizontal scaling.
- **Database**: Implement indexing on `user_id` and `status` fields for faster analytics on large datasets.
