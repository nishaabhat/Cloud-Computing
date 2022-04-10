
from db import db
from model.users import UserModel

# Database table: sessions
class SessionModel(db.Model):
    __tablename__ = 'sessions'

    # Declare table columns
    username  = db.Column(db.String(20),db.ForeignKey(UserModel.username),primary_key=True)
    sid = db.Column(db.String(36), primary_key=True)
    status = db.Column(db.String(10))

    # Constructor for table instance
    def __init__(self, username, sid, status):
        self.username  = username
        self.sid = sid
        self.status = status

    # Method for json response
    def json(self):
        return {'sid': self.sid}

    # Internal Method to update data in table
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # Internal method to delete data from table
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    # Static methods - to be used by external methods as interfaces for database queries
    @classmethod
    def find_by_sid(cls, sid):
        return cls.query.filter_by(sid=sid).first()

    @classmethod
    def find_by_user_sid(cls, username, sid):
        return cls.query.filter_by(username=username,sid=sid).first()

    @classmethod
    def find_by_user_sid_status(cls, username, sid, status):
        return cls.query.filter_by(username = username, sid = sid, status = status).first()        
    
    @classmethod
    def find_by_user(cls,username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def delete_user_all(cls,username):
        list_sessions = cls.query.filter_by(username = username).all()
        for i in list_sessions:
            # print("deleting: ",i)
            i.delete_from_db()

