from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

from app.models import Customer


# ---- Kasbon ----
class KasbonForm(FlaskForm):
    date = DateField("Tanggal", validators=[DataRequired()])
    customer_id = SelectField("Pelanggan", coerce=int, validators=[DataRequired()])
    item_name = StringField("Nama Item", validators=[DataRequired()])
    quantity = IntegerField("Jumlah", default=1, validators=[NumberRange(min=1)])
    unit_price = IntegerField("Harga Satuan", validators=[NumberRange(min=1)])    
    submit = SubmitField("Simpan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]

    def calculate_total(self):
        if self.quantity.data and self.unit_price.data:
            return self.quantity.data * self.unit_price.data
        return 0

