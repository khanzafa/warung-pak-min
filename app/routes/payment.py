from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models import Payment, Customer
from app.forms import PaymentForm

payment_bp = Blueprint("payments", __name__, template_folder="../templates/payment")

@payment_bp.route("/")
def list_payments():
    payments = Payment.query.all()
    return render_template("payment_list.html", payments=payments)

@payment_bp.route("/new", methods=["GET", "POST"])
def new_payment():
    form = PaymentForm()
    if form.validate_on_submit():
        payment = Payment(
            date = form.date.data,
            customer_id = form.customer_id.data,
            amount = form.amount.data,
            description = form.description.data,
        )
        db.session.add(payment)
        db.session.commit()
        flash("Payment berhasil ditambahkan!", "success")
        return redirect(url_for("payments.list_payments"))
    customers = Customer.query.all()
    form.customer_id.choices = [(c.id, c.name) for c in customers]    
    return render_template("payment_form.html", form=form)

@payment_bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_payment(id):
    payment = Payment.query.get_or_404(id)
    form = PaymentForm(obj=payment)
    if form.validate_on_submit():
        form.populate_obj(payment)
        db.session.commit()
        flash("Payment berhasil diperbarui!", "success")
        return redirect(url_for("payments.list_payments"))
    return render_template("payment_form.html", form=form)

@payment_bp.route("/<int:id>/delete", methods=["POST"])
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    flash("Payment berhasil dihapus!", "danger")
    return redirect(url_for("payments.list_payments"))
