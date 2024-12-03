from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# Allow the frontend URL hosted on Render
CORS(app)

# MongoDB connection
def get_mongo_client():
    # Establish MongoDB client inside the function to avoid connection issues in multi-threaded environments
    return MongoClient("mongodb://localhost:27017/todo_db")

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Todo API!"

@app.route('/api/todos', methods=['GET'])
def get_tasks():
    client = get_mongo_client()  # Create a new connection for each request
    db = client.todo_database
    todo_tasks = db.todo_tasks
    tasks = list(todo_tasks.find())
    for task in tasks:
        task['_id'] = str(task['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(tasks)

@app.route('/api/todos', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'title' not in data:
        abort(400, 'Title is required')
    
    client = get_mongo_client()  # Create a new connection for each request
    db = client.todo_database
    todo_tasks = db.todo_tasks

    task = {
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': data.get('completed', False)
    }

    result = todo_tasks.insert_one(task)
    task['_id'] = str(result.inserted_id)

    return jsonify(task), 201

@app.route('/api/todos/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    
    client = get_mongo_client()  # Create a new connection for each request
    db = client.todo_database
    todo_tasks = db.todo_tasks
    
    task = todo_tasks.find_one({'_id': ObjectId(task_id)})
    if not task:
        abort(404, 'Task not found')

    updated_task = {
        'title': data.get('title', task['title']),
        'description': data.get('description', task['description']),
        'completed': data.get('completed', task['completed'])
    }

    todo_tasks.update_one({'_id': ObjectId(task_id)}, {'$set': updated_task})
    updated_task['_id'] = task_id

    return jsonify(updated_task)

@app.route('/api/todos/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    client = get_mongo_client()  # Create a new connection for each request
    db = client.todo_database
    todo_tasks = db.todo_tasks

    result = todo_tasks.delete_one({'_id': ObjectId(task_id)})
    if result.deleted_count == 0:
        abort(404, 'Task not found')
    return '', 204

@app.route('/api/todos/all', methods=['DELETE'])
def delete_all_tasks():
    client = get_mongo_client()  # Create a new connection for each request
    db = client.todo_database
    todo_tasks = db.todo_tasks
    
    todo_tasks.delete_many({})
    return '', 204

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use the Render-provided port
    app.run(debug=True, host="0.0.0.0", port=port)
