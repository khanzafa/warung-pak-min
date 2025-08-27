from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.widgets import TextInput

from app.models import Customer


# ---- Payment ----
class PaymentForm(FlaskForm):
    date = DateField("Tanggal", validators=[DataRequired()])
    customer_id = SelectField("Pelanggan", coerce=int, validators=[DataRequired()])
    amount = IntegerField("Jumlah Bayar", validators=[NumberRange(min=1), DataRequired()], widget=TextInput())
    description = TextAreaField("Keterangan", validators=[Optional()])
    submit = SubmitField("Simpan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]
