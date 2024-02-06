from flask_restx import Namespace, Resource, fields
from ..models.orders import Order # Importing Order to use the save function and also get the databse schemas
from ..models.users import User # Doing this, we will query user db to get the current user check comment 2 line 36
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utility import db

orders_namespace = Namespace("orders", description='orders') # Just like we define a blueprint variable, in the smorest blueprint which is viewd with swagger-ui

###Test running an idea here###
# auth_namespace = Namespace('auth', description='namespace for authentication')
# user_model = auth_namespace.model(
#     'User', {
#         'id': fields.Integer(),
#         'username': fields.String(required=True, description="A username"), # Since we're using swagger-ui, you can add descriptions to your schema to define what each schema/serializer does. This in turn will print ut the description for easy reference.
#         'email': fields.String(required=True, description="An email"),
#         'password_hash': fields.String(required=True, description="A password"),
#         'is_active': fields.Boolean(description='Shows a user\'s active status'),
#         'is_staff': fields.Boolean(description='This shows in Boolean form if the user is a staff or not'),
#         'orders': fields.String()
#     }
# )
######


order_model = orders_namespace.model(
    'Order', {
        'id': fields.Integer(description='Order Id'),
        'size': fields.String(description='Size of customer\'s order', required=True,
                              enum = [ 'Small', 'Medium', 'Large', 'Extra_Large', 'Family_Size']),
        'flavour': fields.String(description='Flavour of the Pizza',
                                 enum = ['Pepperonni', 'Bbq_Chicken', 'Hawaiian', 'Neapolitan', 'Sicilian',
                                         'Veggie', 'Apple', 'Pineapple']),
        'quantity': fields.Integer(description='Qunatity of the Pizza', required=True),
        'pizza_type': fields.String(description='Type of Pizza',
                                    enum = ['Greek', 'Italian', 'New_York', 'Basic']),
        'order_status': fields.String(description='Status of customer\'s order ',
                                      enum = ['NOT_ORDERED', 'PENDING', 'IN_TRANSIT', 'DELIVERED', 'CANCELED']),
        'customer': fields.Integer(description='Customer\'s user Id')
    }
)

order_model_output = orders_namespace.model(
    'Order', {
        'size': fields.String(description='Size of customer\'s order', required=True,
                              enum = [ 'Small', 'Medium', 'Large', 'Extra_Large', 'Family_Size']),
        'flavour': fields.String(description='Flavour of the Pizza',
                                 enum = ['Pepperonni', 'Bbq_Chicken', 'Hawaiian', 'Neapolitan', 'Sicilian',
                                         'Veggie', 'Apple', 'Pineapple']),
        'quantity': fields.Integer(description='Qunatity of the Pizza', required=True),
        'pizza_type': fields.String(description='Type of Pizza',
                                    enum = ['Greek', 'Italian', 'New_York', 'Basic'])
    }
)

order_status_model = orders_namespace.model(
    'OrderStatus', {
        'order_status': fields.String(description='Update thhe Status of customer\'s order ', required=True,
                                      enum = ['NOT_ORDERED', 'PENDING', 'IN_TRANSIT', 'DELIVERED', 'CANCELED']),
    }
)

