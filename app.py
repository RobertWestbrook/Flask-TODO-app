from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://roberts@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


db.create_all() # allows us to call on db.session  

@app.route('/todos/create', methods=['POST'])
def create_todo():
    # define variable with the request info  
    description = request.form.get('description', '')
    todo = Todo(description=description) #creates an instance of the Todo class and pass a value.
    db.session.add(todo) # Adds 'todo' item, which is INPUT, to pending. 
    db.session.commit() #commits the User input into db.
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())


if __name__ == '__main__':
    app.run(debug=True)