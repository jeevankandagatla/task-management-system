import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Task
from analytics import calculate_task_analytics
from datetime import datetime

app = Flask(__name__)

# Secret Key
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'smart-task-manager-secret-key'
)

# Database Configuration
database_url = os.environ.get(
    'DATABASE_URL',
    'sqlite:///task_db.sqlite'
)

# Fix Render PostgreSQL URL
if database_url.startswith('postgres://'):
    database_url = database_url.replace(
        'postgres://',
        'postgresql://',
        1
    )

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Using database: {'PostgreSQL' if 'postgresql' in database_url else 'SQLite'}")

# Initialize Extensions
CORS(app)

db.init_app(app)

# IMPORTANT: Create tables on startup (works on Render)
with app.app_context():
    try:
        db.create_all()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization error: {e}")

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading'
)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------------- USER LOADER ----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- FRONTEND ROUTES ----------------
@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('index'))

            flash('Invalid email or password')

        except Exception as e:
            print(f"Login Error: {e}")
            flash('Login failed')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            # Check existing user
            user_exists = User.query.filter(
                (User.email == email) |
                (User.username == username)
            ).first()

            if user_exists:
                flash('User already exists')
                return redirect(url_for('register'))

            # Create user
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            print(f"Register Error: {e}")
            flash('Registration failed')

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------------- TASK API ----------------
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Task.created_date.desc()
    ).all()

    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    try:
        data = request.json

        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'Medium'),
            user_id=current_user.id
        )

        db.session.add(new_task)
        db.session.commit()

        socketio.emit(
            'task_updated',
            {'message': f'New task added: {new_task.title}'},
            room=str(current_user.id)
        )

        return jsonify(new_task.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Add Task Error: {e}")
        return jsonify({'error': 'Failed to add task'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    try:
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user.id
        ).first_or_404()

        data = request.json

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.priority = data.get('priority', task.priority)
        task.status = data.get('status', task.status)

        db.session.commit()

        socketio.emit(
            'task_updated',
            {'message': f'Task updated: {task.title}'},
            room=str(current_user.id)
        )

        return jsonify(task.to_dict())

    except Exception as e:
        db.session.rollback()
        print(f"Update Task Error: {e}")
        return jsonify({'error': 'Failed to update task'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user.id
        ).first_or_404()

        db.session.delete(task)
        db.session.commit()

        socketio.emit(
            'task_updated',
            {'message': f'Task deleted: {task.title}'},
            room=str(current_user.id)
        )

        return jsonify({'message': 'Task deleted'})

    except Exception as e:
        db.session.rollback()
        print(f"Delete Task Error: {e}")
        return jsonify({'error': 'Failed to delete task'}), 500


# ---------------- ANALYTICS ----------------
@app.route('/api/analytics', methods=['GET'])
@login_required
def get_analytics():
    tasks = Task.query.filter_by(
        user_id=current_user.id
    ).all()

    tasks_data = [task.to_dict() for task in tasks]

    stats = calculate_task_analytics(tasks_data)

    return jsonify(stats)


# ---------------- SOCKET EVENTS ----------------
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        from flask_socketio import join_room

        join_room(str(current_user.id))

        print(f"User {current_user.id} connected.")


# ---------------- MAIN ----------------
if __name__ == '__main__':
    socketio.run(app, debug=True)