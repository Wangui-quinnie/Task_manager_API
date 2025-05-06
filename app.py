from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend interaction
app.config.from_object(Config)

mysql = MySQL(app)

@app.route('/')
def index():
    return "Task Manager API is running!"

if __name__ == '__main__':
    app.run(debug=True)