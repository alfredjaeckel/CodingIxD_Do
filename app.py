# Installed
import contr
from contr import cat_move, init_GPIO, achievement_flag
from RPi import GPIO

from forms import AddItemForm, AddStepForm, EditItemForm
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy


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


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def todo():
    # cat_move(True, 0)

    committed_items = Item.query.filter(Item.committed == True)
    todo_items = Item.query.filter(Item.committed == False, Item.complete == False)
    completed_items = Item.query.filter(Item.complete == True)

    if request.method == "POST":

        [(name, action)] = request.form.items()

        # Item table actions
        if action == "Commit":
            if committed_items.count() < 3:
                item = Item.query.get(name)
                committed_id = db.session.query(Item.committed_id).filter(Item.committed == True)
                committed_id = [n[0] for n in committed_id]
                print(committed_id)
                if 0 not in committed_id:
                    item.committed_id = 0
                elif 1 not in committed_id:
                    item.committed_id = 1
                elif 2 not in committed_id:
                    item.committed_id = 2
                else:
                    print("committed_id failure")
                item.complete = False
                item.committed = True
                item.due_time = datetime.now() + timedelta(hours=2)
                db.session.commit()
                print(item.__repr__())
            else:
                print("To Many commitments")

        if action == "Complete":
            item = Item.query.get(name)
            item.committed_id = None
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


@app.route("/<committed_id>/check_achievement", methods=["GET","POST"])
def check_achievement(committed_id):
    committed_id = int(committed_id)
    item_id = db.session.query(Item.id).filter(Item.committed_id == committed_id).scalar()
    if not contr.achievement_flag[committed_id] and item_id is not None:
        abort(404)
    else:
        contr.achievement_flag[committed_id] = False
        return redirect(url_for("todo"))


@app.route("/<committed_id>/achievement", methods=["GET","POST"])
def achievement(committed_id):
    committed_id = int(committed_id)
    item_id = db.session.query(Item.id).filter(Item.committed_id == committed_id).scalar()

    item = Item.query.get(item_id)
    item.committed_id = None
    item.complete = True
    item.committed = False
    db.session.commit()

    return redirect(url_for("item", item_id=item_id))


@app.route("/<committed_id>/check_fail", methods=["GET","POST"])
def check_fail(committed_id):
    committed_id = int(committed_id)
    item_id = db.session.query(Item.id).filter(Item.committed_id == committed_id).scalar()
    if not contr.fail_flag[committed_id] and item_id is not None:
        abort(404)
    else:
        contr.fail_flag[committed_id] = False
        return redirect(url_for("todo"))


@app.route("/<committed_id>/fail", methods=["GET","POST"])
def fail(committed_id):
    committed_id = int(committed_id)
    item_id = db.session.query(Item.id).filter(Item.committed_id == committed_id).scalar()
    return redirect(url_for("item", item_id=item_id))


if __name__ == '__main__':
    try:
        init_GPIO()
        app.run(host='0.0.0.0')
    finally:
        GPIO.cleanup()
