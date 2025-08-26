from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models import Customer
from app.forms import CustomerForm

customer_bp = Blueprint("customers", __name__, template_folder="../templates/customer")

@customer_bp.route("/")
def list_customers():
    customers = Customer.query.all()
    return render_template("customer_list.html", customers=customers)

@customer_bp.route("/new", methods=["GET", "POST"])
def new_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            price_per_bundle=form.price_per_bundle.data,
            portions_per_bundle=form.portions_per_bundle.data,
        )
        db.session.add(customer)
        db.session.commit()
        flash("Customer berhasil ditambahkan!", "success")
        return redirect(url_for("customers.list_customers"))
    return render_template("customer_form.html", form=form)

@customer_bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        form.populate_obj(customer)
        db.session.commit()
        flash("Customer berhasil diperbarui!", "success")
        return redirect(url_for("customers.list_customers"))
    return render_template("customer_form.html", form=form)

@customer_bp.route("/<int:id>/delete", methods=["POST"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer berhasil dihapus!", "danger")
    return redirect(url_for("customers.list_customers"))
