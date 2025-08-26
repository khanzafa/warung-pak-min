from app.extensions import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    price_per_bundle = db.Column(db.Integer, default=8500)
    portions_per_bundle = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    daily_orders = db.relationship('DailyOrder', backref='customer', lazy=True, cascade='all, delete-orphan')
    kasbons = db.relationship('Kasbon', backref='customer', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'