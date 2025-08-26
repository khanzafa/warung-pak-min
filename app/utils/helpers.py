from datetime import date, datetime
import io
from typing import Any, Dict, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from app.models import db, Customer, DailyOrder, Kasbon, Payment


def calculate_catering_cost(customer: Customer, total_portions: int) -> tuple:
    """
    Calculate catering cost based on customer's bundle configuration
    
    Returns:
        tuple: (total_bundles, charged_portions, catering_cost)
    """
    if customer.portions_per_bundle <= 0:
        return 0, 0, 0
    
    # Hitung berapa bundle yang harus dibayar
    total_bundles = total_portions // customer.portions_per_bundle
    if total_portions % customer.portions_per_bundle != 0:
        total_bundles += 1
    
    charged_portions = total_bundles * customer.portions_per_bundle
    catering_cost = total_bundles * customer.price_per_bundle
    
    return total_bundles, charged_portions, catering_cost


def get_customer_summary(customer_id: int, start_date: date = None, end_date: date = None) -> Optional[Dict[str, Any]]:
    """Get customer summary including orders, kasbon, and payments"""
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return None
    
    # Build queries dengan filter tanggal
    order_query = DailyOrder.query.filter_by(customer_id=customer_id)
    kasbon_query = Kasbon.query.filter_by(customer_id=customer_id)
    payment_query = Payment.query.filter_by(customer_id=customer_id)
    
    if start_date:
        order_query = order_query.filter(DailyOrder.date >= start_date)
        kasbon_query = kasbon_query.filter(Kasbon.date >= start_date)
        payment_query = payment_query.filter(Payment.date >= start_date)
    
    if end_date:
        order_query = order_query.filter(DailyOrder.date <= end_date)
        kasbon_query = kasbon_query.filter(Kasbon.date <= end_date)
        payment_query = payment_query.filter(Payment.date <= end_date)
    
    # Eksekusi queries
    orders = order_query.all()
    kasbons = kasbon_query.all()
    payments = payment_query.all()
    
    # Hitung totals
    total_portions = sum(order.total_portions for order in orders)
    
    # Calculate catering cost
    total_bundles, charged_portions, catering_cost = calculate_catering_cost(customer, total_portions)
    
    # Calculate actual remaining/extra portions
    remaining_portions = charged_portions - total_portions if charged_portions > total_portions else 0
    
    total_kasbon = sum(kasbon.total_amount for kasbon in kasbons)
    total_payments = sum(payment.amount for payment in payments)
    
    total_bill = catering_cost + total_kasbon
    remaining_balance = total_bill - total_payments
    
    # Hitung price per portion
    price_per_portion = customer.price_per_bundle / customer.portions_per_bundle if customer.portions_per_bundle > 0 else 0
    
    return {
        'customer': customer,
        'orders': orders,
        'total_portions': total_portions,
        'total_bundles': total_bundles,
        'charged_portions': charged_portions,
        'remaining_portions': remaining_portions,
        'catering_cost': catering_cost,
        'kasbons': kasbons,
        'total_kasbon': total_kasbon,
        'payments': payments,
        'total_payments': total_payments,
        'total_bill': total_bill,
        'remaining_balance': remaining_balance,
        'price_per_portion': round(price_per_portion, 2),
        'bundle_info': {
            'portions_per_bundle': customer.portions_per_bundle,
            'price_per_bundle': customer.price_per_bundle
        }
    }


def get_customer_pricing_info(customer: Customer) -> dict:
    """Get customer pricing information in a readable format"""
    price_per_portion = customer.price_per_bundle / customer.portions_per_bundle
    
    return {
        'price_per_bundle': customer.price_per_bundle,
        'portions_per_bundle': customer.portions_per_bundle,
        'effective_price_per_portion': price_per_portion,
        'pricing_description': f"Rp {customer.price_per_bundle:,} per {customer.portions_per_bundle} porsi (Rp {price_per_portion:,.0f}/porsi)"
    }


def calculate_cost_breakdown(customer: Customer, total_portions: int) -> dict:
    """Get detailed cost breakdown for a customer"""
    if total_portions == 0:
        return {
            'total_portions': 0,
            'total_bundles': 0,
            'charged_portions': 0,
            'remaining_portions': 0,
            'total_cost': 0,
            'cost_per_portion': 0,
            'breakdown': []
        }
    
    total_bundles, charged_portions, total_cost = calculate_catering_cost(customer, total_portions)
    remaining_portions = charged_portions - total_portions
    cost_per_portion = customer.price_per_bundle / customer.portions_per_bundle
    
    return {
        'total_portions': total_portions,
        'total_bundles': total_bundles,
        'charged_portions': charged_portions,
        'remaining_portions': remaining_portions,
        'total_cost': total_cost,
        'effective_cost_per_portion': cost_per_portion,
        'breakdown': {
            'bundles_ordered': total_bundles,
            'price_per_bundle': customer.price_per_bundle,
            'portions_per_bundle': customer.portions_per_bundle,
            'total_bundle_cost': total_cost
        }
    }

