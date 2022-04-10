
from db import db
from model.admin import AdminModel
import hashlib
from werkzeug.security import safe_str_cmp

# Database table: users
class UserModel(db.Model):
    __tablename__ = 'users'

    # Declare table columns
    username  = db.Column(db.String(20), primary_key=True)
    password  = db.Column(db.String(40))    
    firstname = db.Column(db.String(30))
    lastname  = db.Column(db.String(30))
    country   = db.Column(db.String(20))
    listname  = db.Column(db.String(20))
    role      = db.Column(db.String(10))

    # Constructor for table instance
    def __init__(self, username, password=None, firstname=None, 
                    lastname=None, country=None, listname=None, role=None, adminkey=None):
        self.username  = username
        self.password  = password
        self.firstname = firstname
        self.lastname  = lastname
        self.country   = country
        self.listname  = listname
        self.role      = role
        self.admincode = ""

    # Internal method to save data in table
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # Internal method to update data in table
    def update_db(self):
        db.session.update(self)
        db.session.commit()

    # Internal method to delete data from table
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()    

    # Static methods - to be used by external methods as interfaces for database queries
    @classmethod
    def find_by_username(cls,username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_user_and_list(cls,username,listname):
        return cls.query.filter_by(username=username,listname=listname).first()

    @classmethod    
    def check_admin_code(cls,admincodein):
        o_hash = hashlib.new('ripemd160')
        o_hash.update(admincodein.encode("utf-8"))
        if safe_str_cmp(AdminModel.get_id(), o_hash.hexdigest()) == True:    
            return True
        else:
            return False       

    @classmethod
    def find_by_user_and_role(cls,username,role):
        return cls.query.filter_by(username=username,role=role).first()
