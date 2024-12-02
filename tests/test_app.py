import pytest
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app, mongo

@pytest.fixture
def app():
    app = create_app()
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_todo_db'

    mongo.init_app(app)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_add_task(client):
    response = client.post('/api/todos/', json={'title': 'Test Task', 'description': 'Test Description'})
    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'

def test_get_tasks(client):
    client.post('/api/todos/', json={'title': 'Test Task', 'description': 'Test Description'})
    response = client.get('/api/todos/')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_update_task(client):
    response = client.post('/api/todos/', json={'title': 'Test Task', 'description': 'Test Description'})
    task_id = response.json['_id']
    response = client.put(f'/api/todos/{task_id}', json={'title': 'Updated Task', 'completed': True})
    assert response.status_code == 200
    assert response.json['title'] == 'Updated Task'
    assert response.json['completed'] is True

def test_delete_task(client):
    response = client.post('/api/todos/', json={'title': 'Test Task', 'description': 'Test Description'})
    task_id = response.json['_id']
    response = client.delete(f'/api/todos/{task_id}')
    assert response.status_code == 200
    assert response.json['message'] == 'Task deleted'

def test_delete_all_tasks(client):
    client.post('/api/todos/', json={'title': 'Test Task 1', 'description': 'Test Description 1'})
    client.post('/api/todos/', json={'title': 'Test Task 2', 'description': 'Test Description 2'})
    response = client.delete('/api/todos/all')
    assert response.status_code == 200
    assert response.json['message'] == 'All tasks deleted'
