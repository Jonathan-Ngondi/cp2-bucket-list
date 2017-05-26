# CP2: Bucketlist_API
 
## Introduction
This app was built using the Flask framework and it allows you to perform simple CRUD operations on a database using api endpoints. A bucketlist is a list of things one would like to accomplish before dying. This app allows a user to add, modify and delete bucketlists of their choosing as well as add, modify, and delete items pertaining to those bucketlists. This project was submitted in partial fulfillment of my Andela fellowship requirements. 
 
## Installation
 
Clone the Bucketlist_api's GitHub repo:
 
http:
>`$ git clone https://github.com/Jonathan-Ngondi/cp2-bucket-list.git`

cd into the created folder and install a [virtual environment](https://virtualenv.pypa.io/en/stable/)

`$ virtualenv venv`

Activate the virtual environment

`$ source venv/bin/activate`

Install all app requirements

`$ pip install -r requirements.txt`

Create the database and run migrations

`$ python manage.py create_db [name]`

To run migrations:
`$ python manage.py db init`

`$ python manage.py db migrate`

`$ python manage.py db upgrade`

Don't forget to set your APP_SETTINGS to set your app configurations, you can choose from:
- development
- testing
- production
- staging
#e.g.
`$ export APP_SETTINGS='development`

All done! Now, start your server by running `python manage.py runserver`. For best experience, use a GUI platform like [postman](https://www.getpostman.com/) to make requests to the api.

### Endpoints

Here is a list of all the endpoints in bucketlist app.

Endpoint | Functionality| Access
------------ | ------------- | ------------- 
POST /app/v1/auth/login |Logs a user in | PUBLIC
POST /app/v1/auth/register | Registers a user | PUBLIC
POST /app/v1/bucketlists/ | Creates a new bucket list | PRIVATE
GET /app/v1/bucketlists/ | Lists all created bucket lists | PRIVATE
GET /app/v1/bucketlists/id | Gets a single bucket list with the suppled id | PRIVATE
PUT /app/v1/bucketlists/id | Updates bucket list with the suppled id | PRIVATE
DELETE /app/v1/bucketlists/id | Deletes bucket list with the suppled id | PRIVATE
POST /app/v1/bucketlists/id/items/ | Creates a new item in bucket list | PRIVATE
PUT /app/v1/bucketlists/id/items/item_id | Updates a bucket list item | PRIVATE
DELETE /app/v1/bucketlists/id/items/item_id | Deletes an item in a bucket list | PRIVATE

### Features:
* Search by name
* Pagination
* Token based authentication
### Searching

It is possible to search bucketlists using the parameter `q` in the GET request. 
Example:

`GET http://localhost:/bucketlists?q=Spirituality`

This request will return all bucketlists named `Spirituality`.

### Pagination

It is possible to limit the count of bucketlist data displayed using the parameter `limit` in the GET request. 

Example:

`GET http://localhost:/api/v1/bucketlists?limit=5`

It is also possible to set the record we would like to start viewing from.

Example:

`GET http://localhost:/api/v1/bucketlists?start=5`

### Sample GET response
After a successful resgistration and login, you will receive an athentication token. Pass this token in your request header.
Below is a sample of a GET request for bucketlist

```
{
  "id": 7,
  "name": "Memorable Experiences",
  "items": [],
  "date_created": "Tue, 23 May 2017 14:48:08 GMT",
  "date_modified": "Tue, 23 May 2017 14:48:08 GMT",
  "created_by": "Janoosh"
}

```

### Testing
The application tests are based on python’s unit testing framework unittest.
To run tests with nose, run `nosetests`

### License
The API uses an MIT license
