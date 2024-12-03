import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app import create_app, db
from app.models import Task



@pytest.fixture
def app():
    """Fixture for creating a Flask app with an in-memory SQLite database for testing."""
    app = create_app()
    
    # Use an in-memory database for tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Create the database schema (tables) for tests
    with app.app_context():
        db.create_all()

    yield app

    # Clean up after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture to create and return a test client."""
    return app.test_client()

def test_add_task(client):
    """Test the creation of a new task."""
    response = client.post('/api/todos', json={'title': 'Test Task', 'description': 'Test description'})
    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'
    assert response.json['description'] == 'Test description'
    assert response.json['completed'] is False  # Default value

def test_get_tasks(client):
    """Test fetching all tasks."""
    client.post('/api/todos', json={'title': 'Test Task 1', 'description': 'Description for task 1'})
    client.post('/api/todos', json={'title': 'Test Task 2', 'description': 'Description for task 2'})
    response = client.get('/api/todos')
    assert response.status_code == 200
    tasks = response.json
    assert len(tasks) == 2
    assert any(task['title'] == 'Test Task 1' for task in tasks)
    assert any(task['title'] == 'Test Task 2' for task in tasks)

def test_update_task(client):
    """Test updating an existing task."""
    response = client.post('/api/todos', json={'title': 'Test Task', 'description': 'Test description'})
    task_id = response.json['id']
    response = client.put(f'/api/todos/{task_id}', json={'title': 'Updated Task', 'completed': True})
    assert response.status_code == 200
    assert response.json['title'] == 'Updated Task'
    assert response.json['completed'] is True

def test_delete_task(client):
    """Test deleting a task."""
    response = client.post('/api/todos', json={'title': 'Test Task', 'description': 'Test description'})
    task_id = response.json['id']
    # Deleting the task
    response = client.delete(f'/api/todos/{task_id}')
    assert response.status_code == 204  # Task should be deleted

    # Attempting to get the deleted task should return 404
    response = client.get(f'/api/todos/{task_id}')
    assert response.status_code == 404  # Task is deleted, so 404 should be returned


def test_delete_all_tasks(client):
    """Test deleting all tasks."""
    client.post('/api/todos', json={'title': 'Task 1', 'description': 'Description 1'})
    client.post('/api/todos', json={'title': 'Task 2', 'description': 'Description 2'})
    response = client.delete('/api/todos/all')
    assert response.status_code == 204
    response = client.get('/api/todos')
    assert len(response.json) == 0
