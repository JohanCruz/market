
from flask import request, Blueprint
from flask_restful import Api, Resource

from .schemas import CustomerSchema, ProductSchema, OrderSchema, OrderDetailSchema, CustomerOrdersSchema
from ..models import Customer, Product, Order, Order_Detail

from sqlalchemy import and_, func
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
films_v1_0_bp = Blueprint('films_v1_0_bp', __name__)

customer_schema = CustomerSchema()
product_schema = ProductSchema()
order_schema = OrderSchema()
order_detail_schema = OrderDetailSchema()
customer_order_schema = CustomerOrdersSchema()


api = Api(films_v1_0_bp)

class CustomerListResource(Resource):
    def get(self):
        customers = Customer.get_all()
        result = customer_schema.dump(customers,  many=True)
        return result

    def post(self):
        data = request.get_json()
        customer_dict = customer_schema.load(data)
        customer = Customer(name=customer_dict['name'],
                    email=customer_dict['email']
        )
        print(customer.name)
        print(customer.email)        
        customer.save()
        resp = customer_schema.dump(customer)
        return resp, 201

class CustomerResource(Resource):    

    def get(self, customer_id):
        customer = Customer.get_by_id(customer_id)
        if customer is None:
            raise ObjectNotFound('El cliente no existe')
            #resp = customer_schema.dump({"message":1})
        else:
            resp = customer_schema.dump(customer)
        return resp

class ProductListResource(Resource):
    def get(self):
        products = Product.get_all()
        result = product_schema.dump(products,  many=True)
        return result

    def post(self):
        data = request.get_json()
        product_dict = product_schema.load(data)
        product = Product(name = product_dict['name'],
                    product_description = product_dict['product_description'],
                    price = product_dict['price']
        )        
        product.save()
        resp = product_schema.dump(product)
        return resp, 201

class ProductResource(Resource):    

    def get(self, product_id):
        product = Product.get_by_id(product_id)
        
        if product is None:
            raise ObjectNotFound('El producto no existe')
        else:
            resp = product_schema.dump(product)
        return resp

class OrderListResource(Resource):
    def get(self):
        orders = Order.get_all()
        
        if not orders :
            #raise ObjectNotFound('No hay ordenes')
            return {"message":"no se encuentran ordenes"}
        else:
            result = order_schema.dump(orders, many=True)
            return result
            

    def post(self):
        """
        recibe orden 
        
        """

        {   
            "customer_id": 1,
            "delivery_address": "calle 102 #19-23",
            "total": 500,
            "requested_products":[ {
                    "product_id": 1,
                    "order_id" : 1,
                    "product_description": "xbox-360",
                    "price": 500,
                    "quantity": 1
                },
                {
                    "product_id": 2,
                    "order_id" : 1,
                    "product_description": "xbox-360v2",
                    "price": 560,
                    "quantity": 3
                }]
        }
        
        data = request.get_json()
        order_dict = order_schema.load(data)
        order = Order(customer_id = order_dict['customer_id'],
                delivery_address = order_dict['delivery_address'],
                total = order_dict['total']
            )
        requested_products = order_dict['requested_products']
        if len(requested_products) == 0 or len(requested_products) > 5 :
            resp = {"error":"cantidad de productos solicitados: "+ str(len(requested_products))}
            return resp, 400
        
        customer = Customer.get_by_id(order.customer_id)
        if not customer:
            resp = {"error":"Cliente solicitado errado"}
            return resp, 400
        
        products = customer.products

        for item in requested_products:
            product = Product.get_by_id(item['product_id'])
            if not product:
                resp = {"error":"producto solicitado no existe"}
                return resp, 400
            else:
                if not product in products:
                    resp = {"error":"producto solicitado no habilitado para el cliente"}
                    return resp, 400
                else:
                    if not ( type(item['price'])== type(5) or type(item['price'])== type(5.5)):
                        resp = {"error":"el precio debe ser numérico"}
                        return resp, 400
                    if not ( type(item['quantity'])== type(5) or type(item['quantity'])== type(5.5)):
                        resp = {"error":"el precio debe ser numérico"}
                        return resp, 400 

        order.save()
        orders_details = Order_Detail.get_all()
        id = len(orders_details)
        total = 0
        for item in requested_products:
            id += 1
            order_detail = Order_Detail(order_detail_id = id,
                product_id = item['product_id'],
                order_id = order.order_id,
                product_description = item['product_description'],
                price = item['price'],
                quantity =  item['quantity']
            )
            total += order_detail.quantity*order_detail.price
            order_detail.save()

        order.total = total
        order.save()
        resp = order_schema.dump(order)
        return resp, 201
            
