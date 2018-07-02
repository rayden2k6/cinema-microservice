import uuid

from init_service import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound, abort
import json
from flask_sqlalchemy import SQLAlchemy
from copy import deepcopy
import time
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cmovies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ROOT_MOVIES = {"uri": "/", "subresource_uris": {"movies": "/movies", "movie": "/movies/<id>"}}
MOVIES_JSON = "{}/database/movies.json".format(root_dir())

class Movies(db.Model):
    movie_id = db.Column(db.String(120),primary_key=True,nullable=False)
    title = db.Column(db.String(120),nullable=False)
    rating = db.Column(db.Float,nullable=False)
    director = db.Column(db.String(120),nullable=False)

def get_movies_all():
	movies = Movies.query.all()
	response_object = dict()
	for movie in movies:
		movie_object = {
   "director": movie.director,
   "id": movie.movie_id,
   "rating": movie.rating,
   "title": movie.title,
   "uri" : "/movies/{}".format(movie.movie_id)
		}
		response_object[movie.movie_id] = deepcopy(movie_object)
	return response_object

def get_movie(_id):
	return get_movies_all()[_id]

def create_movie_record(_director,_rating,_title,_id=str(uuid.uuid4())):
	movie = Movies(director=_director,rating=_rating,title=_title,movie_id=_id)
	db.session.add(movie)
	db.session.commit()
	return get_movies_all()

def delete_movie_record(_id):
    movie = Movies.query.get(_id)
    db.session.delete(movie)
    db.session.commit()
    return get_movies_all()

def update_movie_record(_movie_id,_title=None,_rating=None,_director=None):
	if not _title == None:
		Movies.query.filter_by(movie_id=_movie_id).update(dict(title=_title))
	if not _rating == None:
		Movies.query.filter_by(movie_id=_movie_id).update(dict(rating=_rating))
	if not _director == None:
		Movies.query.filter_by(movie_id=_movie_id).update(dict(director=_director))
	db.session.commit()
	return get_movies_all()

def fillsqlitetable():
    movies =  Movies.query.all()
    for movie in movies:
        db.session.delete(movie)
    db.session.commit()
    jsondb = json.load(open('../database/movies.json','r'))
    for movie_id in jsondb.keys():
        title = jsondb[movie_id]['title']
        rating = jsondb[movie_id]['rating']
        director = jsondb[movie_id]['director']
        movie = Movies(movie_id=movie_id,title=title,rating=rating,director=director)
        db.session.add(movie)
    db.session.commit()


# def get_movies(movie_id=None):
#     with open(MOVIES_JSON, "r") as f:
#         movies = json.load(f)
#         if movie_id is None:
#             return movies
#         else:
#             return movies[movie_id]
#
#
# get_movies()


@app.route("/", methods=['GET'])
def root():
    return nice_json(ROOT_MOVIES)


@app.route("/movies/<movieid>", methods=['GET'])
def movie_info(movieid):
    if movieid not in get_movies_all().iterkeys():
        raise NotFound

    result = get_movie(movieid)
    # result["uri"] = "/movies/{}".format(movieid)

    return nice_json(result)


@app.route("/movies", methods=['GET', 'POST'])
def movie_record():
    if request.method == 'POST':
        id = str(uuid.uuid4())
        movie = {
                'title': request.form['title'],
                'rating': request.form['rating'],
                'director': request.form['director'],
                'id': id,
                }

        create_movie_record(movie['director'],movie['rating'],movie['title'],movie['id'])

    return nice_json(get_movies_all())

@app.route('/movies/<movieid>',methods=['DELETE'])
def delete_movie(movieid):
    if not movieid == None and movieid in get_movies_all().iterkeys():
        return nice_json(delete_movie_record(movieid))
        # return _id
    else:
        abort(404)

@app.route('/movies/<movieid>',methods=['PUT'])
def update_movie(movieid):
    movie = {
             'rating': request.form['rating']
    }
    if not movieid in get_movies_all().iterkeys() or movie['rating'] == None or movieid == None:
        abort(404)
    else:
        update_movie_record(_movie_id=movieid,_rating=float(movie['rating']))
        return nice_json(get_movies_all()[movieid])

@app.route('/movies/rank/<username>',methods=['GET'])
def movie_ranking(username):
    limit = 3
    allmovies = Movies.query.order_by(Movies.rating.desc()).all()
    movies = list()
    userbookings = requests.get("http://localhost:5000/users/{}/bookings".format(username))
    userbookings = userbookings.json()
    ignore = []
    for showtime in userbookings.iterkeys():
        ignore += [item['id'] for item in userbookings[showtime]]
        # user_movies = userbookings[showtime]
        # print user_movies
        # for i in range(0,len(allmovies)):
        #     status = True
        #     for j in range(0,len(user_movies)):
        #         if allmovies[i].movie_id == user_movies[j]['id']:
        #             status = False
        #             ignore.append(user_movies[j]['id'])
        #     if not status == False:
        #         state = True
        #         for count in range(0,len(ignore)):
        #             if allmovies[i].movie_id == ignore[count]:
        #                 state = False
        #         if not state == False:
        #             movies.append(allmovies[i])
    print 'ignore: '+str(ignore)
    movies = Movies.query.order_by(Movies.rating.desc()).filter(Movies.movie_id.notin_(ignore)).all()
    if len(movies)> 3:
        movies = movies[:limit]
    return nice_json({'movies':[
        {
            'title': movie.title,
            'id': movie.movie_id,
            'rating': movie.rating,
            'director': movie.director
        } for movie in movies
    ]})

if __name__ == "__main__":
    # Only run below commands to initialize databases from scratch
    # db.create_all()
    # fillsqlitetable()
    app.run(host='127.0.0.1', port=5001, debug=True)
