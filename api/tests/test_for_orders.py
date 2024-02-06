import unittest
from .. import create_app # What happened here is that we can't find the __init__.py file in the utility folder the normal way so, what to do instead is to go out of the test folder using (..) then, import the create_app directly since for init folders, all the classes and functions can be imported without actually going into the folder.
from ..config.config import config_dict # Import the config_dict from the config folder and file.
from ..utility import db # Importing the db from utility
# from werkzeug.security import generate_password_hash
from ..models.orders import Order
from flask_jwt_extended import create_access_token


class OderTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test']) # We need to configure the key and change it to test since we are working on the unit test
        self.appctx = self.app.app_context() # This helps to create your databse in the shell. We created such context in api __init__.py which helps us access our database and create the model(@app.shell_context_processor then the function  def make_shell_context():)

        self.appctx.push() # push means create. This push pushes/creates the route to the appcontext (appctx). While pop means delete
        
        self.client = self.app.test_client()

        # Creating the db which we have imported fomr the utility folder
        db.create_all()

    def tearDown(self): # Think of this as a rollback which reset things. It just clears or deletes/resets a db and so if there exist a db like it.
        db.drop_all()

        self.app = None

        self.client = None

        self.appctx.pop()

    # Creating testcase for the getting all orders
    def test_get_all_orders(self):
        token = create_access_token(identity='testuser') # Create a dummy identity
        
        # The block of code below replicates what we have in insomnia since you can get authorizaton via the bearer tab or the Headers tab, we are using the headers tab in this situation where we now input the Authorization and then the Bearer, space then the token generated. Note, in the token generated, we are using a dummy identity gotten from the 'testuser' string.
        headers = {
            "Authorization" : f"Bearer {token}"
        }

        response = self.client.get('/orders/orders', headers=headers) # Since this route is protected, we need import jwt to be able to access this route. Also note, just like the user login/register, because we needed information to pass to the route, we specifically told it to take up the data in json form json=data now what we need here is headers hence headers=headers

        assert response.status_code == 200 # assert basically means to check this block of code or response. To assertain if this will give the expected result

        assert response.json == []

    # Creating a testcase for placing an order
    def test_place_an_order(self):
        token = create_access_token(identity='testuser')

        headers = {
            "Authorization": f"Bearer {token}"
        }

        data = {
            "size": "Small",
            "quantity": 3,
            "flavour": "Pepperonni",
            "pizza_type": "Italian"
        }

        response = self.client.post('orders/orders', json=data, headers=headers)

        assert response.status_code == 201

        # We want to check how many orders or the size of data that are in the db. So we do this;;

        orders = Order.query.all()

        order_id = orders[0].id # Getting the first order_id by scanning the list for the first value

        assert order_id == 1 # Checks if order_is is equivalent to 1

        assert len(orders) == 1 # Check if the number of orders are equal to 1 since we just placed a single order

        assert response.json ['size'] == 'Sizes.Small' # Checking to be sure that the size in the memory db (json['size']) which corresponds to the key (size) we created above is equal to the enum response 'Sizes.Small'

       
    # Creating a testcase for getting an order by id
    def test_get_single_order(self):
        token = create_access_token(identity='testuser')

        # Modifying the code to see if we can get a resposne of 200 or 201 instead of 404
        # Note below, while using the Order object, you have to assign the values as such "size = "Small" and not the dictionary form " "size": "Small" "
        data = Order(
            size = "Small",
            quantity = 3,
            flavour = "Pepperonni",
            pizza_type = "Italian"
        )

        data.save()
        # End of modification

        headers = {
            'Authorization': f"Bearer {token}" 
        }

        response = self.client.get('/orders/order/1', headers=headers)

        orders = Order.query.all()

        assert len(orders) == 1

        # assert response.status_code == 404 # We expect a 404 error here because there's technically nothing in our db because we tear everythin down after operation also we are using memory db too, so, an error not found will be thrown (404)

        assert response.status_code == 200 # For the modified code

        # Try doing a post request to create/place an order in this same test case to see if you'd be able to get the order without getting a 404