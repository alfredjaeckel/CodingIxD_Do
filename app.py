# Installed
import multiprocessing
import sys, time

import RPi.GPIO as GPIO
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import contr
from forms import AddItemForm, AddStepForm, EditItemForm
from datetime import datetime, timedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_PROJECT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toDoListDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # to supress warning

db = SQLAlchemy(app)




class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=False)
    complete = db.Column(db.Boolean, default=False, nullable=False)
    committed = db.Column(db.Boolean, default=False, nullable=False)
    steps = db.relationship('Step', backref='item', lazy='dynamic', cascade="all, delete, delete-orphan")
    due_time = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return "Item ID: {}, Name: {}, Committed: {}, Complete: {}" \
            .format(self.id, self.name, self.committed, self.complete)


class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=False)
    number = db.Column(db.Integer, unique=False)  # Steps placement
    complete = db.Column(db.Boolean, default=False, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __repr__(self):
        return "Item ID: {}, Step ID: {}, Name: {}, Number: {}, Complete: {}" \
            .format(self.item_id, self.id, self.name, self.number, self.complete)


with app.app_context():
    db.create_all()


def phys():
    contr.move()

process = multiprocessing.Process(target=phys)


@app.route('/', methods=["GET", "POST"])
def todo():
    if not process.is_alive():
        process.start()

    committed_items = Item.query.filter(Item.committed == True)
    todo_items = Item.query.filter(Item.committed == False, Item.complete == False)
    completed_items = Item.query.filter(Item.complete == True)

    if request.method == "POST":

        [(name, action)] = request.form.items()

        # Item table actions
        if action == "Commit":
            item = Item.query.get(name)
            item.complete = False
            item.committed = True
            item.due_time = datetime.now() + timedelta(seconds=2)
            #todo do date
            db.session.commit()
        if action == "Complete":
            item = Item.query.get(name)
            item.complete = True
            item.committed = False
            db.session.commit()
        elif action == "Uncomplete":
            item = Item.query.get(name)
            item.complete = False
            item.committed = False
            db.session.commit()
        elif action == "Edit":
            return redirect(url_for("item", item_id=name))

    return render_template("lists.html",
                           committed_items=committed_items,
                           todo_items=todo_items,
                           completed_items=completed_items,
                           add_item=AddItemForm(),
                           )


@app.route("/item/<item_id>", methods=["GET", "POST"])
def item(item_id):
    item = Item.query.get(item_id)

    if request.method == "POST":

        [(name, action)] = request.form.items()

        # Step Actions
        if action == "Done":
            step = Step.query.get(name)
            step.complete = True
            db.session.commit()
        elif action == "Undo":
            step = Step.query.get(name)
            step.complete = False
            db.session.commit()
        elif action == "Remove":
            step = Step.query.get(name)
            db.session.delete(step)
            db.session.commit()

        # Item Actions
        elif action == "Delete":
            item = Item.query.get(name)
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


@app.route("/<item_id>/edit_item_submit", methods=["POST"])
def edit_item_submit(item_id):
    edit_item_form = EditItemForm()
    #Fix
    if edit_item_form.validate_on_submit():
        item = Item.query.get(item_id)
        item.name = edit_item_form.name.data
        db.session.commit()
    return redirect(url_for("item", item_id = item_id))


@app.route("/<item_id>/add_step_submit", methods=["POST"])
def add_step_submit(item_id):
    add_step_form = AddStepForm()
    if add_step_form.validate_on_submit():
        item = Item.query.get(item_id)
        steps_count = len(item.steps.all()) + 1
        step = Step(name = add_step_form.name.data, number = steps_count, item_id = item_id)
        db.session.add(step)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    return redirect(url_for("item", item_id=item_id))

@app.route("/add_item_submit", methods=["POST"])
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


GPIO.setmode(GPIO.BOARD)

achieve_btn = 40


@app.route('/achievement', methods=["GET", "POST"])
def achievement(ev=None):
    print("achievement")
    with app.app_context():
        return redirect(url_for("todo"))


GPIO.setup(achieve_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(achieve_btn, GPIO.FALLING, callback=achievement, bouncetime=20)
