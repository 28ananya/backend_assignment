from flask import Blueprint, request, jsonify, abort
from app import mongo
from bson.objectid import ObjectId  # Import ObjectId correctly
# 1. Add a new To-Do Task
from flask_cors import cross_origin

todo_bp = Blueprint('todo', __name__, url_prefix='/api/todos')
@cross_origin(origins=["http://localhost:3000"]) 
@todo_bp.route('/', methods=['POST']) # Allow CORS only for this route
def add_task():
    data = request.get_json()
    if not data or 'title' not in data:
        abort(400, 'Title is required')

    task = {
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': False
    }

    result = mongo.db.todo_tasks.insert_one(task)
    task['_id'] = str(result.inserted_id)

    return jsonify(task), 201


# 2. Display list of To-Do Tasks
@todo_bp.route('/', methods=['GET'])
def get_tasks():
    tasks = mongo.db.todo_tasks.find()
    tasks = [{**task, '_id': str(task['_id'])} for task in tasks]  # Convert ObjectId to string
    return jsonify(tasks)

# 3. Edit or delete a particular To-Do Task
@todo_bp.route('/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_task(task_id):
    # Use ObjectId from bson to convert task_id to an ObjectId
    task = mongo.db.todo_tasks.find_one({'_id': ObjectId(task_id)})
    if not task:
        abort(404, 'Task not found')

    if request.method == 'GET':
        task['_id'] = str(task['_id'])
        return jsonify(task)

    elif request.method == 'PUT':
        data = request.get_json()
        updated_task = {
            'title': data.get('title', task['title']),
            'description': data.get('description', task['description']),
            'completed': data.get('completed', task['completed'])
        }

        mongo.db.todo_tasks.update_one({'_id': ObjectId(task_id)}, {'$set': updated_task})
        updated_task['_id'] = task_id

        return jsonify(updated_task)

    elif request.method == 'DELETE':
        mongo.db.todo_tasks.delete_one({'_id': ObjectId(task_id)})
        return jsonify({'message': 'Task deleted'}), 200

# 4. Delete all To-Do Tasks
@todo_bp.route('/all', methods=['DELETE'])
def delete_all_tasks():
    mongo.db.todo_tasks.delete_many({})
    return jsonify({'message': 'All tasks deleted'}), 200
