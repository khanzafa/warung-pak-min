from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import Customer, db
from app.utils.helpers import get_customer_summary, calculate_cost_breakdown, get_customer_pricing_info

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/customer_summary/<int:customer_id>')
def api_customer_summary(customer_id):
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    summary = get_customer_summary(customer_id, start_date, end_date)
    if not summary:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify({
        'customer_name': summary['customer'].name,
        'total_portions': summary['total_portions'],
        'total_bundles': summary['total_bundles'],
        'charged_portions': summary['charged_portions'],
        'remaining_portions': summary['remaining_portions'],
        'catering_cost': summary['catering_cost'],
        'total_kasbon': summary['total_kasbon'],
        'total_payments': summary['total_payments'],
        'total_bill': summary['total_bill'],
        'remaining_balance': summary['remaining_balance'],
        'effective_price_per_portion': summary['price_per_portion'],
        'bundle_info': summary['bundle_info']
    })

@api_bp.route('/pricing_info/<int:customer_id>')
def api_pricing_info(customer_id):
    """Get customer pricing information"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    pricing_info = get_customer_pricing_info(customer)
    return jsonify(pricing_info)

@api_bp.route('/cost_breakdown/<int:customer_id>')
def api_cost_breakdown(customer_id):
    """Calculate cost breakdown for given portions"""
    portions = request.args.get('portions', type=int)
    if portions is None or portions < 0:
        return jsonify({'error': 'Valid portions parameter required'}), 400
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    breakdown = calculate_cost_breakdown(customer, portions)
    return jsonify(breakdown)