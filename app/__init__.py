from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Initialize the SQLAlchemy instance outside the create_app function
db = SQLAlchemy()

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)

    # Allow the frontend URL hosted on Render (CORS)
    CORS(app)

    # SQLite Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///todo.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the SQLAlchemy with the app
    db.init_app(app)

    # Import the Task model after db initialization to avoid circular import
    from .models import Task  # Using relative import

    # Initialize the database schema (tables) in app context
    with app.app_context():
        db.create_all()

    # Define routes
    @app.route('/', methods=['GET'])
    def home():
        return "Welcome to the Todo API!"

    @app.route('/api/todos', methods=['GET'])
    def get_tasks():
        tasks = Task.query.all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        } for task in tasks])

    @app.route('/api/todos', methods=['POST'])
    def add_task():
        data = request.get_json()
        if not data or 'title' not in data:
            abort(400, 'Title is required')

        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        }), 201

    @app.route('/api/todos/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        """Retrieve a specific task by task_id."""
        task = db.session.get(Task, task_id)  # Use session.get() to avoid deprecation warnings
        if not task:
            abort(404, 'Task not found')
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        })

    @app.route('/api/todos/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        """Update an existing task."""
        data = request.get_json()

        task = db.session.get(Task, task_id)  # Use session.get() to avoid deprecation warnings
        if not task:
            abort(404, 'Task not found')

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)

        db.session.commit()

        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        })

    @app.route('/api/todos/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        """Delete a task."""
        task = db.session.get(Task, task_id)  # Use session.get() to avoid deprecation warnings
        if not task:
            abort(404, 'Task not found')

        db.session.delete(task)
        db.session.commit()

        return '', 204

    @app.route('/api/todos/all', methods=['DELETE'])
    def delete_all_tasks():
        """Delete all tasks."""
        Task.query.delete()
        db.session.commit()
        return '', 204

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": str(error)}), 400

    return app
