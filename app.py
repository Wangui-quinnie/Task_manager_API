from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

mysql = MySQL(app)

@app.route('/')
def index():
    return "Task Manager API is running and connected to MySQL!"

if __name__ == '__main__':
    app.run(debug=True)