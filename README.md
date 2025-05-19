Task Manager API

A secure, token-based RESTful API for managing personal tasks. Built with Flask, MySQL, JWT authentication, and bcrypt for secure password management.

Features

- User registration and login with JWT-based authentication
- Passwords hashed using Bcrypt
- Authenticated CRUD operations for tasks (Create, Read, Update, Delete)
- Token-protected routes
- MySQL backend integration
- Modular and extendable structure

Technologies Used

- Python 3.x
- Flask
- MySQL
- Flask-MySQLdb
- Flask-Bcrypt
- PyJWT
- datetime
- functools
- postman

Setup & Installation

1. Clone the repository

git clone https://github.com/yourusername/task-manager-api.git
cd task-manager-api

2. Install dependencies
Create a virtual environment and install required packages:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Configure your MySQL Connection - config.py
MYSQL_HOST = 'localhost'
MYSQL_USER = 'your_mysql_user'
MYSQL_PASSWORD = 'your_mysql_password'
MYSQL_DB = 'your_database_name'
Note: For security, consider using environment variables with python-dotenv.

4. Set a Secret Key
In your main app file:

app.config['SECRET_KEY'] = 'your_super_secret_key'

5. Database Schema - create your database and tables
CREATE DATABASE task_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

6. Run the application
python app.py
The server will run at: http://127.0.0.1:5000/


7. Authentication
All /tasks routes are protected and require a JWT token.
Include the token in the Authorization header:
Authorization: Bearer <your_token>

API Endpoints

| Method | Endpoint      | Description                |
|--------|---------------|----------------------------|
| POST   | `/register`   | Register new user          |
| POST   | `/login`      | Login and get JWT token    |

Tasks (Authenticated Routes)

| Method | Endpoint         | Description                    |
|--------|------------------|--------------------------------|
| GET    | `/tasks`         | Get all tasks for current user |
| GET    | `/tasks/<id>`    | Get a specific task            |
| POST   | `/tasks`         | Create a new task              |
| PUT    | `/tasks/<id>`    | Update a task by ID            |
| DELETE | `/tasks/<id>`    | Delete a task by ID            |

8. Testing with Postman
Register or log in to get a JWT token.

Set the token in Authorization → Bearer Token.

Use the above routes to manage tasks.

Sample JSON for POST/PUT
{
  "title": "Finish README documentation"
}

9. Security Practices
Passwords hashed using bcrypt

JWT tokens used for authentication

All task routes are protected using a token_required decorator

Users can only access their own tasks

10. Author
Winfred Ng'ang'a
https://github.com/Wangui-quinnie
http://www.linkedin.com/in/winfred-nganga