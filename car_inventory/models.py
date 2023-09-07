from werkzeug.security import generate_password_hash #allows us to generate a hashed password
from flask_sqlalchemy import SQLAlchemy #allows our database to read our classes/objects as tables/rows 
from flask_login import UserMixin, LoginManager #allows us to load a current logged in user
from datetime import datetime
import uuid #generate a unique id (basically the same serializing last week)
from flask_marshmallow import Marshmallow

#internal imports
from .helpers import get_image



db = SQLAlchemy() #instantiate our database
login_manager = LoginManager() #instantiate our login manager
ma = Marshmallow() #instantiating our Marshmellow class



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) #this queries our database & brings back the user with the same id



class User(db.Model, UserMixin):
    #think of this part as the CREATE TABLE 'User' 
    user_id = db.Column(db.String, primary_key = True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    #think of our __init__() as our INSERT INTO 
    def __init__(self, username, email, password, first_name="", last_name=""):
        self.user_id = self.set_id() #method to create a unique id
        self.first_name = first_name
        self.last_name = last_name 
        self.username = username
        self.email = email
        self.password = self.set_password(password) #method to hash our password for security 


    def set_id(self):
        return str(uuid.uuid4())
    
    def get_id(self):
        return str(self.user_id)
    

    def set_password(self, password):
        return generate_password_hash(password)
    

    def __repr__(self):
        return f"<USER: {self.username}"

class Car(db.Model):
    car_id = db.Column(db.String, primary_key = True)
    make = db.Column(db.String(25), nullable = False)
    model = db.Column(db.String(25), nullable = False)
    color = db.Column(db.String(25), nullable = False)
    year = db.Column(db.String(10), nullable = False)
    image = db.Column(db.String, nullable = False)
    description = db.Column(db.String(200))
    price = db.Column(db.Numeric(precision=10, scale=2), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    #user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable = False) #if we wanted to make a foreign key relationship

    def __init__(self, make, model, year, color, price, quantity, image = '', description = ''):
        self.car_id = self.set_id()
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.price = price
        self.quantity = quantity
        self.image = self.set_image(image, model, make, year, color)
        self.description = description

    def set_id(self):
        return str(uuid.uuid4()) #create unique ID
    
    def set_image(self, image, model, make, year, color):
        if not image: 
            image = get_image(color+year+make+model) #adding get_image function which makes an external API call

        return image
    
    def decrement_quantity(self, quantity):
        self.quantity -= int(quantity)
        return self.quantity #all methods need to return otherwise the object attribute doesn't get updated
    
    def increment_quantity(self, quantity):
        self.quantity += int(quantity)
        return self.quantity
    
    def __repr__(self):
        return f'<car: {self.model}>'
    

class Customer(db.Model):
    cust_id = db.Column(db.String, primary_key = True)
    date_created = db.Column(db.DateTime, default = datetime.utcnow) 
    car_order = db.relationship('carOrder', backref = 'customer', lazy = True) #backref is how are these related, lazy means a customer can exist without the carOrder table


    def __init__(self, cust_id):
        self.cust_id = cust_id #we are getting their id from the front end


#many to many relationship with cars, Customers & Orders
#So we need a join table

class carOrder(db.Model):
    car_order_id = db.Column(db.String, primary_key = True)
    car_id = db.Column(db.String, db.ForeignKey('car.car_id'), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Numeric(precision = 10, scale = 2), nullable = False)
    order_id = db.Column(db.String, db.ForeignKey('order.order_id'), nullable = False)
    cust_id = db.Column(db.String, db.ForeignKey('customer.cust_id'), nullable = False)
    
    def __init__(self, car_id, quantity, price, order_id, cust_id):
        self.car_order_id = self.set_id()
        self.car_id = car_id
        self.quantity = quantity
        self.price = self.set_price(price, quantity)
        self.order_id = order_id
        self.cust_id = cust_id


    def set_id(self):
        return str(uuid.uuid4())
    
    def set_price(self, price, quantity):
        quantity = int(quantity)
        price = float(price)

        self.price = quantity * price
        return self.price
    
    def update_quantity(self, quantity): #method used for when customers update their order quantity of a specific car
        self.quantity = int(quantity)
        return self.quantity 


class Order(db.Model):
    order_id = db.Column(db.String, primary_key = True)
    order_total = db.Column(db.Numeric(precision = 10, scale = 2), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow())
    preorder = db.relationship('carOrder', backref = 'order', lazy = True)

    def __init__(self):
        self.order_id = self.set_id()
        self.order_total = 0.00

    def set_id(self):
        return str(uuid.uuid4())
    
    #for every car's total price in carorder table add to our order's total price
    def increment_order_total(self, price):
        self.order_total = float(self.order_total)
        self.order_total += float(price)

        return self.order_total
    
    def increment_order_total(self, price):
        self.order_total = float(self.order_total)
        self.order_total -= float(price)

        return self.order_total
    
    def __repr__(self):
        return f'<ORDER: {self.order_id}>'

#Because we are building a RESTful API this week (Representational State Transfer)
#json rules that world.  JavaScript Object Notation aka dictionaries

#Build our Schema
#How your object looks when being passed from server to server
#These will look like dictionaries

class carSchema(ma.Schema):
    class Meta: 
        fields = ['car_id', 'make', 'model', 'year', 'color', 'image', 'description', 'price', 'quantity']


car_schema = carSchema() # this is for passing 1 singular car
cars_schema = carSchema(many = True) # this is for passing mulitple cars, list of dictionaries