@orders_namespace.route('/orders') # Remember that authomatically, the route for the swagger-ui will be showing "/orders/" when we pass in "/" into the namespace route like this "orders_namespace.route('/')" (this is because of what we have up there in the Namespace configuration ('orders'). So it's picking from there) but on passing in "/orders" into the route, it will changes to "/orders/orders" or is we pass "/oda" we'll get "/orders/oda"
class OrderGetandCreate(Resource):
    @orders_namespace.marshal_with(order_model)
    # @orders_namespace.marshal_with(order_model_output)
    @orders_namespace.doc(description="Get all orders") # Adding documentation to the routes
    @jwt_required()
    def get(self):
        """Get all orders"""
        orders = Order.query.all()

        # return({'orders': orders}, HTTPStatus.OK) # Doing this is more detailed in the sense that is will show you a dictionary with null values if there is no data to be returned.
        return orders, HTTPStatus.OK  # This on the other hand will return an empty list if there is no data to be returned.

    @orders_namespace.expect(order_model) # Get all details of the all orders
    @orders_namespace.marshal_with(order_model) # Without adding this line, we got the error: "Object Order is not JSON serializable. So, should you want to serialize a data to be presented ot saved to the data base you need to do marshal_with if not, flask won't understand the data you're passing into it.
    @orders_namespace.doc(description="Place an order") # Adding documentation to the routes
    @jwt_required()
    def post(self):
        """Place an order"""

        username = get_jwt_identity() # When we get a token, it has every information of the user that logged in and created that the token, now this token has access to the username of the user which is unique. Now, with thhis, the username of the token owner will be saved to the username variable which will be used to query the database.

        current_user = User.query.filter_by(username=username).first() # Comment 2. For each user that signs in, the user gets a unique token, this toke is what the jwt looks for to identify the user. Now this token is attached to that user and is used to identify the user. On this line, we are querying with the user jwt_identity.

        data = orders_namespace.payload # This is another way of getting data which the user has inputed. Payload does not obey the serializer or the models, what it simply does is to take the user's input, and save it in the variable data whether or not there is a mistake.
        
        new_order = Order(
            size = data['size'],
            quantity = data['quantity'],
            flavour = data['flavour'],
            pizza_type = data['pizza_type'] 
        )

        new_order.user = current_user # new_order.user is gotten from backref of user table which has a relation with the order table. The user table is querried to get the current user which has logged in with the help of jwt_access_token. Once gotten, the user is then passed into the new_order.user variable which represents the logged in user that is placing the order
        
        new_order.save()

        return new_order, HTTPStatus.CREATED
    
@orders_namespace.route('/order/<int:order_id>')
class Get_Update_Delete_Orders_byId(Resource):
    @orders_namespace.marshal_with(order_model)
    @orders_namespace.doc(description="Get an order by ID",
                          params = {
                              'order_id' : 'An ID for an order'
                          }) # Adding documentation to the routes/endpoints. Params on the other hand defines the parameters or input you need to pass in.
    @jwt_required()
    def get(self, order_id):
        """Get a single order by ID"""
        order = Order.get_by_id(order_id) # Here we call the class method e defined in the order file (db/schema file)

        return order, HTTPStatus.OK
    
    @orders_namespace.expect(order_model) # This serializes the data we are expecting. SInce we are getting data to be updated, we need to add the ".expect" class because we are expecting data from the database thta'll be used to update some information and not just writing/posting or deleting from the database
    @orders_namespace.marshal_with(order_model)
    @orders_namespace.doc(description="Update an order by ID")
    @jwt_required()
    def put(self, order_id):
        """Update an order by id"""
        order_to_update = Order.get_by_id(order_id)

        # Using the payload to get the user input
        data = orders_namespace.payload

        # Below, you can choose to call or target the data any way you'd like whether using the dot notation using brackets. This does not work as explained below.

        order_to_update.size = data["size"]
        order_to_update.quantity = data["quantity"]
        order_to_update.flavour = data["flavour"]
        order_to_update.pizza_type = data["pizza_type"]

        # Below are lines of code that threw errors
        # order_to_update["pizza_type"] = data["pizza_type"] # Error, Order object does not support item assignment
        # order_to_update.pizza_type = data.pizza_type # Error, Dict object has no attribute pizza_type.
        # So technically you can't use dot notation on the data payload and you can't use object assignment on the databse dict element (order_to_update.pizza_type)

        order_to_update.update()
        # OR
        # db.session.commit()

        return order_to_update, HTTPStatus.OK
    @orders_namespace.doc(description="Delete and order by id")
    @jwt_required()
    def delete(self, order_id):
        """Delete an order by id"""
        order_to_delete = Order.get_by_id(order_id)

        # Order.delete(order_to_delete) # The function call. This also works thoug, but I will be commenting it out in the order model

        order_to_delete.delete() # The class method call. This is actually better, no need for passing an argument

        return {'msg': 'Order deleted successfully'}, HTTPStatus.OK


