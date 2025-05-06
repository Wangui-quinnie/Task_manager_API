from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

mysql = MySQL(app)

@app.route('/')
def index():
    return "Task Manager API is running and connected to MySQL!"

from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'taskmanager'

mysql = MySQL(app)

@app.route('/')
def index():
    return "Task Manager API is running and connected to MySQL!"

# Create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Task created successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=True)
