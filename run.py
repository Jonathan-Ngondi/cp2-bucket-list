import os
from app import create_app
from app.models import User, Bucketlist
from flask import Flask, jsonify, request, make_response
from flask_bcrypt import Bcrypt
import jwt
import json 
# config_name = os.getenv('APP_SETTINGS') # config_name = "development"
# app = create_app(config_name)

app = Flask(__name__)

users = [{'username': 'MenesRa', 'password':'password123', 'email': 'menes@gmail.com'},\
         {'username':'Janoosh','password':'password123', 'email': 'janoosh@gmail.com'},\
         {'username':'JKamau','password': 'password123', 'email': 'JK@gmail.com'}]
bucketlists = [{'id': 1,'bucketlist':['Go skydiving','Visit the Far East']},\
            {'id': 2, 'bucketlist': ['See the Taj Mahal','Visit South America','Visit Egypt']},\
            {'id': 3, 'bucketlist':['Do works of charity','See my children grow']}]
secret = os.getenv('SECRET')

@app.route('/', methods=['GET'])
def homepage():
    return jsonify({'Message':'Welcome to BucketlistAPI'})

@app.route('/bucketlists', methods=['GET'])
def get_all_bucketlists():
    
    #Should get from database here
    return jsonify({'Bucketlists': bucketlists})

@app.route('/bucketlists/<int:id>', methods=['GET'])
def get_bucketlist_by_id(id):
    #Should get from database here and apply logic
    bucketlist = [bucketlist for bucketlist in bucketlists if bucketlist['id'] == id]
    return jsonify({'Bucketlists': bucketlist[0]})

@app.route('/bucketlists/<int:id>/items', methods=['POST'])
def create_bucketlist_item(id):
    #Should ensure that bucketlists is a gotten from the db
    bucketlist_item = request.json['bucketlist_item']
    bucketlist = [bucketlist for bucketlist in bucketlists if bucketlist['id'] == id]
    bucketlist[0]['bucketlist'].append(bucketlist_item)
    return jsonify({'Bucketlists': bucketlists})

@app.route('/bucketlists/<int:id>/items/<item_id>', methods=['PUT'])
def modify_bucketlist_item(id, item_id):
    bucketlist_item = request.json['bucketlist_item']
    bucketlist = [bucketlist for bucketlist in bucketlists if bucketlist['id']== id]
    bucketlist[0]['bucketlist'][int(item_id)] = bucketlist_item
    return jsonify({'Bucketlists': bucketlists})

@app.errorhandler(400)
def bad_request(error):
    return make_response({'Error': "We don't know what happeneed.?!"})
    
@app.route('/bucketlists', methods=['POST'])
def add_bucketlist():
    #Should insert into database here

    bucketlist = {'id': len(bucketlists) + 1, 'bucketlist': request.json['bucketlist']}
    bucketlists.append(bucketlist)
    return jsonify({'Bucketlists': bucketlists})
    
@app.route('/bucketlists/<int:id>', methods=['PUT'])
def modify_bucketlist(id):
    #Should find the item in db by id
    bucketlist = [bucketlist for bucketlist in bucketlists if bucketlist['id'] == id]
    bucketlist[0]['bucketlist'] = request.json['bucketlist']
    return jsonify({'bucketlist': bucketlist[0]})

@app.route('/bucketlists/<int:id>', methods= ['DELETE'])
def delete_bucketlist(id):
    #Should find the id in the database
    bucketlist = [bucketlist for bucketlist in bucketlists if bucketlist['id'] == id]
    bucketlists.remove(bucketlist[0])
    return jsonify({'Bucketlists': bucketlists})

@app.route('/auth/login', methods=['POST'])
def login_user():
    #Should connect to db and bcrypt password
    username = request.json['username']
    password = request.json['password']
    user = [user for user in users if user['username'] == username and user['password'] == password]
    if user != []:
        user_json = json.dumps(user[0])
        token = jwt.encode(user_json, secret)
        return jsonify({'User': user[0], 'token': token})
    else:
        return jsonify({'message':'There was a problem with login.'})

@app.route('/auth/register', methods=['POST'])
def register_user():
    #Should connect to db and insert user details.
        username = request.json['username']
        email = request.json['email']
        password1 = request.json['password1']
        password2 = request.json['password2']
        if not str(username).isalpha():
            return jsonify({"message": "That is an invalid username"})
        if password1 == password2:
            new_user = {'username': username, 'password':password1,'email': email}
            users.append(new_user)
            return jsonify({'message': 'User {} has been successfully created'.format(username)})

if __name__ == '__main__':
    app.run()
