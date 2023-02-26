from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FieldsRequiredForm(FlaskForm):
    class Meta:
        def render_field(self, field, render_kw):
            if field.type == "_Option":
                render_kw.setdefault("required", True)
            return super().render_field(field, render_kw)


'''
    Forms used by the templates
'''


class AddItemForm(FieldsRequiredForm):
    name = StringField("Item Name", render_kw={"placeholder": "Add Item"}, validators=[DataRequired()])
    submit = SubmitField("")


class AddStepForm(FieldsRequiredForm):
    name = StringField("Step Name", render_kw={"placeholder": "Add Step"}, validators=[DataRequired()])
    submit = SubmitField("")


class EditItemForm(FieldsRequiredForm):
    name = StringField("Item Name", validators=[DataRequired()])
    submit = SubmitField("")