# Get a user order by id. Which translates to getting all orders ordered by a user
@orders_namespace.route('/user/<int:user_id>/order/<int:order_id>')
class GetSpecificOrderByUser(Resource):
    @orders_namespace.marshal_list_with(order_model) # If you have multiple things ypu want to display/present or return, marshal_list_with is your best best for that because it will help to serialize a lot of entries and present them in a list which is quite easy to peruse. But when returing just one item, marshal_with will do the trick. Though, using marshal_with in this case won't spoil anything though.
    @orders_namespace.doc(description="Get an order specific to a user",
                          params = {
                              'order_id' : 'An ID for an order',
                              'user_id': 'An Id for a user'
                          })
    @jwt_required()
    def get(self, user_id, order_id):
        """Get user specific orders"""
        # Getting the user
        user = User.get_by_id(user_id)

        # Getting the a order specific to the user.
        # To explain this well, the orders have the user_id attached to them, thanks to the backref. Now, the code below filters all the order (with the user key) which has the user id we which is equivalent to the our user id (user = User.get_by_id(user_id))
        # order = Order.get_by_id(order_id).filter_by(user=user).first() # This line of code did not work. So we used the next line of code to query the order by id, to get the order for that particular id, then we filter the order to get that which a specific user (with user_id) placed
        order = Order.query.filter_by(id=order_id).filter_by(user=user).first() # To get the specific orders, we first get the the get the order by id, then filter it using the user keyword. This makes sure that each user each order is specific to the user. And how we are able to get this is because of the backref we did with the user which injects the user_id into the oder table
        return order, HTTPStatus.OK
    
@orders_namespace.route('/user/<int:user_id>/orders')
class UserOrder(Resource):
    @orders_namespace.marshal_list_with(order_model) # If you have multiple things ypu want to display/present or return, marshal_list_with is your best best for that because it will help to serialize a lot of entries and present them in a list which is quite easy to peruse. But when returing just one item, marshal_with will do the trick. Though, using marshal_with in this case won't spoil anything though.
    # @orders_namespace.marshal_list_with(user_model) #Test running and idea here
    @orders_namespace.doc(description="Get all orders plced by a user",
                           params = {
                              'user_id': 'An Id for a specific user\'s orders'
                          })
    @jwt_required()
    def get(self, user_id):
        """Get all user Orders"""
        # Long explanation here, when an order is created, due to the relationsuip created using (orders = db.relationship('Order', backref='user', lazy=True)) the order is saved to the current user that placed the order, note that jwt access token and jwt identity helps us to identify the user that placed the order using the user_id, with this, we can now add the order tothe list of information which the user has.
        # One might wonder what customer is doing in the Order table, well, it's just there to link the user db to the order db just so we can get specific orders the user placed for instance, cutomer id of 1 translates to user id of one. SO once we are querying, we'll query the user id and get the orders tied to that user id/customer id
        user = User.get_by_id(user_id) # Getting the specific user
        user_orders = user.orders # Accessing the user orders and storing it in the user_orders variable. What happened here is that the all the infromation of the user was gotten in the previous line with the help of the user_id, later, the order specific to the user was pulled and passed into user_order variable. Remeber the user has relationship with the order db whcih helps it to get information of orders specific to each user. So with this, every order created by individual users are linked to the users themselve.

        # return user ## Test running an Idea here
        return user_orders, HTTPStatus.OK

@orders_namespace.route('/orders/status/<int:order_id>') # This route checks if the order was sucessfull or not
class UpdateOrdersSatus(Resource):
    @orders_namespace.expect(order_status_model)
    @orders_namespace.doc(description="Update the Status of an order",
                          params = {
                              'order_id' : 'An ID for an order'
                          })
    @jwt_required()
    def patch(self, order_id): # Patch helps you update just a single thing
        """Update order status"""
        data = orders_namespace.payload
        
        order_to_update = Order.get_by_id(order_id)
        order_to_update.order_status = data["order_status"]

        order_to_update.update()

        return {"msg": "Status updated successfully"}, HTTPStatus.OK