from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models import Kasbon
from app.forms import KasbonForm

kasbon_bp = Blueprint("kasbons", __name__, template_folder="../templates/kasbon")

@kasbon_bp.route("/")
def list_kasbons():
    kasbons = Kasbon.query.all()
    return render_template("kasbon_list.html", kasbons=kasbons)

@kasbon_bp.route("/new", methods=["GET", "POST"])
def new_kasbon():
    form = KasbonForm()
    if form.validate_on_submit():
        total_amount = form.calculate_total()
        kasbon = Kasbon(
            date = form.date.data,
            customer_id = form.customer_id.data,
            item_name = form.item_name.data,
            quantity = form.quantity.data,
            unit_price = form.unit_price.data,
            total_amount = total_amount
        )
        db.session.add(kasbon)
        db.session.commit()
        flash("Kasbon berhasil ditambahkan!", "success")
        return redirect(url_for("kasbons.list_kasbons"))    
    return render_template("kasbon_form.html", form=form)

@kasbon_bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_kasbon(id):
    kasbon = Kasbon.query.get_or_404(id)
    form = KasbonForm(obj=kasbon)
    if form.validate_on_submit():
        form.populate_obj(kasbon)
        db.session.commit()
        flash("Kasbon berhasil diperbarui!", "success")
        return redirect(url_for("kasbons.list_kasbons"))
    return render_template("kasbon_form.html", form=form)

@kasbon_bp.route("/<int:id>/delete", methods=["POST"])
def delete_kasbon(id):
    kasbon = Kasbon.query.get_or_404(id)
    db.session.delete(kasbon)
    db.session.commit()
    flash("Kasbon berhasil dihapus!", "danger")
    return redirect(url_for("kasbons.list_kasbons"))