class OrderResource(Resource):    

    def get(self, order_id):
        order = Order.get_by_id(order_id)
        
        if Order is None:
            raise ObjectNotFound('La orden no existe')
            #resp = order_schema.dump({"message":1})
                    
        resp = order_schema.dump(order)            
        return resp

class OrderCustomerResource(Resource): 
    """
    GET 
    http://localhost:5000/api/v1.0/orders/customer/1
    {   
            
    "start_date":"2012-01-01",
    "end_date":"2021-01-01"
            
}
    """   

    def get(self, customer_id):
        data = request.get_json()
        customer_orders = customer_order_schema.load(data)
        start_date = customer_orders['start_date']
        end_date = customer_orders['end_date']
        orders =db.session.query(Order).filter(and_(func.date(Order.creation_date) >= start_date,
                                              func.date(Order.creation_date) <= end_date ))

        result = order_schema.dump(orders, many=True)

        
        return result

  

       

class OrderDetailListResource(Resource):
    def get(self):
        orders_details = Order_Detail.get_all()
        
        if not orders_details :
            #raise ObjectNotFound('No hay ordenes')
            return {"message":"no se encuentran detalles de las ordenes"}
        else:
            result = order_detail_schema.dump(orders_details, many=True)
            return result
            

    def post(self):

        '''{
            "product_id": 1,
            "order_id" : 1,
            "product_description": "xbox-360",
            "price": 500,
            "quantity": 1
        }'''
        
        data = request.get_json()
        order_detail_dict = order_detail_schema.load(data)

        orders_details = Order_Detail.get_all()
        id = len(orders_details)
        
        order_detail = Order_Detail(order_detail_id = id+1,
                product_id = order_detail_dict['product_id'],
                order_id = order_detail_dict['order_id'],
                product_description = order_detail_dict['product_description'],
                price = order_detail_dict['price'],
                quantity =  order_detail_dict['quantity']
            )
        
        order = Order.get_by_id(order_detail.order_id)

        if order:
            customer = Customer.get_by_id(order.customer_id)
            if customer:
                products = customer.products
                product = Product.get_by_id(order_detail.product_id)
                if product in products:

                    order_detail.save()
                    resp = order_detail_schema.dump(order_detail)
                    return resp, 201
                else:
                    return {"message":"producto no habilitado"}
            else:
                    return {"message":"cliente no encontrado"}
        else:
            return {"message":"orden no encontrada"}

        



class MockupResource(Resource):
    def get(self):
        c1 = Customer(name = "Johan Cruz", email = "Johandanielcruz@gmail.com")
        c2 = Customer(name = "Jeison Torres", email = "Jeison@gmail.com")
        p1 = Product(name = "pc", product_description = "all on one", price= 12.35)
        p2 = Product(name = "laptop", product_description = "gamer", price= 19.49)
        p1.customers.append(c1)
        p1.customers.append(c2)
        p2.customers.append(c1)

        "el cliente 1 tiene 2 productos elegibles por comprar , el cliente 2 solo tiene 1"
        c1.save()
        c2.save()
        p1.save()
        p2.save()

        '''
        o1 = Order(customer_id = c1.customer_id, delivery_address = "cll 123 # 13-24",
              total = 123.0)
        o2 = Order(customer_id = c1.customer_id, delivery_address = "cll 46 -60",
              total = 123.34)
        '''
        
        " se crean dos ordenes para el cliente de id # 1 "
        '''
        o1.save()
        o2.save()
        ''' 
        
        customers = Customer.get_all()
        result = customer_schema.dump(customers, many=True)

        return result

        #http://localhost:5000/api/v1.0/mockup


api.add_resource(CustomerListResource, '/api/v1.0/customers/', endpoint='customer_list_resource')
api.add_resource(CustomerResource, '/api/v1.0/customers/<int:customer_id>', endpoint='customer_resource')
api.add_resource(ProductListResource, '/api/v1.0/products/', endpoint='product_list_resource')
api.add_resource(ProductResource, '/api/v1.0/products/<int:product_id>', endpoint='product_resource')

api.add_resource(OrderListResource, '/api/v1.0/orders/', endpoint='order_list_resource')
api.add_resource(OrderResource, '/api/v1.0/orders/<int:order_id>', endpoint='order_resource')

api.add_resource(OrderCustomerResource, '/api/v1.0/orders/customer/<int:customer_id>', endpoint='order_customer_resource')

api.add_resource(MockupResource, '/api/v1.0/mockup/', endpoint='mockup_resource')

api.add_resource(OrderDetailListResource, '/api/v1.0/orders_details/', endpoint='order_detail_list_resource')