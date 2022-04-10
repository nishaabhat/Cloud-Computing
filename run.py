from app import app
from db import db

db.init_app(app)

@app.before_first_request
def create_tables():
    from models.admin import AdminModel
    db.create_all()
    # if AdminModel.get_id() == None:  #Required for initial heroku deploymenyt, commented after that
        # AdminModel().save_to_db()    #Required for initial heroku deploymenyt, commented after that
