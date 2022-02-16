import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

DATABASE_URI = 'sqlite:///todolist.db'
app = Flask(__name__)  # __main__
app.config['SECRET_KEY'] = "secret1234"  # this key used to secret data coming from form
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)


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


@app.route('/', methods=['GET'])
def get():
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
def create():
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
def update_delete(id):
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
