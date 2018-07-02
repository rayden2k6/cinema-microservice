from init_service import root_dir, nice_json
from flask import Flask,request,abort,render_template
from werkzeug.exceptions import NotFound, ServiceUnavailable
import json
import requests
from flask_sqlalchemy import SQLAlchemy
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def get_users():
	response_object = dict()
	users = Users.query.all()
	for user in users:
		response_object[user.user_id] = {
			'id': user.user_id,
			'name': user.name,
			'last_active': user.last_active
		}
	return response_object

def get_user_by_id(_id):
	return get_users()[_id]

def create_user(_id,_name):
	user = Users(user_id=_id,name=_name,last_active=int(time.time()))
	db.session.add(user)
	db.session.commit()
	return get_users()

def delete_user(_id):
	user = Users.query.get(_id)
	db.session.delete(user)
	db.session.commit()
	return get_users()

def fillsqlitetable():
	users = Users.query.all()
	for user in users:
		db.session.delete(user)
	db.session.commit()
	jsondb = json.load(open('../database/users.json','r'))
	for key in jsondb.keys():
		user = Users(user_id=key,name=jsondb[key]['name'],last_active=jsondb[key]['last_active'])
		db.session.add(user)
	db.session.commit()
	return get_users()

def obtain_user_statuses():
    users = Users.query.all()
    res = dict()
    for user in users:
        user_booking = requests.get("http://localhost:5003/bookings/{}".format(user.user_id))
        user_booking = user_booking.json()
        if not 'message' in user_booking.iterkeys():
            user_detail = {
                'username': user.user_id,
                'name': user.name,
                'last_active': user.last_active,
                'bookings': user_booking
            }
            res[user.user_id] = user_detail
        else:
            res[user.user_id] = user_detail = {
                'username': user.user_id,
                'name': user.name,
                'last_active': user.last_active,
                'bookings':{}
            }
    return res


class Users(db.Model):
	user_id = db.Column(db.String(120), primary_key=True)
	name = db.Column(db.String(120),nullable=False)
	last_active = db.Column(db.String,nullable=False)

# with open("{}/database/users.json".format(root_dir()), "r") as f:
#     users = json.load(f)


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "users": "/users",
            "user": "/users/<username>",
            "create user": "/users/add",
            "bookings": "/users/<username>/bookings",
            "suggested": "/users/<username>/suggested"
        }
    })


@app.route("/users", methods=['GET'])
def users_list():
    return nice_json(get_users())


@app.route("/users/<username>", methods=['GET'])
def user_record(username):
    username = username.encode('ascii','ignore')
    if username not in get_users().iterkeys():
        raise NotFound("User '{}' not found.".format(username))

    return nice_json(get_user_by_id(username))

@app.route("/users/add",methods=['POST'])
def user_create():

    print 'user_create'	
    _id = request.form.get('id')
    _name = request.form.get('name')
    if not _id == None and not _name==None:
        create_user(_id,_name)
        return nice_json(get_users()[_id])
    else:
        abort(404)

    print 'end_create_user'


@app.route("/users/<username>/bookings", methods=['GET'])
def user_bookings(username):
    """
    Gets booking information from the 'Bookings Service' for the user, and
     movie ratings etc. from the 'Movie Service' and returns a list.
    :param username:
    :return: List of Users bookings
    """
    user_bookings = None
    # reply = requests.get('http://localhost:5003/bookings')
    # reply = reply.json()
    # return nice_json(reply)

    if username not in get_users().iterkeys():
        raise NotFound("User '{}' not found.".format(username))

    try:
        users_bookings = requests.get("http://localhost:5003/bookings/{}".format(username))
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Bookings service is unavailable.")
    
    if users_bookings.status_code == 404:
        raise NotFound("No bookings were found for {}".format(username))

    users_bookings = requests.get("http://localhost:5003/bookings/{}".format(username))
    users_bookings = users_bookings.json()
    print "Done"

    # For each booking, get the rating and the movie title
    result = {}
    for date, movies in users_bookings.iteritems():
        result[date] = []
        for movieid in movies:
            try:
                movies_resp = requests.get("http://localhost:5001/movies/{}".format(movieid))
                movies_resp = movies_resp.json()
                result[date].append({
                    "title": movies_resp["title"],
                    "rating": movies_resp["rating"],
                    "uri": movies_resp["uri"],
                    "id": movies_resp["id"]
                })
            except requests.exceptions.ConnectionError:
                raise ServiceUnavailable("The Movie service is unavailable.")

    return nice_json(result)

@app.route("/users/order",methods=["POST"])
def order_movie_():
    movie_id = request.form['movie_id']
    showtime_id = request.form['showtime_id']
    user_id = request.form['user_id']

    payload = {
        'movieid': movie_id,
        'showtimeid': showtime_id,
        'userid': user_id
    }

    movie_status = requests.get('http://localhost:5001/movies/{}'.format(movie_id))
    if movie_status.status_code == 200:
        order = requests.post('http://localhost:5003/bookings',data = payload)
        if order.status_code == 200:
            return nice_json(order.json())
    else:
        abort(404)

@app.route("/users/statuses",methods=['GET'])
def user_statuses():
    data = obtain_user_statuses()
    return nice_json(data)

@app.route("/users/home",methods=['GET'])
def render_page():
    return render_template('userbookings.html')


if __name__ == "__main__":
    # Only run below commands to initialize database from scratch
    # db.create_all()
    # fillsqlitetable()
    app.run(port=5000, debug=True)
