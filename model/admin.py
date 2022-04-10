
from db import db

# Database table: admin
class AdminModel(db.Model):
    __tablename__ = 'admin'

    # Declare table columns
    adminid  = db.Column(db.String(40), primary_key=True)

    # Constructor for table instance
    def __init__(self):
        self.adminid = "34fce8e54af2a418da63ce05b265cc8ea98cc1ef"
        self.save_to_db()

    # Method to update data in table
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # Method for getting data from table
    @classmethod
    def get_id(cls):
        return cls.query.filter_by().first().adminid
