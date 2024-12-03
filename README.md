## Running the backend server
1. Install all the requriements
  pip install -r requriements.txt
2. run the surver
    python run.py
3. It will run one the surver http://127.0.0.1:5000
   ## API CALLS 
5. URL: http://localhost:5000/api/todos (get api, which will display all the tasks0
6. http://localhost:5000/api/todos (post api which will enter task,title)
     Body (raw JSON):
{
    "title": "New Task",
    "description": "This is a new task.",
    "completed": false
}

http://localhost:5000/api/todos/<task_id> (update api)
http://localhost:5000/api/todos/<task_id> (detete api)
