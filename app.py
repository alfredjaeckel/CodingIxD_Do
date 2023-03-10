# Installed
import contr
from contr import cat_move, butterfly_move, init_GPIO

from forms import AddItemForm, AddStepForm, EditItemForm
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_path='/Users/alfred/PycharmProjects/CodingIxD_Do/instance')
app.config['SECRET_KEY'] = 'SECRET_PROJECT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toDoListDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # to supress warning

db = SQLAlchemy(app)

# one hour more required running linux on raspi
TIMESPAN = timedelta(days=7, hours=1, minutes=0, seconds=0)


# define the models for the database
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=False)
    complete = db.Column(db.Boolean, default=False, nullable=False)
    committed = db.Column(db.Boolean, default=False, nullable=False)
    committed_id = db.Column(db.Integer)
    steps = db.relationship('Step', backref='item', lazy='dynamic', cascade="all, delete, delete-orphan")
    due_time = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return "Item ID: {}, Name: {}, Committed: {}, Complete: {}, Commit_id: {}" \
            .format(self.id, self.name, self.committed, self.complete, self.committed_id)


class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=False)
    number = db.Column(db.Integer, unique=False)  # Steps placement
    complete = db.Column(db.Boolean, default=False, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __repr__(self):
        return "Item ID: {}, Step ID: {}, Name: {}, Number: {}, Complete: {}" \
            .format(self.item_id, self.id, self.name, self.number, self.complete)


# initialise database
with app.app_context():
    db.create_all()

'''
    Functions to handle button inputs on main page
'''


def commit(committed_items, name):
    if committed_items.count() < 3:
        item = db.session.get(Item, name)
        committed_id = db.session.query(Item.committed_id).filter(Item.committed == True)
        committed_id = [n[0] for n in committed_id]
        if 0 not in committed_id:
            item.committed_id = 0
            cat_move(True, 0)
        elif 1 not in committed_id:
            item.committed_id = 1
            cat_move(True, 0)
        elif 2 not in committed_id:
            item.committed_id = 2
            cat_move(True, 0)
        else:
            print("committed_id failure")
        item.complete = False
        item.committed = True
        item.due_time = datetime.now() + TIMESPAN
        db.session.commit()
    else:
        print("To Many commitments")


def complete(name):
    butterfly_move()
    item = db.session.get(Item, name)
    if (db.session.query(Step.item_id).filter(Step.item_id == item.id, Step.complete == False).count()) > 0:
        step = db.session.query(Step).filter(Step.item_id == item.id, Step.complete == False) \
            .order_by(Step.number).first()
        step.complete = True
        db.session.commit()
        return redirect(url_for("prompt_finish", item_id=name))
    else:
        item.committed_id = None
        item.complete = True
        item.committed = False
        db.session.commit()
        return redirect(url_for("todo"))


def uncomplete(name):
    item = db.session.get(Item, name)
    item.complete = False
    item.committed = False
    db.session.commit()


def procede(name):
    item = db.session.get(Item, name)
    item.due_time = datetime.now() + TIMESPAN
    db.session.commit()
    return redirect(url_for("todo"))


def extend(name):
    item = db.session.get(Item, name)
    item.due_time = datetime.now() + TIMESPAN
    db.session.commit()
    return redirect(url_for("prompt_fail", item_id=name))


def get_steps(committed_items):
    step_list = [None, None, None]
    for item in committed_items:
        if (db.session.query(Step.item_id).filter(Step.item_id == item.id, Step.complete == False).count()) > 0:
            step_list[item.committed_id] = db.session.query(Step.name).filter(Step.item_id == item.id,
                                                                              Step.complete == False) \
                .order_by(Step.number).first()
    return step_list


'''
    Functions for adding steps
'''


def add_step(item_id):
    add_step_form = AddStepForm()
    if add_step_form.validate_on_submit():
        item = db.session.get(Item, item_id)
        if (db.session.query(Step).filter(Step.item_id == item.id, Step.complete == False).count()) > 0:
            undone_step = db.session.query(Step).filter(Step.item_id == item.id, Step.complete == False).order_by(
                Step.number).first()
            steps_count = undone_step.number
            for step in db.session.query(Step).filter(Step.item_id == item.id, Step.number >= undone_step.number):
                step.number = step.number + 1
        else:
            steps_count = len(item.steps.all()) + 1

        step = Step(name=add_step_form.name.data, number=steps_count, item_id=item_id)
        db.session.add(step)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()


'''
    Routes for Websites
'''


@app.route('/', methods=["GET", "POST"])  # start page
def todo():
    committed_items = db.session.query(Item).filter(Item.committed)
    todo_items = db.session.query(Item).filter(Item.committed == False, Item.complete == False)
    completed_items = db.session.query(Item).filter(Item.complete)
    step_list = get_steps(committed_items)

    if request.method == "POST":
        [(name, action)] = request.form.items()
        # Item table actions
        if action == "Commit":
            commit(committed_items, name)
        if action == "Complete":
            return complete(name)
        elif action == "Uncomplete":
            uncomplete(name)
        elif action == "Edit":
            return redirect(url_for("item", item_id=name))

    return render_template("lists.html",
                           committed_items=committed_items,
                           todo_items=todo_items,
                           completed_items=completed_items,
                           step_list=step_list,
                           add_item=AddItemForm(),
                           )


@app.route('/prompt/<item_id>', methods=["GET", "POST"])  # prompt after a week
def prompt(item_id):
    prompt_item = db.session.get(Item, item_id)
    committed_items = db.session.query(Item).filter(Item.committed)
    todo_items = db.session.query(Item).filter(Item.committed == False, Item.complete == False)
    completed_items = db.session.query(Item).filter(Item.complete)
    step_list = get_steps(committed_items)

    if request.method == "POST":

        [(name, action)] = request.form.items()

        # Item table actions
        if action == "Commit":
            commit(committed_items, name)
        if action == "Complete":
            return complete(name)
        elif action == "Uncomplete":
            uncomplete(name)
        elif action == "Edit":
            return redirect(url_for("item", item_id=name))
        elif action == "Finish":
            return complete(name)
        elif action == "Extend":
            return extend(name)

    return render_template("prompt.html",
                           item=prompt_item,
                           committed_items=committed_items,
                           todo_items=todo_items,
                           completed_items=completed_items,
                           step_list=step_list,
                           add_item=AddItemForm(),
                           )


@app.route('/prompt_fail/<item_id>', methods=["GET", "POST"])  # prompt on choosing extend in first prompt
def prompt_fail(item_id):
    prompt_item = db.session.get(Item, item_id)
    committed_items = db.session.query(Item).filter(Item.committed)
    todo_items = db.session.query(Item).filter(Item.committed == False, Item.complete == False)
    completed_items = db.session.query(Item).filter(Item.complete)
    step_list = get_steps(committed_items)

    if request.method == "POST":
        [(name, action)] = request.form.items()
        # Item table actions
        if action == "Commit":
            commit(committed_items, name)
        if action == "Complete":
            return complete(name)
        elif action == "Uncomplete":
            uncomplete(name)
        elif action == "Edit":
            return redirect(url_for("item", item_id=name))

    return render_template("prompt_fail.html",
                           item=prompt_item,
                           add_step=AddStepForm(),
                           committed_items=committed_items,
                           todo_items=todo_items,
                           completed_items=completed_items,
                           step_list=step_list,
                           add_item=AddItemForm(),
                           )


@app.route('/prompt_finish/<item_id>', methods=["GET", "POST"])  # prompt to add further step or continue project
def prompt_finish(item_id):
    prompt_item = db.session.get(Item, item_id)
    committed_items = db.session.query(Item).filter(Item.committed)
    todo_items = db.session.query(Item).filter(Item.committed == False, Item.complete == False)
    completed_items = db.session.query(Item).filter(Item.complete)
    step_list = get_steps(committed_items)

    if request.method == "POST":
        [(name, action)] = request.form.items()
        # Item table actions
        if action == "Commit":
            commit(committed_items, name)
        if action == "Complete":
            return complete(name)
        elif action == "Uncomplete":
            uncomplete(name)
        elif action == "Edit":
            return redirect(url_for("item", item_id=name))
        elif action == "Continue":
            return procede(name)
        elif action == "Extend":
            return extend(name)

    return render_template("prompt_finish.html",
                           item=prompt_item,
                           committed_items=committed_items,
                           todo_items=todo_items,
                           completed_items=completed_items,
                           step_list=step_list,
                           add_item=AddItemForm(),
                           )


@app.route("/item/<item_id>", methods=["GET", "POST"])  # edit page
def item(item_id):
    item = db.session.get(Item, item_id)

    if request.method == "POST":

        [(name, action)] = request.form.items()

        # Step Actions
        if action == "Complete":
            step = db.session.get(Step, name)
            step.complete = True
            db.session.commit()
        elif action == "Uncomplete":
            step = db.session.get(Step, name)
            step.complete = False
            db.session.commit()
        elif action == "Remove":
            step = db.session.get(Step, name)
            db.session.delete(step)
            db.session.commit()

        # Item Actions
        elif action == "Delete":
            item = db.session.get(Item, name)
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for("todo"))

        # Site Actions
        elif action == "Return":
            return redirect(url_for("todo"))

    return render_template("items.html",
                           item=item,
                           steps=Step.query.filter(Step.item_id == item.id).order_by(Step.number),
                           add_step=AddStepForm(),
                           edit_item=EditItemForm(name=item.name),
                           )


