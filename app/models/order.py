from app.extensions import db
from datetime import datetime, date

class DailyOrder(db.Model):
    __tablename__ = 'daily_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    morning_portions = db.Column(db.Integer, default=0)
    afternoon_portions = db.Column(db.Integer, default=0)
    evening_portions = db.Column(db.Integer, default=0)
    total_portions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<DailyOrder {self.date} - Customer {self.customer_id}>'