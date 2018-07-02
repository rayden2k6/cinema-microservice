from copy import deepcopy

import requests

from init_service import root_dir, nice_json
from flask import Flask, request, abort, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cbookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Bookings(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    user_id = db.Column(db.String(120),nullable=False)
    showtime_id = db.Column(db.Integer,nullable=False)
    movie_id = db.Column(db.String(120),nullable=False)

def fillsqlitetable():
    bookings = Bookings.query.all()
    for booking in bookings:
        db.session.delete(booking)
    db.session.commit()
    jsondb = json.load(open('../database/bookings.json','r'))
    for user_id in jsondb.keys():
        for showtime_id in jsondb[user_id].keys():
            for movie_id in jsondb[user_id][showtime_id]:
                booking = Bookings(user_id=user_id,showtime_id=showtime_id,movie_id=movie_id)
                db.session.add(booking)
    db.session.commit()

# with open("{}/database/bookings.json".format(root_dir()), "r") as f:
#     bookings = json.load(f)

def get_bookings():
    response = dict()
    users = requests.get("http://localhost:5000/users")
    showtimes = requests.get("http://localhost:5002/showtimes")
    showtimes = showtimes.json()
    users = users.json()
    for user in users.iterkeys():
        _object = dict()
        for showtime in showtimes.iterkeys():
            bookings = Bookings.query.filter_by(user_id=user, showtime_id=showtime).all()
            movie_ids = [booking.movie_id for booking in bookings]
            if not movie_ids == []:
                _object[showtime] = movie_ids
        if not _object == {}:
            response[user] = _object
    return response

def delete_booking_by_id(user_id,showtime_id,movie_id):
    booking = Bookings.query.filter_by(user_id=user_id,showtime_id=showtime_id,movie_id=movie_id).first()
    db.session.delete(booking)
    db.session.commit()
    return get_bookings()

def add_booking(user_id,showtime_id,movie_id):
    booking = Bookings(user_id=user_id,showtime_id=showtime_id,movie_id=movie_id)
    db.session.add(booking)
    db.session.commit()

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "bookings": "/bookings",
            "booking": "/bookings/<username>"
        }
    })


@app.route("/bookings", methods=['GET'])
def booking_list():
    return nice_json(get_bookings())


@app.route("/bookings/<username>", methods=['GET'])
def booking_record(username):
    if username not in get_bookings().iterkeys():
        return not_found()

    return nice_json(get_bookings()[username])

@app.route("/bookings",methods=['DELETE'])
def delete_user_booking():
    _user_id,_showtime_id,_movie_id = request.form['userid'],request.form['showtimeid'],request.form['movieid']
    if _user_id == None and _showtime_id == None and _movie_id == None:
        raise NotFound
    else:
        delete_booking_by_id(_user_id,_showtime_id,_movie_id)
        return nice_json(get_bookings())

@app.route("/bookings",methods=['POST'])
def add_user_booking():
    movie_id = request.form['movieid']
    user_id = request.form['userid']
    showtime_id = request.form['showtimeid']

    add_booking(user_id,showtime_id,movie_id)
    return nice_json(get_bookings())


if __name__ == "__main__":
    # Only run below commands to initialize database from scratch
    # db.create_all()
    # fillsqlitetable()
    app.run(port=5003, debug=True)

