from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.widgets import TextInput

# ---- Customer ----
class CustomerForm(FlaskForm):
    name = StringField("Nama", validators=[DataRequired()])
    price_per_bundle = IntegerField("Harga per bundle", default=8500, validators=[NumberRange(min=1)], widget=TextInput())
    portions_per_bundle = IntegerField("Porsi per bundle", default=1, validators=[NumberRange(min=1)])
    submit = SubmitField("Simpan")