from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models import DailyOrder, Customer
from app.forms import DailyOrderForm

order_bp = Blueprint("orders", __name__, template_folder="../templates/order")

@order_bp.route("/")
def list_orders():
    orders = DailyOrder.query.all()
    return render_template("order_list.html", orders=orders)

@order_bp.route("/new", methods=["GET", "POST"])
def new_order():
    form = DailyOrderForm()
    if form.validate_on_submit():
        total_portions = form.calculate_total()
        order = DailyOrder(
            date = form.date.data,
            customer_id = form.customer_id.data,
            morning_portions = form.morning_portions.data,
            afternoon_portions = form.afternoon_portions.data,
            evening_portions = form.evening_portions.data,
            total_portions = total_portions
        )
        db.session.add(order)
        db.session.commit()
        flash("DailyOrder berhasil ditambahkan!", "success")
        return redirect(url_for("orders.list_orders"))
    customers = Customer.query.all()
    form.customer_id.choices = [(c.id, c.name) for c in customers]    
    return render_template("order_form.html", form=form)

@order_bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_order(id):
    order = DailyOrder.query.get_or_404(id)
    form = DailyOrderForm(obj=order)
    if form.validate_on_submit():
        form.populate_obj(order)
        db.session.commit()
        flash("DailyOrder berhasil diperbarui!", "success")
        return redirect(url_for("orders.list_orders"))
    return render_template("order_form.html", form=form)

@order_bp.route("/<int:id>/delete", methods=["POST"])
def delete_order(id):
    order = DailyOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash("DailyOrder berhasil dihapus!", "danger")
    return redirect(url_for("orders.list_orders"))
