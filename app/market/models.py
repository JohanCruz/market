from email.policy import default
from app.db import db, BaseModelMixin
from sqlalchemy.dialects import mysql

import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(db.Model, BaseModelMixin):
    __tablename__ = "customer"
    customer_id = db.Column(mysql.INTEGER(10), primary_key=True)
    name = db.Column(db.String(length=191))
    email = db.Column(db.String(length=191))
    products = db.relationship('Product', secondary='customer_product', back_populates="customers")
    orders = db.relationship('Order', backref='customer', lazy=False, cascade='all, delete-orphan')
     
class Order_Detail(db.Model, BaseModelMixin):
    __tablename__ = 'order_detail'
    order_detail_id = db.Column(mysql.INTEGER(10), primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key = True)
    
    product_description = db.Column(db.String(length=191))
    price = db.Column(db.Numeric(10,2, asdecimal=False))
    quantity = db.Column(mysql.INTEGER(10), default=0)

class Product(db.Model, BaseModelMixin):
    __tablename__ = "product"
    product_id = db.Column(mysql.INTEGER(10), primary_key=True)
    name = db.Column(db.String(length=191))
    product_description = db.Column(db.String(length=191))
    price = db.Column(db.Numeric(10,2, asdecimal=False))
    customers = relationship('Customer', secondary='customer_product', back_populates="products")
    requested_products = relationship('Order_Detail', backref='product',
                         primaryjoin= product_id == Order_Detail.product_id)
    def __repr__(self):
        return f'{self.product_id}'

    def __str__(self):
        return f'{self.product_id}'
    

class Customer_Product(db.Model, BaseModelMixin):
   __tablename__ = 'customer_product'
   customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), primary_key = True)
   product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key = True)
   

class Order(db.Model, BaseModelMixin):
    __tablename__ = 'order'
    order_id = db.Column(mysql.INTEGER(10), primary_key=True)
    customer_id = db.Column(mysql.INTEGER(10), db.ForeignKey('customer.customer_id'), nullable=False)
    creation_date = db.Column(DateTime, default= datetime.datetime.utcnow)
    delivery_address = db.Column(db.String(length=191))
    total = db.Column(db.Numeric(10,2, asdecimal=False))
    requested_products = relationship('Order_Detail', backref='order',
                         primaryjoin= order_id == Order_Detail.order_id)


    
    

    