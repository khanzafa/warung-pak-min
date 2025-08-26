from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

from app.models import Customer


# ---- Daily Order ----
class DailyOrderForm(FlaskForm):
    date = DateField("Tanggal", validators=[DataRequired()])
    customer_id = SelectField("Pelanggan", coerce=int, validators=[DataRequired()])
    morning_portions = IntegerField("Pagi", default=0, validators=[NumberRange(min=0)])
    afternoon_portions = IntegerField("Siang", default=0, validators=[NumberRange(min=0)])
    evening_portions = IntegerField("Sore", default=0, validators=[NumberRange(min=0)])
    submit = SubmitField("Simpan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]

    def calculate_total(self):
        return (
            (self.morning_portions.data or 0) +
            (self.afternoon_portions.data or 0) +
            (self.evening_portions.data or 0)
        )
