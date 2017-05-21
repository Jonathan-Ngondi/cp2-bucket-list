import os
from app import create_app
from app.models import User, Bucketlist, Items
from flask import Flask, jsonify, request, make_response
from flask_bcrypt import Bcrypt
import jwt
import json 

app = create_app('development')

users = [{'username': 'MenesRa', 'password':'password123', 'email': 'menes@gmail.com'},\
         {'username':'Janoosh','password':'password123', 'email': 'janoosh@gmail.com'},\
         {'username':'JKamau','password': 'password123', 'email': 'JK@gmail.com'}]
bucketlists = [{'id': 1,'bucketlist':['Go skydiving','Visit the Far East']},\
            {'id': 2, 'bucketlist': ['See the Taj Mahal','Visit South America','Visit Egypt']},\
            {'id': 3, 'bucketlist':['Do works of charity','See my children grow']}]
secret = app.config['SECRET_KEY']

@app.route('/', methods=['GET'])
def homepage():
    return jsonify({'Message':'Welcome to BucketlistAPI'})

@app.route('/auth/register', methods=['POST'])
def register_user():
        
        username = request.json['username']
        email = request.json['email']
        password1 = request.json['password1']
        password2 = request.json['password2']
        check = User.query.filter_by(username=username)
        check_list = [user.username for user in check]
        if not str(username).isalpha():
            return jsonify({"message": "That is an invalid username"})
        if password1 == password2 and check_list == []:
            new_user = {'username': username, 'password':password1,'email': email}
            newUser = User(username=username, password=User.hash_password(password1), email=email)
            newUser.save()
            import pdb;pdb.set_trace()
            return jsonify({'message': 'User {} has been successfully created'.format(username)}), 201
        else:
            return jsonify({'message': 'That username already exists'}), 

@app.route('/auth/login', methods=['POST'])
def login_user():
    
    username = request.json['username']
    password = request.json['password']
    query = User.query.filter_by(username=username)
    user = [{'username':user.username, 'password':user.password} for user in query]
    
    if User.check_password(user[0]['password'], password) and user != []:
        json_data = {'username':username, 'password': password}
        import pdb; pdb.set_trace()
        token = jwt.encode(json_data, secret, algorithm='HS256')
        return jsonify({'User': user[0], 'token': token})
    else:
        return jsonify({'message':'There was a problem with login.'})


@app.route('/bucketlists', methods=['GET'])
def get_all_bucketlists():
    auth = Bucketlist.verify_token(secret)
    if type(auth) is json:
        return auth
    else:
        user_query = User.query.filter_by(username=auth['username'])
        user = [user for user in user_query]
        bucketlist_query = Bucketlist.query.filter_by(created_by=user[0].id)
        bucketlists = [bucketlist.name for bucketlist in bucketlist_query]

        return jsonify({'Bucketlists': bucketlists})

@app.route('/bucketlists', methods=['POST'])
def add_bucketlist():
    auth = Bucketlist.verify_token(secret)
    if type(auth) is json:
        return auth
    else:
        user_query = User.query.filter_by(username=auth['username'])
        user = [user for user in user_query]
        new_bucketlist = Bucketlist(name=request.json['name'], created_by=user[0].id)
        new_bucketlist.save()
        bucketlist_query = Bucketlist.query.filter_by(created_by=user[0].id)
        bucketlists = [bucketlist.name for bucketlist in bucketlist_query]
        import pdb;pdb.set_trace()
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
    return jsonify({'Error': "We don't know what happeneed.?!"})

# @app.errorhandler(401)
# def unathorized(error):
#     return jsonify({'Error':"You don't have permission to acces this resource"})
    



if __name__ == '__main__':
    app.run()
