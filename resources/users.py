import sqlite3
from flask_restful import Resource, reqparse
from model.users import UserModel
from model.titles import TitlesModel
from model.sessions import SessionModel
import hashlib

# Resource: User Registration / Sign up
class UserRegister(Resource):

#   Define request attributes for new user signup
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
    parser.add_argument('firstname',
        type=str,
        required=False,
        help="First Name."
    )
    parser.add_argument('lastname',
        type=str,
        required=False,
        help="Last Name."
    )
    parser.add_argument('country',
        type=str,
        required=False,
        help="Country"
    )        
    parser.add_argument('listname',
        type=str,
        required=True,
        help="ListName field cannot be blank."
    )    
    parser.add_argument('role',
        type=str,
        required=True,
        help="Role of the user cannot be blank (must be user or admin)."   
    )     
    parser.add_argument('adminkey',
        type=str,
        required=False,
        help="Admin key if the role is admin."          
    )      

#   Post method to create new user
    def post(self):
        data = UserRegister.parser.parse_args()

#       Check if user name is already present
        if UserModel.find_by_username(data['username']):
            return {"message": "A user with the given username already exists"}, 403

        # Check if list name is already present
        if TitlesModel.find_by_listname(listname=data['listname']):
            return{"message" : "A list already exists with this name, please select a different list name."}, 403
            
    #   Check if correct admin key is supplied for admin role 
        if data["role"] == "admin":
            if data["adminkey"] == None:
                return{"Message" : "No admin code supplied for the admin"}, 401
            if UserModel.check_admin_code(data["adminkey"]) == False:
                return{"Message" : "Invalid admin code"}, 401

#       Hash password before saving to DB    
        o_hash = hashlib.new('ripemd160')
        o_hash.update(data["password"].encode("utf-8"))
        data["password"] = o_hash.hexdigest() 

    #   Save new user to DB
        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201

# Resource: User Deletion / Sign up
class UserDelete(Resource):

#   Define request attributes for new user signup
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('username',
        type=str,
        required=True,
        help="Username cannot be blank."
    )
    parser.add_argument('sid',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('user_to_delete',
        type=str,
        required=True,
        help="User to be deleted must be specified."
    )

#   Delete method to delete a user and all its data (can be called by admin only)
    def delete(self):
        data = UserDelete.parser.parse_args()

        # Check if user session is valid, if user doesn't have a valid active session => Error
        if SessionModel.find_by_user_sid_status(
                username=data['username'],sid=data['sid'],status='Active') == None:
            return {'message': 'Invalid session ID'}, 403

#       Check if user name is an admin
        if UserModel.find_by_user_and_role(username=data['username'],role="admin") == None:
            return {"message": "No authorization to delete users"}, 401

#       Check if user to be deleted is present   
        if UserModel.find_by_username(data['user_to_delete']) == None:
            return {"message": "User to be deleted does not exist"}, 404
        
        # User instance
        user = UserModel.find_by_username(username=data['user_to_delete'])
        
#       Delete user data from all database tables        
        # Titles table
        titles = TitlesModel.find_by_listname(listname=user.listname)
        if titles != None:
            TitlesModel.delete_titles_all(listname=titles.listname)

        # Session table
        sessions = SessionModel.find_by_user(username=user.username)
        if sessions != None:
            SessionModel.delete_user_all(username=data['user_to_delete'])
            
        # User table
        user.delete_from_db()            

        return {"message": "User deleted successfully."}, 200
