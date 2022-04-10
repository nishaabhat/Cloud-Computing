
from flask_restful import Resource, reqparse
from model.titles import TitlesModel
from model.sessions import SessionModel
from model.users import UserModel
from flask import jsonify
import json
import requests
import requests_cache

# Resource: Browse TV titles, calling external API to get title information
class Browse(Resource):

    def get(self, title):
        url_template = "http://api.tvmaze.com/search/shows?q={title}"
        url = url_template.format(title=title)
        resp = requests.get(url)
        if resp.ok:
            if resp.text == "[]":
                return {"message": "Title not found, please check the spellings and separators carefully."}, 404
            return jsonify(resp.json())
        else:
            return {"message": "Title not found"}, 404

# Resource: Add items to user's list
class AddToList(Resource):

    # Define request parameters
    parser = reqparse.RequestParser()

    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    parser.add_argument('sid',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    parser.add_argument('listname',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    parser.add_argument('title',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('remarks',
                        type=str,
                        required=False,
                        help="This field cannot be left blank!"
                        )

    # PUT method for updating the list
    def put(self):
        data = AddToList.parser.parse_args()
        # Check if user session is valid, if user doesn't have a valid active session => Error
        if SessionModel.find_by_user_sid_status(
                username=data['username'],sid=data['sid'],status='Active') == None:
            return {'message': 'Invalid session ID'}, 403

        # Check if list name is valid for the user
        if UserModel.find_by_user_and_list(username=data['username'],listname=data['listname']) == None:
            return {'message': 'Invalid list name for the user'}, 403

        # Add new title to list if title doesn't exit, if exists then return error    
        if TitlesModel.find_by_listname_title(listname=data['listname'], title=data['title']) == None:
            item = TitlesModel(listname = data["listname"], title = data["title"], remarks = data["remarks"])
            item.save_to_db()
            return {'message': 'Title added successfully'}, 201
        else:
            return {"message" : "Title already exists" }, 403    

# Resource: Delete items from user's list
class DeleteFromList(Resource):

    # Define request parameters
    parser = reqparse.RequestParser()

    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('sid',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('listname',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    parser.add_argument('title',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    # DELETE method for deleting titles from list
    def delete(self):
        data = DeleteFromList.parser.parse_args()

        # Check if user session is valid, if user doesn't have a valid active session => Error
        if SessionModel.find_by_user_sid_status(
                username=data['username'],sid=data['sid'],status='Active') == None:
            return {'message': 'Invalid session ID'}, 403

        # Check if list name is valid for the user
        if UserModel.find_by_user_and_list(username=data['username'],listname=data['listname']) == None:
            return {'message': 'Invalid list name for the user'}, 403

        # Check if title to be deleted exists, if not then return error
        if TitlesModel.find_by_listname_title(listname=data['listname'],title=data['title']) == None:
            return {'message': 'The requested title does not exist in the list'}, 404

        # Title found, Delete title from list
        title = TitlesModel.find_by_listname_title(listname = data['listname'], title= data['title'])
        title.delete_from_db()
        return {'message': 'Title has been deleted from the list'}, 200
   
# Resource: View iser's list   
class ViewList(Resource):
    # Define request parameters
    parser = reqparse.RequestParser()

    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    parser.add_argument('sid',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    parser.add_argument('listname',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    # GET method for retrieving user's list
    def get(self):
        data = ViewList.parser.parse_args()
        # Check if user session is valid, if user doesn't have a valid active session => Error
        if SessionModel.find_by_user_sid_status(
                username=data['username'],sid=data['sid'],status='Active') == None:
            return {'message': 'Invalid session ID'}, 403

        # Check if list name is valid for the user
        if UserModel.find_by_user_and_list(username=data['username'],listname=data['listname']) == None:
            return {'message': 'Invalid list name for the user'}, 403    

        # Return all titles
        return {'titles': [x.json() for x in TitlesModel.find_by_listname_all(listname=data['listname'])]}, 200