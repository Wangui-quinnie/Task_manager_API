from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import config
import jwt # for authentication
import datetime # handle time related tasks like token expiration
from flask_bcrypt import Bcrypt #securely hash and verify passwords
from functools import wraps #build decoratorse.g for protected routes

app = Flask(__name__)
app.config.from_object(config)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key!
bcrypt = Bcrypt(app) #initialize Bcrypt

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

# Delete task
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (id,))
    mysql.connection.commit()
    affected_rows = cur.rowcount
    cur.close()

    if affected_rows == 0:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({'message': 'Task deleted successfully'})

# Add the /register route
# Receives a username and password
# Validates them and hashes the password
# Inserts the user into a MySQL db
# Returns a clear response
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add the /login route
# Verifies the user's credentials
# Creates a secure JWT if they are valid
# Returns the token so the user can access protected resources
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.check_password_hash(user[2], password):  # user[2] is the hashed password
        token = jwt.encode({
            'user_id': user[0],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)
