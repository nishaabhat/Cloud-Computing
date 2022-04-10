import hashlib
import uuid
import sqlite3
from flask_restful import Resource, reqparse
from model.users import UserModel
from model.sessions import SessionModel

# Resource: Login user
class Login(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="Username cannot be blank."
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="Password cannot be blank."
                        )

    # POST method: Login user after authentication
    def post(self):
        print("post triggered")
        data = Login.parser.parse_args()

        # Get password hash
        o_hash = hashlib.new('ripemd160')
        o_hash.update(data['password'].encode("utf-8"))

        # Authenticate and login
        user = UserModel.find_by_username(username=data['username'])
        if user is None:
            return {"message": "Username or Password is incorrect"}, 401
        elif o_hash.hexdigest() != user.password:
            return{"message": "Username or Password is incorrect"}, 401
        else:
            session_id = str(uuid.uuid4())
            session = SessionModel(username=data['username'],sid=session_id,status="Active")
            session.save_to_db()
            return {"message" : "User successfully logged in.",
                    "sid" : session_id}, 201

# Resource: Logout User
class Logout(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="Username cannot be blank."
                        )
    parser.add_argument('sid',
                        type=str,
                        required=True,
                        help="sid cannot be blank."
                        )
                        
    # DELETE method: Logout user and blacklist the session
    def delete(self):
        data = Logout.parser.parse_args()
        session = SessionModel.find_by_user_sid_status(
            sid=data['sid'], status='Active', username=data['username'])
        if session == None:
            return {'message': 'No active session found'}, 404
        else:
            session.delete_from_db()
            return {'message': 'User logged out!'}, 200
