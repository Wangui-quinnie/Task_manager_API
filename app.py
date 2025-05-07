from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import config

app = Flask(__name__)
app.config.from_object(config)

mysql = MySQL(app)

@app.route('/')
def index():
    return "Task Manager API is running and connected to MySQL!"

# Test database connection
@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        return "Database connection successful"
    except Exception as e:
        return f"Database connection failed: {e}"

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

# Fetch all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, completed FROM tasks")
    rows = cur.fetchall()
    cur.close()

    tasks = []
    for row in rows:
        task = {
            'id': row[0],
            'title': row[1],
            'completed': bool(row[2])
        }
        tasks.append(task)

    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True)
