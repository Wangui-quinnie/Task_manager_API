from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import config
import jwt # for authentication
import datetime # handle time related tasks like token expiration
from flask_bcrypt import Bcrypt # securely hash and verify passwords
from functools import wraps # build decorators e.g for protected routes

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

# Protect routes with a decorator which:
# Checks for a JWT in the request
# Validates and decodes it
# Extracts the user ID and Passes it to the protected route if everything is valid
def token_required(f): # decorator function
    @wraps(f)# helper from functools that preserves the original function's name and docstring when it's wrapped
    def decorated(*args, **kwargs): # adds logic (token checking)before calling the original route function f
        token = None

        if 'Authorization' in request.headers:# checks if the authorization header exists and extracts the token if it does
            token = request.headers['Authorization'].split(" ")[1]  # e.g., "Bearer <token>"

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256']) #decodes the token and extracts the user_id embedded in the token
            current_user_id = data['user_id']
        except:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        return f(current_user_id, *args, **kwargs) # calls the original route function (f)
    return decorated    


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
    cur.execute("SELECT * FROM users WHERE username = %s", (username,)) #The comma in (username,) ensures it's treated as a single-element tuple.
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


# Create a new task
@app.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user_id):
    data = request.get_json()

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tasks (title, user_id) VALUES (%s, %s)", (title,current_user_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Task created successfully!'}), 201

# Fetch all tasks for the current user
@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, completed FROM tasks WHERE user_id = %s", (current_user_id,))
    rows = cur.fetchall()
    cur.close()

    return jsonify([{'id': task[0], 'title': task[1]} for task in tasks])


# Fetch a specific task
@app.route('/tasks/<int:id>', methods=['GET'])
@token_required
def get_task(current_user_id, id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM tasks WHERE id = %s AND user_id = %s", (id, current_user_id))
    task = cur.fetchone()
    cur.close()

    if task:
        return jsonify({'id': task[0], 'title': task[1]})
    else:
        return jsonify({'error': 'Task not found'}), 404

# Update a task
@app.route('/tasks/<int:id>', methods=['PUT'])
@token_required
def update_task(current_user_id, id):
    data = request.get_json()
    new_title = data.get('title')

    if not new_title:
        return jsonify({'error': 'Title is required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET title = %s WHERE id = %s AND user_id = %s", (new_title, id, current_user_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Task updated successfully'})

# Delete task
@app.route('/tasks/<int:id>', methods=['DELETE'])
@token_required
def delete_task(current_user, id):
    cur = mysql.connection.cursor()
    # Ensure the task belongs to the logged-in user
    cur.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (id, current_user['id']))
    task = cur.fetchone()

    if not task:
        return jsonify({'message': 'Task not found or not authorized'}), 404

    cur.execute("DELETE FROM tasks WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Task deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
