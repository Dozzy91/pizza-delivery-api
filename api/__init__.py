from flask import Flask
from flask_restx import Api
from .auth.views import auth_namespace # Importing from a folder, make sure you tell it if the folder you want to import is in the same folder as the init file hence .auth.views
from .orders.views import orders_namespace
from .config.config import config_dict # Importing the config dictionary (config_dict) which will give us access to the various classes
from .utility import db # Importing the database from the utility folder
from .models.orders import Order # Importing the Order model
from .models.users import User # Importing the User model
from flask_migrate import Migrate # Helps to modify the database without needing to delethe entire databse when wahala burst 
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound, MethodNotAllowed

def create_app(config): # Depending on the configuration we want to use, which will be passed in as an argument, we can simply change it here to either "dev", "prod" or "test" depending on what task we want to carry out.
                        # Note, leaving this parameter as 'config' in order to get data from runserver.py when called actually runs the server but it does not run Flask shell, also it creates the db but Flask shell will never work. So we have to leave to as this "config=config_dict['prod']".
                        # Also, trying to create the db with the config as parameter raised errors. To avoid that, we have to manually enter 'prod'/'test'/'dev' as argument both here and runserver that is (config=config_dict['prod']) 
    
    app = Flask(__name__)

    app.config.from_object(config) # This is gets values form an object and updates them to the current state. In this case, it's getting the config_dict['dev'] dictionary from the config.py file and updates it depending on what config is passed in which could be 'prod' or 'test'

    db.init_app(app) # db has a method ".init_app" which is used to initialise a database in this operation

    jwt = JWTManager(app)
    
    migrate = Migrate(app, db)

    # In order to be able to enter access tokens in swagger-UI or have access token functionality more accurately authorization features, the follow code treats that.

    # Defining the authorization
    authorizations = { # Notice how this is more like what we have in insomnia in the headeer/authorization section
        "Bearer Auth" : {
            'type': 'apiKey',
            'in' : 'header', # "in" here means where you'd want to add the token to and in thiscase, it's the header.
            'name': 'Authorization',
            'description' : 'Add a JWT Token to the header with ** Bearer &lt;JWT&gt; token to authorize** ' # Note from the ** to the other **, what you have there is regular expression where &lt = lessthan, JWT is JWT &gt=greaterthan
        }
    }


    # Below, we will be editing and modifying our App information to have a more unique look on swagger ui. The documentation plus comments will be added as well
    api = Api(
        app,
        title = "Pizza Delivery API",
        description = "A simple pizza delivery REST API service",
        # version = 1.0 # This version is a bit tricky because if you add a version that's not same with the FLask restx version, there might be conflicts.
        authorizations= authorizations,
        security = 'Bearer Auth' 
        )

    api.add_namespace(orders_namespace) # No need adding a path to this because technically, this will turn to the landing/home page leaving the path option blank will assign a default path of "/" putting a path of '/' or '/orders' will turn the swaggger-ui path to '//' or '/orders//' respectively
    api.add_namespace(auth_namespace, path='/auth')

    # Coding different error handlers
      # Not Found
    @api.errorhandler(NotFound) # This block of code kicks in whenever the code meets a not found error. Instead of all those plenty strings, the code will just return the simple message that is (return {"error": "Not Found"})
    def not_found(error):
        return {"error": "Not Found"}, 404

      # Method not allowed
    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 404
    
    #Accessing our db models
    @app.shell_context_processor # This helps us create our model, connect to the databse and do our migrate
    def make_shell_context():
        return{
            'db': db,
            'User': User,
            'Order': Order
        }
    
    return app