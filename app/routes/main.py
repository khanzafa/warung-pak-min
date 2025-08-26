from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from sqlalchemy import extract, func

from app.utils.helpers import create_pdf_summary, get_customer_summary
from app.models import db, Customer, DailyOrder, Kasbon, Payment
from app.schemas import (
    CustomerCreate, CustomerResponse, CustomerUpdate,
    DailyOrderCreate, DailyOrderResponse, DailyOrderUpdate,
    KasbonCreate, KasbonResponse, KasbonUpdate,
    PaymentCreate, PaymentResponse, PaymentUpdate    
)

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

# @login_required
# @main_bp.route('/customers')
# def customers():
#     customers = Customer.query.order_by(Customer.name).all()
#     return render_template('customers.html', customers=customers)

# @login_required
# @main_bp.route('/customers/add', methods=['GET', 'POST'])
# def add_customer():
#     if request.method == 'POST':
#         try:
#             # Validasi dengan Pydantic schema
#             customer_data = CustomerCreate(
#                 name=request.form['name'],
#                 price_per_bundle=int(request.form['price_per_bundle']),
#                 portions_per_bundle=int(request.form['portions_per_bundle'])
#             )
            
#             # Buat customer baru
#             customer = Customer(
#                 name=customer_data.name,
#                 price_per_bundle=customer_data.price_per_bundle,
#                 portions_per_bundle=customer_data.portions_per_bundle
#             )
            
#             db.session.add(customer)
#             db.session.commit()
#             flash('Customer berhasil ditambahkan!', 'success')
#             return redirect(url_for('main.customers'))
            
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error: {str(e)}', 'danger')
    
#     return render_template('add_customer.html')

# @login_required
# @main_bp.route('/orders')
# def orders():
#     orders = DailyOrder.query.join(Customer).order_by(DailyOrder.date.desc()).all()
    
#     orders_with_names = []
#     for order in orders:
#         order_dict = {
#             'id': order.id,
#             'date': order.date,
#             'customer_id': order.customer_id,
#             'morning_portions': order.morning_portions,
#             'afternoon_portions': order.afternoon_portions,
#             'evening_portions': order.evening_portions,
#             'total_portions': order.total_portions,
#             'created_at': order.created_at,
#             'customer_name': order.customer.name if order.customer else "Unknown"
#         }
#         orders_with_names.append(order_dict)
    
#     return render_template('orders.html', orders=orders_with_names)

# @login_required
# @main_bp.route('/orders/add', methods=['GET', 'POST'])
# def add_order():
#     if request.method == 'POST':
#         try:
#             # Validasi dengan Pydantic schema
#             order_data = DailyOrderCreate(
#                 date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
#                 customer_id=int(request.form['customer_id']),
#                 morning_portions=int(request.form.get('morning_portions', 0)),
#                 afternoon_portions=int(request.form.get('afternoon_portions', 0)),
#                 evening_portions=int(request.form.get('evening_portions', 0)),
#                 total_portions=0  # Akan dihitung otomatis oleh validator
#             )
            
#             # Buat order baru
#             order = DailyOrder(
#                 date=order_data.date,
#                 customer_id=order_data.customer_id,
#                 morning_portions=order_data.morning_portions,
#                 afternoon_portions=order_data.afternoon_portions,
#                 evening_portions=order_data.evening_portions,
#                 total_portions=order_data.total_portions
#             )
            
#             db.session.add(order)
#             db.session.commit()
#             flash('Pesanan berhasil ditambahkan!', 'success')
#             return redirect(url_for('main.orders'))
            
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error: {str(e)}', 'danger')
    
#     customers = Customer.query.order_by(Customer.name).all()
#     return render_template('add_order.html', customers=customers)

# @login_required
# @main_bp.route('/kasbon')
# def kasbon():
#     kasbons = Kasbon.query.join(Customer).order_by(Kasbon.date.desc()).all()

#     kasbons_with_names = []
#     for kasbon in kasbons:
#         kasbon_dict = {
#             'id': kasbon.id,
#             'date': kasbon.date,
#             'customer_id': kasbon.customer_id,
#             'item_name': kasbon.item_name,
#             'quantity': kasbon.quantity,
#             'unit_price': kasbon.unit_price,
#             'total_amount': kasbon.total_amount,
#             'created_at': kasbon.created_at,
#             'customer_name': kasbon.customer.name if kasbon.customer else "Unknown"
#         }
#         kasbons_with_names.append(kasbon_dict)
    
#     return render_template('kasbon.html', kasbons=kasbons_with_names)

# @login_required
# @main_bp.route('/kasbon/add', methods=['GET', 'POST'])
# def add_kasbon():
#     if request.method == 'POST':
#         try:
#             # Validasi dengan Pydantic schema
#             kasbon_data = KasbonCreate(
#                 date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
#                 customer_id=int(request.form['customer_id']),
#                 item_name=request.form['item_name'],
#                 quantity=int(request.form['quantity']),
#                 unit_price=int(request.form['unit_price']),
#                 total_amount=0  # Akan dihitung otomatis oleh validator
#             )
            
#             # Buat kasbon baru
#             kasbon = Kasbon(
#                 date=kasbon_data.date,
#                 customer_id=kasbon_data.customer_id,
#                 item_name=kasbon_data.item_name,
#                 quantity=kasbon_data.quantity,
#                 unit_price=kasbon_data.unit_price,
#                 total_amount=kasbon_data.total_amount
#             )
            
#             db.session.add(kasbon)
#             db.session.commit()
#             flash('Kasbon berhasil ditambahkan!', 'success')
#             return redirect(url_for('main.kasbon'))
            
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error: {str(e)}', 'danger')

#     customers = Customer.query.order_by(Customer.name).all()
#     return render_template('add_kasbon.html', customers=customers)

# @login_required
# @main_bp.route('/payments')
# def payments():
#     payments = Payment.query.join(Customer).order_by(Payment.date.desc()).all()
    
#     payments_with_names = []
#     for payment in payments:
#         payment_dict = {
#             'id': payment.id,
#             'date': payment.date,
#             'customer_id': payment.customer_id,
#             'amount': payment.amount,
#             'description': payment.description,
#             'created_at': payment.created_at,
#             'customer_name': payment.customer.name if payment.customer else "Unknown"
#         }
#         payments_with_names.append(payment_dict)
    
#     return render_template('payments.html', payments=payments_with_names)

# @login_required
# @main_bp.route('/payments/add', methods=['GET', 'POST'])
# def add_payment():
#     if request.method == 'POST':
#         try:
#             # Validasi dengan Pydantic schema
#             payment_data = PaymentCreate(
#                 date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
#                 customer_id=int(request.form['customer_id']),
#                 amount=int(request.form['amount']),
#                 description=request.form.get('description', '')
#             )
            
#             # Buat payment baru
#             payment = Payment(
#                 date=payment_data.date,
#                 customer_id=payment_data.customer_id,
#                 amount=payment_data.amount,
#                 description=payment_data.description
#             )
            
#             db.session.add(payment)
#             db.session.commit()
#             flash('Pembayaran berhasil ditambahkan!', 'success')
#             return redirect(url_for('main.payments'))
            
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error: {str(e)}', 'danger')
    
#     customers = Customer.query.order_by(Customer.name).all()
#     return render_template('add_payment.html', customers=customers)

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

