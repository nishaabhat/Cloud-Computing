from db import db
from model.users import UserModel

# Database table: titles
class TitlesModel(db.Model):
    __tablename__ = 'titles'

    # Declare table columns
    listname = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(50), primary_key=True)
    remarks = db.Column(db.String(80))

    # Constructor for table instance
    def __init__(self, listname, title, remarks=None):
        self.listname = listname
        self.title = title
        self.remarks = remarks

    # Internal method to update data in table
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()        

    # Internal method to delete data from table
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    # Method for returning json response
    def json(self):
        return {'title': self.title}

    # Static methods - to be used by external methods as interfaces for database queries
    @classmethod
    def find_by_listname(cls,listname):
        return cls.query.filter_by(listname=listname).first()

    @classmethod
    def find_by_listname_all(cls,listname):
        return cls.query.filter_by(listname=listname).all()        

    @classmethod
    def find_by_listname_title(cls,listname, title):
        return cls.query.filter_by(listname=listname, title = title).first()        

    @classmethod
    def delete_titles_all(cls,listname):
        list_titles = cls.query.filter_by(listname = listname).all()
        # print("Mehtod in title resource, list values: ",list_titles, "lsitname:", listname)
        for i in list_titles:
            # print("Deleting: ", i)
            i.delete_from_db()