# This will handle the sign up/sign in and authentication.
from flask import request # Will be used to request for data in json format.
from flask_restx import Namespace, Resource, fields # Think of Resource as more of MethodView
from ..models.users import User # This will bring in the save function defined in the user class
from werkzeug.security import generate_password_hash, check_password_hash # Using werkzeug.security for our security in place of passlib.hash
from http import HTTPStatus # This will be used to get http status instead of the basic status code (401, 404, 201) we manually type in. We also can selected from a predefined list of codes to choose from. 
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_namespace = Namespace('auth', description='namespace for authentication') # Just like we define aa blueprint in the smorest blueprint which is viewd with swagger-ui

# Creating a serializer which is known as the Schema in Flask Smorest

signup_model = auth_namespace.model(
    'Signup', {
        'username': fields.String(required=True, description="A username"), # Since we're using swagger-ui, you can add descriptions to your schema to define what each schema/serializer does. This in turn will print ut the description for easy reference.
        'email': fields.String(required=True, description="An email"),
        'password': fields.String(required=True, description="A password")
    }
)

# Another schema or in this case another model that will help us represent our data.
user_model = auth_namespace.model(
    'User', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description="A username"), # Since we're using swagger-ui, you can add descriptions to your schema to define what each schema/serializer does. This in turn will print ut the description for easy reference.
        'email': fields.String(required=True, description="An email"),
        'password_hash': fields.String(required=True, description="A password"),
        'is_active': fields.Boolean(description='Shows a user\'s active status'),
        'is_staff': fields.Boolean(description='This shows in Boolean form if the user is a staff or not')
    }
)

# Creating the user login model.
login_model = auth_namespace.model(
    'Login', {
        'email': fields.String(required=True, description="An email"),
        'password': fields.String(required=True, description="A password")
    }
)

@auth_namespace.route('/signup')
class SignUp(Resource):
    @auth_namespace.expect(signup_model) # This is mainly for making user inputs. Passing the serialised model in the argument so that any data coming in can be serialised on the go. This is similar to @blueprint.response or @blueprint.argument. This tells the code what exactly to expect in essence, what data is coming in. If we put in thr signup model, it will work with that model, also if we put in the argument field the user_model, it will work with that model.
    @auth_namespace.marshal_with(user_model) # Specifies the field to use in serializing. Also, it helps to represent our data in json (dictionary) format so it can easily return it after creation.
    
    def post(self):
        """Signup"""
        
        data = request.get_json()

        new_user = User(
            username = data.get('username'),
            email = data.get('email'),
            password_hash = generate_password_hash(data.get('password'))
            )
        
        new_user.save()

        return new_user, HTTPStatus.CREATED # {'message': 'Created Successfully'}

@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_model) # This is mainly for making user inputs. Passing the serialised model in the argument so that any data coming in can be serialised on the go. This is similar to @blueprint.response or @blueprint.argument. This tells the code what exactly to expect in essence, what data is coming in. If we put in thr signup model, it will work with that model, also if we put in the argument field the user_model, it will work with that model.

    def post(self):
        """Generate JWT Token and Login"""
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        # Since email is unique, we'll check the db to get the unique email and the data attached to the email.
        user = User.query.filter_by(email=email).first()

        if (user is not None) and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.CREATED


@auth_namespace.route("/refresh")
class Refresh_Token(Resource):
    @jwt_required(refresh=True)
    def post(self):
        username = get_jwt_identity()

        # return{"username": username} # Just testing out the code to see what it will return (think of it as a debugging mechanism)

        access_token = create_access_token(identity=username) # TO get this you have to go to the route in insomnia, first log in a user then, copy the user's refresh token, open up the'Auth" section, click on the brearer authorization then paste the token you copied. Remeber that this access token is what will be used instead of the first one so it doesn't unexpectdely expire.
        return {"access_token": access_token}, HTTPStatus.OK 

