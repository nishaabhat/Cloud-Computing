from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os
import json, io
import urllib.request, urllib.response
import hashlib

# Init app
app = Flask(__name__)
app.secret_key = 'CC-GP12'
#basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Password123@database-1.cmdfiwgzwnsx.us-east-1.rds.amazonaws.com:5432/postgres'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

#Defining user
class User(db.Model):
    #declaring variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(80))
    userpassword = db.Column(db.String())

    #constructor for table instance
    def __init__(self, username, email, userpassword):
      self.username = username
      self.email = email
      self.userpassword = userpassword
 
# User Schema
class UserSchema(ma.Schema):
  class Meta:
    fields = ('username', 'email', 'userpassword')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

#add new user
@app.route('/adduser', methods=['POST'])
def add_user():
  username = request.json['username']
  email = request.json['email']
  userpassword = request.json['userpassword']
  existing_user = User.query.filter_by(username=username).first()
  if existing_user:
    return {"message": "User already exists"}, 403
  #hashing the password
  o_hash = hashlib.new('ripemd160')
  o_hash.update(userpassword.encode("utf-8"))
  userpassword = o_hash.hexdigest() 
  new_user = User(username, email, userpassword)
  #writing to database
  db.session.add(new_user)
  db.session.commit()
  return user_schema.jsonify(new_user), 200

#method to get all users
@app.route('/getusers', methods=['GET'])
def get_user():
  all_users = User.query.all()
  result_users = users_schema.dump(all_users)
  return jsonify(result_users), 200

#method to authenticate user based on hashed password
@app.route('/authenticate', methods = ['POST'])
def authenticate():
  username = request.json['username']
  userpassword = request.json['userpassword']

  #hash the password received
  o_hash = hashlib.new('ripemd160')
  o_hash.update(userpassword.encode("utf-8"))
  fetchpassword = o_hash.hexdigest()

  user = User.query.filter_by(username = username).first()
  #check if the password matches
  if user is not None and user.userpassword == fetchpassword:
    return 'Password matches. User '+username+' authenticated.', 200
  else:
    return 'Username or password incorrect!!', 403

# Product Class/Model
class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), unique=True)
  description = db.Column(db.String(200))
  price = db.Column(db.Float)
  qty = db.Column(db.Integer)

  #constructor for table instance
  def __init__(self, name, description, price, qty):
    self.name = name
    self.description = description
    self.price = price
    self.qty = qty

# Product Schema
class ProductSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'description', 'price', 'qty')

# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a Product
@app.route('/addproduct', methods=['POST'])
def add_product():
  name = request.json['name']
  description = request.json['description']
  price = request.json['price']
  qty = request.json['qty']

  existing_product = Product.query.filter_by(name=name).first()
  if existing_product:
    return {"message": "Product already exists"}, 403

  new_product = Product(name, description, price, qty)

  db.session.add(new_product)
  db.session.commit()

  return product_schema.jsonify(new_product), 200

# Get All Products
@app.route('/getproduct', methods=['GET'])
def get_products():
  all_products = Product.query.all()
  if all_products is None:
    return {"message": "No products available"}, 200
  result = products_schema.dump(all_products)
  return jsonify(result), 200

# Get Single Products
@app.route('/getproduct/<id>', methods=['GET'])
def get_product(id):
  product = Product.query.get(id)
  if product == None:
    return {"message": "Product doesn't exist exists"}, 403
  else:
    return product_schema.jsonify(product), 200

# Update a Product
@app.route('/updateproduct/<id>', methods=['PUT'])
def update_product(id):
  product = Product.query.get(id)
  if product == None:
    return {"message": "Product doesn't exist exists"}, 403
  else:
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']
    product.name = name
    product.description = description
    product.price = price
    product.qty = qty
    db.session.commit()
    return product_schema.jsonify(product), 200

# Delete Product
@app.route('/deleteproduct/<id>', methods=['DELETE'])
def delete_product(id):
  product = Product.query.get(id)
  if product == None:
    return {"message": "Product doesn't exist exists"}, 403
  else:
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)

@app.route('/COVIDAnnouncements', methods=['GET'])
def getAnnouncements():
    # 
    url = 'https://api.coronavirus.data.gov.uk/generic/announcements'
    with urllib.request.urlopen(url) as response:
        return json.JSONEncoder().encode(json.load(response)), 200

# Run Server
if __name__ == '__main__':
  db.create_all()
  app.run(debug=True, host='0.0.0.0')