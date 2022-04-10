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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

@app.route('/')
def index():
  return 'Welcome to clothing app'

# Product Class/Model
class Product(db.Model):
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

  db.session.add(new_product)
  db.session.commit()

  return product_schema.jsonify(new_product)

# Get All Products
@app.route('/product', methods=['GET'])
def get_products():
  all_products = Product.query.all()
  result = products_schema.dump(all_products)
  return jsonify(result)

# Get Single Products
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
  product = Product.query.get(id)
  return product_schema.jsonify(product)

# Update a Product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
  product = Product.query.get(id)

  name = request.json['name']
  price = request.json['price']
  qty = request.json['qty']

  product.name = name
  product.price = price
  product.qty = qty

  db.session.commit()

  return product_schema.jsonify(product)

# Delete Product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
  product = Product.query.get(id)
  db.session.delete(product)
  db.session.commit()

  return product_schema.jsonify(product)

@app.route('/getholidays/', methods=['GET'])
def getHolidays():
    # Retreive information on public holiday's from the external api
    url = 'https://api.coronavirus.data.gov.uk/generic/announcements'
    with urllib.request.urlopen(url) as response:
        return json.JSONEncoder().encode(json.load(response)), 200

errors = {
    'UserAlreadyExistsError': { 
        'message': 'A user with that username already exists.',
        'status': 409,

    },
    'ResourceDoesNotExist': {
        'message': 'A resource with that ID no longer exists.',
        'status': 410,
        'extra': 'Any extra information you want.',
    },
    'ResourceBaseError': {
        'message': 'Recheck the details again. Name of the item must be unique.',
        'status': 500,
        
    },
    'BadRequestError': {
        'message': 'Missing required parameters.',
        'status': 400,
    },
    

}  

api = Api(app, errors=errors, catch_all_404s=True)

# Run Server
if __name__ == '__main__':
  app.run(debug=True)