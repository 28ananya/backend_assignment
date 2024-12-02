import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/todo_db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
