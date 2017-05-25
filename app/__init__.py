from flask import Flask, Blueprint, jsonify, request, render_template
from flask_paginate import Pagination
from flask_sqlalchemy import SQLAlchemy
from instance.config import app_config
import json
import jwt


db = SQLAlchemy()



def create_app(config_name):
    from app.v1.models import User, Bucketlist, Items
    app = Flask(__name__)
    api = Blueprint('api',__name__)
    app.config.from_object(app_config[config_name])
    app.register_blueprint(api, url_prefix='/api/v1.0')
    app.config['JSON_SORT_KEYS'] = False
    secret = app.config['SECRET_KEY']
    db.init_app(app)
    with app.app_context():
         db.create_all()

    @app.route('/', methods=['GET'])
    def homepage():
        """Greets user with a message"""
        return jsonify({'Message':'Welcome to BucketlistAPI'})

    @app.route('/api/v1/auth/register', methods=['POST'])
    def register_user():
            """Registers a user and saves them to the database."""
            request.get_json(force=True)
            username = request.json['username']
            email = request.json['email']
            password1 = request.json['password1']
            password2 = request.json['password2']
            check = User.query.filter_by(username=username)
            check_list = [user.username for user in check]
            if check_list != []:
                return jsonify({"message":"That username already exists."}), 409
            if not str(username).isalpha():
                return jsonify({"message": "That is an invalid username"})

            if password1 == password2 and check_list == []:
                new_user = {'username': username, 'password':password1,'email': email}
                newUser = User(username=username, password=User.hash_password(password1), email=email)
                newUser.save()
                
                return jsonify({'message': 'User {} has been successfully created'.format(username)}), 201
            else:
                return jsonify({'message': "Your passwords don't match."}), 400

    @app.route('/api/v1/auth/login', methods=['POST'])
    def login_user():
        """Allows user to login and returns a token value."""
        request.get_json(force=True)
        username = request.json['username']
        password = request.json['password']
        query = User.query.filter_by(username=username)
        user = [{'username':user.username, 'password':user.password} for user in query]

        if User.check_password(user[0]['password'], password) and user != []:
            json_data = {'username':username, 'password': password}
            token = jwt.encode(json_data, secret, algorithm='HS256')

            return jsonify({'User': user[0], 'token': str(token)}), 200

        else:
            return jsonify({'message':'There was a problem with the username or password.'}), 400


    @app.route('/api/v1/bucketlists', methods=['GET'])
    def view():
    	return jsonify(get_all_bucketlists(
		Bucketlist, 
		'/api/v1/bucketlists', 
		start=int(request.args.get('start', 1)), 
		limit=int(request.args.get('limit', 5)),
        q=str(request.args.get('q',''))
	)), 200


    def get_all_bucketlists(Class,url, start, limit,    q):
        """Get's all the bucketlists for a user and displays their info."""
        auth = User.verify_token(secret)
        if type(auth) is json:
            return auth
        else:
            user_query = User.query.filter_by(username=auth['username'])
            user = [user for user in user_query]    
            bucketlist_query = Bucketlist.query.filter_by(created_by=user[0].id)
            bucketlists = [bucketlist for bucketlist in bucketlist_query]
            count = len(bucketlists)
            obj = {}
            obj['q'] = q
            obj['start'] = start
            obj['limit'] = limit
            obj['count'] = count

            if q == '':
                #Make the 'previous' url
                if start == 1:
                    obj['previous'] = ''
                else:
                    start_text = max(1, start-limit)
                    limit_text = start - 1
                    obj['previous'] = url + '?start={}&limit={}'.format(start_text, limit_text)

                #Make the 'next' url
                if start + limit > count:
                    obj['next'] = ''
                else:
                    start_text = start + limit
                    obj['next'] = url + '?start={}&limit={}'.format(start_text, limit)
                
                bucketlists_paginated = bucketlists[(start -1):(start -1 + limit)]
                item_query = Items.query.filter_by(bucketlist_id=id)
                obj_results = []
                for bucketlist in bucketlists_paginated:
                    item_query = Items.query.filter_by(bucketlist_id=bucketlist.id_key)
                    results = {'id': bucketlist.id_key,
                                    'name':bucketlist.name,
                                    'items': item_query.count(),
                                    'date_created': bucketlist.date_created,
                                    'date_modified': bucketlist.date_modified,
                                    'created_by': user[0].username
                                    }
                    obj_results.append(results)
                
                obj['results'] = obj_results
            
            else:
                try:
                    bucketlist_query_q = Bucketlist.query.filter_by(name=q)
                    bucketlist_q = [bucketlist for bucketlist in bucketlist_query_q]
                    item_query_q = Items.query.filter_by(bucketlist_id=bucketlist_q[0].id_key)
                    item_q = [items for items in item_query_q]
                    results = {'id': bucketlist_q[0].id_key,
                                        'name':bucketlist_q[0].name,
                                        'items': [{          
                                                'id': item.id,
                                                'name': item.name,
                                                'date_created': item.date_created,
                                                'date_modified': item.date_modified
                                    
                                    } for item in item_q],
                                        'date_created': bucketlist_q[0].date_created,
                                        'date_modified': bucketlist_q[0].date_modified,
                                        'created_by': user[0].username
                                        }
                    obj['results'] = results
                    obj['count'] = 1
                    obj['start'] = 1
                    obj['limit'] = 1
                except IndexError:
                    return {"Error":"There is no bucketlist by that name"}
            
            return obj

    @app.route('/api/v1/bucketlists', methods=['POST'])
    def add_bucketlist():
        """Adds a user's bucketlist to the database."""
        request.get_json(force=True)
        auth = User.verify_token(secret)

        if type(auth) is json:
            return auth
        else:
            try:
                user_query = User.query.filter_by(username=auth['username'])
                user = [user for user in user_query]
                new_bucketlist = Bucketlist(name=request.json['name'], created_by=user[0].id)
                new_bucketlist.save()
                bucketlist_query = Bucketlist.query.filter_by(created_by=user[0].id)
                bucketlists = [bucketlist.name for bucketlist in bucketlist_query]

                return jsonify({'Bucketlists': bucketlists}), 201
            except:
                
                return jsonify({"Message":"Please user the format {'name':'String'} to add a bucketlist."}), 400 
        
    @app.route('/api/v1/bucketlists/<int:id>', methods=['PUT'])
    def modify_bucketlist(id):
        """Allows the user to modify a bucketlist, and saves to the database."""
        request.get_json(force=True)
        auth = User.verify_token(secret)
        if type(auth) is json:
            return auth
        else:
            try:
                user_query = User.query.filter_by(username=auth['username'])
                user = [user for user in user_query]
                bucketlist_query = Bucketlist.query.filter_by(id_key=id)
                bucketlist = [bucketlist for bucketlist in bucketlist_query]
                bucketlist[0].name = request.json['name']
                bucketlist[0].save()
                all_bucketlists_query = Bucketlist.query.filter_by(created_by=user[0].id)
                bucketlists = [bucketlist.name for bucketlist in bucketlist_query]

                return jsonify({'bucketlist': bucketlists}), 201
            except IndexError:
                return jsonify({"Message":"That bucketlist id does not exist, please try again."}), 400

    @app.route('/api/v1/bucketlists/<int:id>', methods= ['DELETE'])
    def delete_bucketlist(id):
        """Delete's a user's bucketlist from the database."""
        auth = User.verify_token(secret)
        if type(auth) is json:
            return auth
        else:
            
            try: 
                bucketlist_query = Bucketlist.query.filter_by(id_key=id)
                bucketlist = [bucketlist for bucketlist in bucketlist_query]
                bucketlist_name = bucketlist[0].name
                items_query = Items.query.filter_by(bucketlist_id=id)
                for item in items_query:
                    item.delete()
                
                bucketlist[0].delete()
                

                return jsonify({"message":"You're bucketlist {} has been successfully deleted".format(bucketlist_name)})
            
            except IndexError:
                return jsonify({"Message":"That bucketlist id does not exist, please try again."}), 404

    @app.route('/api/v1/bucketlists/<int:id>', methods=['GET'])
    def get_bucketlist_by_id(id):
        """Get's a bucketlist by id and returns the values."""
        auth = User.verify_token(secret)
        if type(auth) is json:
            return auth
        else:
            try:
                user_query = User.query.filter_by(username=auth['username'])
                user = [user for user in user_query] 
                bucketlist_query = Bucketlist.query.filter_by(id_key=id)
                bucketlist = [bucketlist for bucketlist in bucketlist_query]
                item_query = Items.query.filter_by(bucketlist_id=id)
                results = {'id': bucketlist[0].id_key,
                                'name':bucketlist[0].name,
                                'items': [{          
                                            'id': item.id,
                                            'name': item.name,
                                            'date_created': item.date_created,
                                            'date_modified': item.date_modified
                                
                                } for item in item_query],
                                'date_created': bucketlist[0].date_created,
                                'date_modified': bucketlist[0].date_modified,
                                'created_by': user[0].username
                                }
                return jsonify(results), 200
            except IndexError:
                return jsonify({"Error":"This page doesn't exist"}), 404



    @app.route('/api/v1/bucketlists/<int:id>/items', methods=['POST'])
    def create_bucketlist_item(id):
        """
        Allows you to create a bucketlist item via a bucketlist id and save it to the db.
        """
        request.get_json(force=True)
        auth = User.verify_token(secret)
        if type(auth) is json:
            return auth
        else:
            try:
                bucketlist_query = Bucketlist.query.filter_by(id_key=id) 
                bucketlist = [bucketlist for bucketlist in bucketlist_query]
                new_item = Items(name=request.json['bucketlist_item'], bucketlist_id=bucketlist[0].id_key)
                new_item.save()
                item_query = Items.query.filter_by(bucketlist_id=id)
                items = [item.name for item in item_query]

                return jsonify({bucketlist[0].name : items}), 201
            except IndexError:
                return jsonify({"Message":"That bucketlist id does not exist, please try again."}), 400

        
    @app.route('/api/v1/bucketlists/<int:id>/items/<item_id>', methods=['PUT'])
    def modify_bucketlist_item(id, item_id):
        """
        Allows you to modify a bucketlist item by bucketlist id as well as item id and save to
        the db.
        """
        request.get_json(force=True)
        auth = User.verify_token(secret)
        if type(auth) is json:
            return auth
        else:
            bucketlist_query = Bucketlist.query.filter_by(id_key=id)
            bucketlist = [bucketlist for bucketlist in bucketlist_query]
            item_query = Items.query.filter_by(id=item_id)
            item = [item for item in item_query]
            item[0].name = request.json['bucketlist_item']
            item[0].save()
            new_item_query = Items.query.filter_by(id=item_id)
            new_item = [item.name for item in item_query]
        
            return jsonify({bucketlist[0].name: new_item}), 201

    @app.route('/api/v1/bucketlists/<id>/items/<item_id>', methods=['DELETE'])
    def delete_bucketlist_item(id, item_id):
        """
        Deletes a bucketlist item by taking in the bucketlist id as well as the item id.
        """
        auth = User.verify_token(secret)
        if type(auth) is json:
            return auth
        else:
            bucketlist_query = Bucketlist.query.filter_by(id_key=id)
            bucketlist = [bucketlist for bucketlist in bucketlist_query]
            item_query = Items.query.filter_by(id=item_id)
            item = [item for item in item_query]
            item[0].delete()

            return jsonify\
            ({"Message": "{} has been deleted from {}."\
                                .format(item[0].name, bucketlist[0].name)})

    @app.errorhandler(400)
    def bad_request(error):
        """
        Error Handling for status code 400.
        """
        return jsonify({'Error': "We don't know what happened.?!"}), 400



    return app

