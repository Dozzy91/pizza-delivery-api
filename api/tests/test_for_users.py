import unittest
from .. import create_app # What happened here is that we can't find the __init__.py file in the utility folder the normal way so, what to do instead is to go out of the test folder using (..) then, import the create_app directly since for init folders, all the classes and functions can be imported without actually going into the folder.
from ..config.config import config_dict # Import the config_dict from the config folder and file.
from ..utility import db # Importing the db from utility
# from werkzeug.security import generate_password_hash
from ..models.users import User


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test']) # We need to configure the key and change it to test since we are working on the unit test
        self.appctx = self.app.app_context() # This helps to create your databse in the shell. We created such context in api __init__.py which helps us access our database and create the model(@app.shell_context_processor then the function  def make_shell_context():)

        self.appctx.push() # push means create while pop means delete
        
        self.client = self.app.test_client()

        # Creating the db which we have imported fomr the utility folder
        db.create_all()

    def tearDown(self): # Think of this as a rollback which reset things. It just clears or deletes/resets a db and so if there exist a db like it.
        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None

    # Creating testcase for the user registration
    def test_user_registration(self): # Testing the user  registration route
        # Creating test data
        data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/signup', json=data) # Getting information from the client with the signup endpoint. json=data means that the test should expect a json data.

        user = User.query.filter_by(email="testuser@gmail.com").first()

        assert user.username == 'testuser' # This checks if the username created is the same and the expected testuser username in the memory db
        assert response.status_code == 201 # Here, we are expecting a status code of 201 to show that the route/code ran successfully, if not, then there is a rpblem. Note that each time you want to run a test, you'll have to use assert

    # Creating the login test
    def test_user_login(self):
         # Creating test data
        data = {
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200

# You need not run the server when you're doing pytest, automatically, the server will be fired up when you run pytest by simply running "pytest"
