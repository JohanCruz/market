from marshmallow import fields

from app.ext import ma



class CustomerSchema(ma.Schema):
    customer_id = fields.Integer(dump_only=True)
    name = fields.String()
    email = fields.String()
    products = fields.Nested('ProductSchema', many=True)
    orders = fields.Nested('OrderSchema', many=True)

    class Meta:
        fields = ('customer_id', 'name','email', 'products', 'orders')
        ordered = True

class ProductSchema(ma.Schema):
    product_id = fields.Integer(dump_only=True)
    name = fields.String()
    product_description = fields.String()
    price = fields.Float()
    customers = fields.Nested('CustomerSchema')

    class Meta:
        fields = ('product_id', 'name','product_description', 'price')
        ordered = True

class OrderSchema(ma.Schema):
    order_id = fields.Integer(dump_only=True)
    delivery_address = fields.String()
    customer_id = fields.Integer()
    total = fields.Float()
    creation_date = fields.String()
    requested_products = fields.Nested('OrderDetailSchema', many=True)

    class Meta:
        fields = ('customer_id', 'delivery_address', 'total', 'creation_date','requested_products') 
        ordered = True

class OrderDetailSchema(ma.Schema):
    order_detail_id = fields.Integer(dump_only=True)
    order_id = fields.Integer()
    product_id = fields.Integer()
    product_description = fields.String()
    price = fields.Float()
    quantity = fields.Integer()
    class Meta:
        fields = ('order_detail_id','order_id', 'product_id','product_description','price','quantity')
        ordered = True

class CustomerOrdersSchema(ma.Schema):
    start_date = fields.String()
    end_date = fields.String()
    class Meta:
        fields = ('start_date','end_date')
        ordered = True

    
