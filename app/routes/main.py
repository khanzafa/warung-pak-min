from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from sqlalchemy import extract, func

from app.utils.helpers import create_pdf_summary, get_customer_summary
from app.models import db, Customer, DailyOrder, Kasbon, Payment


main_bp = Blueprint('main', __name__)

# Routes
@login_required
@main_bp.route('/')
def index():
    # Data dasar
    customers = Customer.query.all()
    
    # Hitung statistik untuk dashboard
    total_customers = len(customers)
    
    # Pesanan hari ini
    today_orders = DailyOrder.query.filter(DailyOrder.date == date.today()).all()
    today_orders_count = len(today_orders)
    today_total_portions = sum(order.total_portions for order in today_orders)
    
    # Total kasbon yang belum dibayar
    total_kasbon = db.session.query(func.coalesce(func.sum(Kasbon.total_amount), 0)).scalar()
    
    # Pendapatan bulan ini
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        extract('month', Payment.date) == current_month,
        extract('year', Payment.date) == current_year
    ).scalar()
    
    # Pesanan terbaru (7 hari terakhir)
    seven_days_ago = date.today() - timedelta(days=7)
    recent_orders = DailyOrder.query.filter(
        DailyOrder.date >= seven_days_ago
    ).order_by(DailyOrder.date.desc()).limit(10).all()
    
    # Tambahkan nama customer ke pesanan terbaru
    recent_orders_with_names = []
    for order in recent_orders:
        customer = Customer.query.get(order.customer_id)
        recent_orders_with_names.append({
            'id': order.id,
            'date': order.date,
            'customer_id': order.customer_id,
            'customer_name': customer.name if customer else "Unknown",
            'morning_portions': order.morning_portions,
            'afternoon_portions': order.afternoon_portions,
            'evening_portions': order.evening_portions,
            'total_portions': order.total_portions,
            'paid': True  # Asumsi sederhana, bisa disesuaikan dengan logika bisnis
        })
    
    # 5 Kasbon terbaru
    recent_kasbons = Kasbon.query.order_by(Kasbon.date.desc()).limit(5).all()
    
    # 5 Pembayaran terbaru
    recent_payments = Payment.query.order_by(Payment.date.desc()).limit(5).all()
    
    return render_template('dashboard.html',
        customers=customers,
        total_customers=total_customers,
        today_orders_count=today_orders_count,
        today_total_portions=today_total_portions,
        total_kasbon=total_kasbon,
        monthly_revenue=monthly_revenue,
        recent_orders=recent_orders_with_names,
        recent_kasbons=recent_kasbons,
        recent_payments=recent_payments
    )

@login_required
@main_bp.route('/summary/<int:customer_id>')
def customer_summary(customer_id):
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    summary = get_customer_summary(customer_id, start_date, end_date)
    if not summary:
        flash('Customer tidak ditemukan!', 'error')
        return redirect(url_for('customers.list_customers'))
    
    return render_template('customer_summary.html', summary=summary, 
                         start_date=start_date, end_date=end_date)

@login_required
@main_bp.route('/summary/<int:customer_id>/pdf')
def customer_summary_pdf(customer_id):
    """Generate PDF summary for customer"""
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    summary = get_customer_summary(customer_id, start_date, end_date)
    if not summary:
        flash('Customer tidak ditemukan!', 'error')
        return redirect(url_for('customers.list_customers'))
    
    # Generate PDF
    pdf_buffer = create_pdf_summary(summary, start_date, end_date)
    
    # Create response
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=ringkasan_{summary["customer"].name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response

