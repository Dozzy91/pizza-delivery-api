from ..utility import db
from enum import Enum 
from datetime import datetime

# For the fact that we want to create sizes for our pizza orders, like a user can decide to order a small pizza, large or medium oizza, we will be using the Enum to achieve this
# Enum: Is used store several values which can be accessed simultaenously of each other and mapped to different values depending on what the user selected. Enum cannot have two items of the same name.
# try checking if a dictionary can be used instead of enum

class Sizes(Enum):
    Small = 'small'
    Medium = 'medium'
    Large = 'large'
    Extra_Large = 'extra_large'
    Family_Size = 'family_size'

class OrderStatus(Enum):
    Not_Ordered = 'not_ordered'
    Pending = 'pending'
    In_Transit = 'in-transit'
    Delivered = 'delivered'
    Canceled = 'canceled'

class Flavours(Enum):
    Pepperonni = 'pepperoni'
    Bbq_Chicken = 'bbq chicken'
    Hawaiian = 'hawaiian'
    Neapolitan = 'neapolitan'
    Sicilian = 'sicilian'
    Veggie = 'veggie'
    Apple = 'apple'
    Pineapple = 'pineapple'

class PizzaType(Enum):
    Greek = 'Greek'
    Italian = 'Italian'
    New_York = 'New York'
    Basic = 'Basic'


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer(), primary_key=True)
    size = db.Column(db.Enum(Sizes), default=Sizes.Small)
    order_status = db.Column(db.Enum(OrderStatus), default=OrderStatus.Not_Ordered)
    flavour = db.Column(db.Enum(Flavours), nullable=False)
    quantity = db.Column(db.Integer(), default=1)
    pizza_type = db.Column(db.Enum(PizzaType), default=PizzaType.Basic)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    customer = db.Column(db.Integer(), db.ForeignKey('users.id')) # Getting a value from the users database Model. Note that the table name is users hence users.id

    def __repr__(self):
        return f"<Order {self.id}>"

    # Creating a save function to save our created user when called. WE have to import this in the auth view.py file.
    
    def save(self):
        db.session.add(self) # Self here acts like a filler, it gives you to opportuity to pass an argument into it without necessarily typing it in. so by calling th function save like this new_user.save(), you are more like saying save(new_user)
        db.session.commit()

    # Creating a delete function. Note, you can have it here or you can add it to your class method below
    # def delete(self):
    #     db.session.delete(self)
    #     db.session.commit()


    # Another way to get id from the database. This helps you to query a database to get individual id's. (Most times it is advisable to do this in order to keep thiings (your views.py) clean)
    @classmethod
    def get_by_id(self, id): # cls can be anything, we could even change it to self
        # get_by_id(cls, id)
        return self.query.get_or_404(id)
    
    def get_by_customer_id(self, customer): # cls can be anything, we could even change it to self
        # get_by_id(cls, id)
        return self.query.get_or_404(customer)

    # Creating a delete function. This is more efficient because is doesn't requre you to input an argument
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # Creating an update function
    def update(self):
        db.session.commit()