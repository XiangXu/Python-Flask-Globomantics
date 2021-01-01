from utils.db_util import DBUtily
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DecimalField, FileField, HiddenField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError
from wtforms.widgets import Input
from markupsafe import Markup
from app import app

class PriceInput(Input):
    input_type = "number"
  
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        kwargs.setdefault("step", "0.01")
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        return Markup("""<div class="input-group mb-3">
                    <div class="input-group-prepend">
                        <span class="input-group-text">$</span>
                    </div>
                    <input %s>
                </div>""" % self.html_params(name=field.name, **kwargs))

class PriceField(DecimalField):
    widget = PriceInput()

class ItemForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired("Input is required"), 
                                            DataRequired("Data is required"),
                                            Length(min=1, max=20, message="Input must be between 5 and 20 characters long")])
    price = PriceField("Price")
    description = TextAreaField("Description")
    image = FileField("Image", validators=[FileAllowed(app.config["ALLOWED_IMAGE_EXTENSIONS"], "Images only")])

class NewItemForm(ItemForm):
    category = SelectField("Category", coerce=int)
    subcategory = SelectField("Subcategory", coerce=int)
    submit = SubmitField("Submit")

    def validate_subcategory(form, field):
        exists = DBUtily.validate_subcategor(field.data, form.category.data)
        if not exists:
            raise ValidationError("Choice does not belong to that")

class EditItemForm(ItemForm):
    submit = SubmitField("Update item")

class DeleteItemForm(FlaskForm):
    submit = SubmitField("Delete item")

class FilterForm(FlaskForm):
    title = StringField("Title", validators=[Length(max=20)])
    price = SelectField("Price", coerce=int, choices=[(0, "---"), (1, "Max to Min"), (2, "Min to Max")])
    category = SelectField("Category", coerce=int)
    subcategory = SelectField("Subcategory", coerce=int)
    submit = SubmitField("Filter")

class NewCommentForm(FlaskForm):
    content = TextAreaField("Comment", validators=[InputRequired("Input is required"), DataRequired("Data is required")])
    item_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Submit")

