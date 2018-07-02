import unittest
from copy import deepcopy

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../services/cmovies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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


class TestMoviesService(unittest.TestCase):
    def setUp(self):
        self.url = "http://127.0.0.1:5001/movies"

    def test_all_movie_records(self):
        """ Test /movies/<movieid> for all known movies"""
        fillsqlitetable()
        for movieid, expected in GOOD_RESPONSES.iteritems():
            expected['uri'] = "/movies/{}".format(movieid)
            reply = requests.get("{}/{}".format(self.url, movieid))
            actual_reply = reply.json()
            self.assertEqual( set(actual_reply.items()), set(expected.items()))

    def test_not_found(self):
        fillsqlitetable()
        invalid_movie_id = "b18f"
        actual_reply = requests.get("{}/{}".format(self.url, invalid_movie_id))
        self.assertEqual(actual_reply.status_code, 404,
                    "Got {} but expected 404".format(
                        actual_reply.status_code))

    def test_movie_delete(self):
        fillsqlitetable()
        valid_id = "720d006c-3a57-4b6a-b18f-9b713b073f3c"
        invalid_movie_id = "b18f"
        valid_response = dict(GOOD_RESPONSES)
        del valid_response[valid_id]
        actual_reply = requests.delete("{}/{}".format(self.url,valid_id))
        actual_reply = actual_reply.json()
        self.assertEqual(set(actual_reply.iterkeys()),set(valid_response.iterkeys()))

        #Check for invalid item delete request
        actual_reply = requests.delete("{}/{}".format(self.url,invalid_movie_id))
        self.assertEqual(actual_reply.status_code, 404, "Got {} but expected 404".format(
                        actual_reply.status_code))

    def test_movie_rating_update(self):
        fillsqlitetable()
        valid_id = "a8034f44-aee4-44cf-b32c-74cf452aaaae"
        rating = 4.6
        valid_response = deepcopy(GOOD_RESPONSES[valid_id])
        valid_response['rating'] = rating
        actual_reply = requests.put("{}/{}".format(self.url,valid_id),data = {'rating':rating})
        actual_reply = actual_reply.json()
        self.assertEqual(actual_reply['rating'],valid_response['rating'])

GOOD_RESPONSES = {
  "720d006c-3a57-4b6a-b18f-9b713b073f3c": {
    "title": "The Good Dinosaur",
    "rating": 7.4,
    "director": "Peter Sohn",
    "id": "720d006c-3a57-4b6a-b18f-9b713b073f3c"
  },
  "a8034f44-aee4-44cf-b32c-74cf452aaaae": {
    "title": "The Martian",
    "rating": 8.2,
    "director": "Ridley Scott",
    "id": "a8034f44-aee4-44cf-b32c-74cf452aaaae"
  },
  "96798c08-d19b-4986-a05d-7da856efb697": {
    "title": "The Night Before",
    "rating": 7.4,
    "director": "Jonathan Levine",
    "id": "96798c08-d19b-4986-a05d-7da856efb697"
  },
  "267eedb8-0f5d-42d5-8f43-72426b9fb3e6": {
    "title": "Creed",
    "rating": 8.8,
    "director": "Ryan Coogler",
    "id": "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
  },
  "7daf7208-be4d-4944-a3ae-c1c2f516f3e6": {
    "title": "Victor Frankenstein",
    "rating": 6.4,
    "director": "Paul McGuigan",
    "id": "7daf7208-be4d-4944-a3ae-c1c2f516f3e6"
  },
  "276c79ec-a26a-40a6-b3d3-fb242a5947b6": {
    "title": "The Danish Girl",
    "rating": 5.3,
    "director": "Tom Hooper",
    "id": "276c79ec-a26a-40a6-b3d3-fb242a5947b6"
  },
  "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab": {
    "title": "Spectre",
    "rating": 7.1,
    "director": "Sam Mendes",
    "id": "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
  }
}

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
