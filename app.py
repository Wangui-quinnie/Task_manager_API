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

# Fetch a specific task
@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM tasks WHERE id = %s", (id,))
    task = cur.fetchone()
    cur.close()

    if task:
        return jsonify({'id': task[0], 'title': task[1]})
    else:
        return jsonify({'error': 'Task not found'}), 404

# Update a task
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    new_title = data.get('title')

    if not new_title:
        return jsonify({'error': 'Title is required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET title = %s WHERE id = %s", (new_title, id))
    mysql.connection.commit()
    affected_rows = cur.rowcount
    cur.close()

    if affected_rows == 0:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({'message': 'Task updated successfully'})


if __name__ == '__main__':
    app.run(debug=True)
