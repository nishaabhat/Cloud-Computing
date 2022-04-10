from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os
from flask_restful import Api
import urllib.request, urllib.response
import datetime
import json, io

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
db_url = os.environ.get('DATABASE_URL')                                   # For Heroku, comment for local execution 
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("://", "ql://", 1) # For Heroku, comment for local execution
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'             # For Local, comment for Heroku execution  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


@app.route('/')
def index():
  return 'Welcome to clothing app', 200

# Product Class/Model
class Product(db.Model):
  __tablename__ = 'apparel'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), unique=True)
  price = db.Column(db.Float)
  qty = db.Column(db.Integer)

  def __init__(self, name, price, qty):
    self.name = name
    self.price = price
    self.qty = qty

# Product Schema
class ProductSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'price', 'qty')

# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a Product
@app.route('/product', methods=['POST'])
def add_product():
  name = request.json['name']
  price = request.json['price']
  qty = request.json['qty']
  new_product = Product(name, price, qty)
  
  existing_name = Product.query.filter_by(name=name).first()
  if existing_name:
      return {"message": "This apparel already exists"}, 403

  db.session.add(new_product)
  db.session.commit()

  return product_schema.jsonify(new_product)

# Get All Products
@app.route('/product', methods=['GET'])
def get_products():
  all_products = Product.query.all()
  result = products_schema.dump(all_products)
  return jsonify(result), 200

# Get Single Products
@app.route('/product/<name>', methods=['GET'])
def get_product(name):
  product = Product.query.get(name)
  if product is None:
      return {"message": "This apparel doesn't exist. Please recheck apparel name."}, 403  
  return product_schema.jsonify(product), 200

# Update a Product
@app.route('/product/<name>', methods=['PUT'])
def update_product(name):
  product = Product.query.get(name)
  name = request.json['name']
  price = request.json['price']
  qty = request.json['qty']
  product.name = name
  product.price = price
  product.qty = qty
  if product is None:
      return {"message": "This apparel doesn't exist. Please recheck apparel name."}, 403  
  db.session.commit()

  return product_schema.jsonify(product), 200

# Delete Product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
  product = Product.query.get(id)
  db.session.delete(product)
  db.session.commit()

  return product_schema.jsonify(product), 200

@app.route('/COVIDAnnouncements/', methods=['GET'])
def getAnnouncements():
    # 
    url = 'https://api.coronavirus.data.gov.uk/generic/announcements'
    with urllib.request.urlopen(url) as response:
        return json.JSONEncoder().encode(json.load(response)), 200

class AdminModel(db.Model):
    __tablename__ = 'admin'

    # Declare table columns
    adminid  = db.Column(db.String(40), primary_key=True)

    # Constructor for table instance
    def __init__(self):
        self.adminid = "34fce8e54af2a418da63ce05b265cc8ea98cc1ef"
        self.save_to_db()

# Run Server
if __name__ == '__main__':
        if app.config['DEBUG']:
            @app.before_first_request
            def create_tables():
                AdminModel()
                db.create_all()
                AdminModel().save_to_db()
        app.run(debug=True)