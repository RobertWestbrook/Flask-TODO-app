import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://roberts@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    complete = db.Column(db.Boolean(), nullable=False, default= False)
    notes = db.Column(db.String(), nullable=True)
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable= False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = (db.Column(db.Integer, primary_key=True))
    name = (db.Column(db.String(), nullable=False))
    todos = db.relationship('Todo', backref='list', lazy=True)

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error=False
    body = {}
    try: # Try - Except - Finally statements are good practice to making testing and properly dealing 
         # with errors statements.
        description = request.get_json()['description']# define variable with the request info 
        todo = Todo(description=description, complete=False) #creates an instance of the Todo class and pass a value.
        db.session.add(todo) # Adds 'todo' item, which is INPUT, to pending. 
        db.session.commit() #commits the User input into db.
        body['description'] = todo.description
    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()  
    if error:
        abort (400)
    else:
        return jsonify(body) # need to call the instance of todo before except statement because 
                             # an error will cause commit to expire and throw an error whentrying
                             # to access after the statement. 

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.complete = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True })

@app.route('/lists/<todolist_id>')
def get_list_todos(todolist_id):
    return render_template('index.html', 
    lists=TodoList.query.all(),
    active_list=TodoList.query.get(todolist_id),
    todos=Todo.query.filter_by(todolist_id=todolist_id).order_by('id').all())

@app.route('/lists/create', methods=['POST']) 
def create_list():
    error= False
    body= {}
    try:
        name = request.get_json()['name']
        todolist = TodoList(name=name, complete=False)
        db.session.add(todolist)
        db.session.commit()
        body['name'] = todolist.name
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()  
    if error:
        abort (400)
    else:
        return jsonify(body)

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', todolist_id=1))

if __name__ == '__main__':
    app.run(debug=True)