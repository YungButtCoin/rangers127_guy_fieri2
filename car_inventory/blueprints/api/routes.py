from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

#internal imports
from car_inventory.models import Customer, Car, carOrder, Order, db, car_schema, cars_schema

#instantiate our blueprint
api = Blueprint('api', __name__, url_prefix='/api') #all our endpoints need to be prefixed with API

@api.route('/token', methods = ['GET', 'POST'])
def token():

    data = request.json

    if data:
        client_id = data['client_id'] #looking for the key of the client_id on the dictionary passed to us
        access_token = create_access_token(identity=client_id)
        return {
            'status' : 200,
            'access_token': access_token
        }
    else:
        return{
            'status': 400,
            'message': 'Missing Client Id. Try Again'
        }

#creating our READ data request for shop
@api.route('/shop')
@jwt_required() # if we don't have this access token, then we can't make an api call
def get_shop():

    shop = Car.query.all() # list of objects, we can't send a list of objects through api calls

    response = cars_schema.dump(shop) #takes our list of objects and turns it into a list of dictionaries
    return jsonify(response) #jsonify essentially stringifies the list to send to our frontend

#creating our READ data request for orders, READ associated with "GET"
@api.route('/order/<cust_id>')
@jwt_required()
def get_order(cust_id):

    #We need to grab all the order_ids associated with the customer
    #Grab all the products on that particular order

    car_order = carOrder.query.filter(carOrder.cust_id == cust_id).all()

    data = []

    #need to traverse to grab all the products from each other
    for order in car_order:
        
        car = Car.query.filter(Car.car_id == order.car_id).first()

        car_data = car_schema.dump(car)

        car_data['quantity'] = order.quantity
        car_data['order_id'] = order.order_id
        car_data['id'] = order.car_order_id

        data.append(car_data)

    return jsonify(data)

@api.route('/order/create/<cust_id>', methods = ['POST'])
@jwt_required()
def create_order(cust_id):

    data = request.json

    customer_order = data['order']

    customer = Customer.query.filter(Customer.cust_id == cust_id).first()
    if not customer:
        customer = Customer(cust_id)
        db.session.add(customer)

    order = Order()
    db.session.add(order)

    for car in customer_order:

        car_order = carOrder(car['car_id'], car['quantity'], car['price'], order.order_id, customer.cust_id)
        db.session.add(car_order)

        order.increment_order_total(car_order.price)

        current_car = Car.query.filter(Car.car_id == car['car_id']).first()
        current_car.decrement_quantity(car['quantity'])

    db.session.commit()

    return {
        'status': 200,
        'message': 'New Order was created!'
    }

@api.route('/order/update/<order_id>', methods=['PUT','POST'])
@jwt_required()
def update_order(order_id):
    try:

        data = request.json
        new_quantity = int(data['quantity'])
        car_id = data['car_id']

        car_order = carOrder.query.filter(carOrder.order_id == order_id, carOrder.car_id == car_id).first()
        order = Order.query.get(order_id)
        car = Car.query.get(car_id)

        car_order.set_price(car.price, new_quantity)

        diff = abs(car_order.quantity - new_quantity)

        if car_order < new_quantity:
            car.decrement_quantity(diff)
            order.increment_order_total(car_order.price)
        
        elif car_order > new_quantity:
            car.increment_quantity(diff)
            order.decrement_order_total(car_order.price)

        car_order.update_quantity(new_quantity)

        db.session.commit()

        return {
            'status': 200,
            'message': 'Order was successfully updated!'
        }
    
    except:

        return{
            'status': 400,
            'message': 'Unable to process your request.  Please try again'
        }
    
@api.route('/order/delete/<order_id>', methods=['DELETE'])
@jwt_required()
def delete_car_order(order_id):

    data = request.json
    car_id = data['car_id']

    car_order = carOrder.query.filter(carOrder.order_id == order_id, carOrder.car_id == car_id).first()

    order = Order.query.get(order_id)
    car = Car.query.get(car_id)

    order.decrement_order_total(car_order.price)
    car.increment_quantity(car_order.quantity)

    db.session.delete(car_order)
    db.session.commit()

    return {
        'status': 200,
        'message': 'Order was successfully deleted!'
    }