import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token, get_jwt
)
from datetime import timedelta

DATABASE_URI = 'sqlite:///todolist.db'
app = Flask(__name__)  # __main__
app.config['SECRET_KEY'] = "secret1234"  # this key used to secret data coming from form
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] = "alaa123456"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)


# To Do List Model
class ToDoList(db.Model):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, unique=True, nullable=False)
    status = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # a special method used to represent a class's objects as a string.
    def __repr__(self):
        return f'User("{self.title}")'


# User Model
class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    # a special method used to represent a class's objects as a string.
    def __repr__(self):
        return f'User("{self.username}")'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "GET":
        return jsonify({
            "status": "Please Register"
        })
    elif request.method == "POST":
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        user = User(
            username=username,
            password=password,
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "data": f"{username} added successfully"
        }), 201


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return jsonify({
            'status': 'Please Login',
        })
    elif request.method == 'POST':
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).first()
        if user.password == password:
            access_token = create_access_token(identity=username)
            return jsonify({
                'status': 'success',
                'data': {
                    'access_token': access_token
                }})
        return jsonify({
            'status': 'Fail',
            'msg': "username or password is incorrect"
        })


@app.route('/', methods=['GET'])
@jwt_required()
def get():
    username = get_jwt_identity()
    todolists = ToDoList.query.all()
    result = []
    for todo in todolists:
        dict = {}
        dict['id'] = todo.id
        dict['title'] = todo.title
        dict['description'] = todo.description
        dict['status'] = todo.status
        dict['created_at'] = todo.created_at
        result.append(dict)
    return jsonify({
        "data": result
    })


@app.route('/create', methods=['POST'])
@jwt_required()
def create():
    username = get_jwt_identity()
    data = json.loads(request.data)
    todotitle = data['title']
    todotitledescription = data['description']
    todostatus = data['status']
    todo = ToDoList(
        title=todotitle,
        description=todotitledescription,
        status=todostatus,
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify({
        "data": f"{todotitle} added successfully"
    }), 201


@app.route('/todo/<int:id>', methods=['PUT', 'GET', 'DELETE'])
@jwt_required()
def update_delete(id):
    username = get_jwt_identity()
    todo = ToDoList.query.filter_by(id=id).first()
    if request.method == 'GET':
        dict = {}
        dict['id'] = todo.id
        dict['title'] = todo.title
        dict['description'] = todo.description
        dict['status'] = todo.status
        dict['created_at'] = todo.created_at
        return jsonify({
            "data": dict
        })
    if request.method == 'PUT':
        data = json.loads(request.data)
        todo.status = data['status']
        todo.description = data['description']

        db.session.commit()
        return jsonify({
            "data": "To Do List Updated successfully"
        })
    if request.method == 'DELETE':
        db.session.delete(todo)
        db.session.commit()
        return jsonify({
            "data": "To Do List Deleted successfully"
        })

db.create_all()
app.run(debug=True, port=5000)
