from copy import deepcopy

from init_service import root_dir, nice_json
from flask import Flask
from werkzeug.exceptions import NotFound
from flask_sqlalchemy import SQLAlchemy
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cshowtimes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Showtimes(db.Model):
    showtime_id = db.Column(db.Integer,primary_key=True,nullable=False)
    name = db.Column(db.String(120),nullable=True)

class Showtimes_Movies(db.Model):
    rel_id = db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    showtime_id = db.Column(db.Integer,nullable=False)
    movie_id = db.Column(db.String(120), nullable=False)


# with open("{}/database/showtimes.json".format(root_dir()), "r") as f:
#     showtimes = json.load(f)

def fillsqlitetable():
    showtimes = Showtimes.query.all()
    for showtime in showtimes:
        db.session.delete(showtime)
    showtimes_movies = Showtimes_Movies.query.all()
    for showtime_movie in showtimes_movies:
        db.session.delete(showtime_movie)
    db.session.commit()

    jsondb = json.load(open('../database/showtimes.json','r'))
    for showtime_id in jsondb.keys():
        # query = "INSERT into showtimes(showtime_id) VALUES(?)"
        # _cursor.execute(query,(showtime_id,))
        showtime = Showtimes(showtime_id=showtime_id)
        db.session.add(showtime)
        movie_ids = jsondb[showtime_id]
        for movie_id in movie_ids:
            showtime_relation = Showtimes_Movies(showtime_id=showtime_id,movie_id=movie_id)
            db.session.add(showtime_relation)
    db.session.commit()


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "showtimes": "/showtimes",
            "showtime": "/showtimes/<date>"
        }
    })

def get_showtimes():
    showtimes = Showtimes.query.all()
    response = dict()
    for showtime in showtimes:
        showtime_relations = Showtimes_Movies.query.filter_by(showtime_id=showtime.showtime_id)
        movie_ids = [showtime_relation.movie_id for showtime_relation in showtime_relations]
        response[showtime.showtime_id] = deepcopy(movie_ids)
    return  response


@app.route("/showtimes", methods=['GET'])
def showtimes_list():
    return nice_json(get_showtimes())


@app.route("/showtimes/<date>", methods=['GET'])
def showtimes_record(date):
    if int(date) not in get_showtimes().iterkeys():
         raise NotFound
    return nice_json(get_showtimes()[int(date)])

if __name__ == "__main__":
    # Only run below commands to initialize database from scratch
    # db.create_all()
    # fillsqlitetable()
    app.run(port=5002, debug=True)