def format_currency(amount):
    """Format currency to Indonesian Rupiah"""
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        amount = 0
    return f"Rp {amount:,}".replace(",", ".")

def create_pdf_summary(summary, start_date=None, end_date=None):
    """Create professional PDF summary report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2E3440')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#3B4252')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Title
    title = Paragraph("RINGKASAN TAGIHAN CATERING", title_style)
    elements.append(title)
    
    # Date range
    if start_date and end_date:
        date_range = f"Periode: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
    else:
        date_range = "Periode: Keseluruhan Data"
    
    date_para = Paragraph(date_range, normal_style)
    elements.append(date_para)
    elements.append(Spacer(1, 20))
    
    # Customer Information
    customer = summary['customer']
    pricing_info = get_customer_pricing_info(customer)
    
    customer_info = [
        ['Informasi Customer', ''],
        ['Nama Customer:', customer.name],
        ['Harga per Bundle:', format_currency(customer.price_per_bundle)],
        ['Porsi per Bundle:', f"{customer.portions_per_bundle} porsi"],
        ['Harga Efektif per Porsi:', format_currency(int(pricing_info['effective_price_per_portion']))],
        ['', '']
    ]
    
    customer_table = Table(customer_info, colWidths=[3*inch, 3*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5E81AC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(customer_table)
    elements.append(Spacer(1, 20))
    
    # Order Summary
    order_summary = [
        ['Ringkasan Pesanan', ''],
        ['Total Porsi Dipesan:', f"{summary['total_portions']} porsi"],
        ['Total Bundle Ditagih:', f"{summary['total_bundles']} bundle"],
        ['Total Porsi Ditagih:', f"{summary['charged_portions']} porsi"],
        ['Porsi Bonus/Sisa:', f"{summary['remaining_portions']} porsi"],
        ['Biaya Catering:', format_currency(summary['catering_cost'])],
        ['', '']
    ]
    
    order_table = Table(order_summary, colWidths=[3*inch, 3*inch])
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#81A1C1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECEFF4')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(order_table)
    elements.append(Spacer(1, 20))
    
    # Financial Summary
    financial_data = [
        ['Ringkasan Keuangan', ''],
        ['Biaya Catering:', format_currency(summary['catering_cost'])],
        ['Total Kasbon:', format_currency(summary['total_kasbon'])],
        ['Total Tagihan:', format_currency(summary['total_bill'])],
        ['Total Pembayaran:', format_currency(summary['total_payments'])],
        ['Sisa Saldo:', format_currency(summary['remaining_balance'])],
    ]
    
    financial_table = Table(financial_data, colWidths=[3*inch, 3*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#BF616A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#ECEFF4')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    # Highlight remaining balance
    if summary['remaining_balance'] > 0:
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EBCB8B')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
        ]))
    elif summary['remaining_balance'] < 0:
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#A3BE8C')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
        ]))
    
    elements.append(financial_table)
    elements.append(Spacer(1, 30))

    hari_dict = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    
    # Detail Tables
    if summary['orders']:
        elements.append(Paragraph("Detail Pesanan", heading_style))
        
        order_details = [['Hari', 'Tanggal', 'Pagi', 'Siang', 'Sore', 'Total']]
        for order in summary['orders']:
            hari = order.date.strftime('%A')
            hari = hari_dict.get(hari, hari)
            order_details.append([
                hari,
                order.date.strftime('%d/%m/%Y'),
                str(order.morning_portions),
                str(order.afternoon_portions),
                str(order.evening_portions),
                str(order.total_portions)
            ])
        
        detail_table = Table(order_details, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(detail_table)
        elements.append(Spacer(1, 20))
    
    if summary['kasbons']:
        elements.append(Paragraph("Detail Kasbon", heading_style))
        
        kasbon_details = [['Hari', 'Tanggal', 'Item', 'Qty', 'Harga Satuan', 'Total']]
        for kasbon in summary['kasbons']:
            hari = kasbon.date.strftime('%A')
            hari = hari_dict.get(hari, hari)
            kasbon_details.append([
                hari,
                kasbon.date.strftime('%d/%m/%Y'),
                kasbon.item_name,
                str(kasbon.quantity),
                format_currency(kasbon.unit_price),
                format_currency(kasbon.total_amount)
            ])
        
        kasbon_table = Table(kasbon_details, colWidths=[1.2*inch, 1*inch, 1.7*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        kasbon_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(kasbon_table)
        elements.append(Spacer(1, 20))
    
    if summary['payments']:
        elements.append(Paragraph("Detail Pembayaran", heading_style))
        
        payment_details = [['Tanggal', 'Jumlah', 'Keterangan']]
        for payment in summary['payments']:
            payment_details.append([
                payment.date.strftime('%d/%m/%Y'),
                format_currency(payment.amount),
                payment.description or '-'
            ])
        
        payment_table = Table(payment_details, colWidths=[1.5*inch, 2*inch, 2.5*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(payment_table)
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_text = f"Dicetak pada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    footer = Paragraph(footer_text, normal_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # FileResponse
    buffer.seek(0)
    return buffer