@app.route("/<item_id>/edit_item_submit", methods=["POST"])  # route for editing item name on edit page
def edit_item_submit(item_id):
    edit_item_form = EditItemForm()
    # Fix
    if edit_item_form.validate_on_submit():
        item = db.session.get(Item, item_id)
        item.name = edit_item_form.name.data
        db.session.commit()
    return redirect(url_for("item", item_id=item_id))


@app.route("/<item_id>/add_step_submit", methods=["POST"])  # route for adding step on edit page
def add_step_submit(item_id):
    add_step(item_id)
    return redirect(url_for("item", item_id=item_id))


@app.route("/<item_id>/add_step_submit_prompt", methods=["POST"])  # route for adding step in prompt
def add_step_submit_prompt(item_id):
    add_step(item_id)
    return redirect(url_for("todo"))


@app.route("/add_item_submit", methods=["POST"])  # route for adding item on main page
def add_item_submit():
    add_item_form = AddItemForm()
    if add_item_form.validate_on_submit():
        item = Item(name=add_item_form.name.data)
        db.session.add(item)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        return redirect(url_for("todo"))


'''
    Initialise webpage 
'''

if __name__ == '__main__':
    try:
        init_GPIO()
        app.run(host='0.0.0.0')
    finally:
        print("Website shutdown")
