import unittest
import requests

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../services/cbookings.db'
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


class TestBookingService(unittest.TestCase):
    def setUp(self):
        self.url = "http://127.0.0.1:5003/bookings"

    def test_booking_records(self):
        """ Test /bookings/<username> for all known bookings"""
        fillsqlitetable()
        for date, expected in GOOD_RESPONSES.iteritems():
            print date, expected
            reply = requests.get("{}/{}".format(self.url, date))
            actual_reply = reply.json()

            self.assertEqual(len(actual_reply), len(expected),
                             "Got {} booking but expected {}".format(
                                 len(actual_reply), len(expected)
                             ))

            # Use set because the order doesn't matter
            self.assertEqual(set(actual_reply), set(expected),
                             "Got {} but expected {}".format(
                                 actual_reply, expected))

    def test_not_found(self):
        """ Test /showtimes/<date> for non-existent users"""
        fillsqlitetable()
        invalid_user = "jim_the_duck_guy"
        actual_reply = requests.get("{}/{}".format(self.url, invalid_user))
        self.assertEqual(actual_reply.status_code, 404,
                         "Got {} but expected 404".format(
                             actual_reply.status_code))

    def test_add_new_booking(self):
        fillsqlitetable()
        payload = {
            'movieid' : "7daf7208-be4d-4944-a3ae-c1c2f516f3e6",
            'userid': "chris_rivers",
            'showtimeid': "20151201"
        }
        actual_reply = requests.post(self.url,data = payload)
        actual_reply = actual_reply.json()
        self.assertEqual(set(actual_reply[payload['userid']][payload['showtimeid']]),set(GOOD_RESPONSES[payload['userid']][payload['showtimeid']]+[payload['movieid']]))

    def test_delete_booking(self):
        fillsqlitetable()
        payload = {
            'movieid': "7daf7208-be4d-4944-a3ae-c1c2f516f3e6",
            'userid': "dwight_schrute",
            'showtimeid': "20151201"
        }
        res = GOOD_RESPONSES[payload['userid']][payload['showtimeid']][1]
        actual_reply = requests.delete("{}".format(self.url),data = payload)
        actual_reply = actual_reply.json()
        self.assertEqual(actual_reply[payload['userid']][payload['showtimeid']][0],res)


GOOD_RESPONSES = {
  "chris_rivers": {
    "20151201": [
      "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
    ]
  },
  "garret_heaton": {
    "20151201": [
      "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
    ],
    "20151202": [
      "276c79ec-a26a-40a6-b3d3-fb242a5947b6"
    ]
  },
  "dwight_schrute": {
    "20151201": [
      "7daf7208-be4d-4944-a3ae-c1c2f516f3e6",
      "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
    ],
    "20151205": [
      "a8034f44-aee4-44cf-b32c-74cf452aaaae",
      "276c79ec-a26a-40a6-b3d3-fb242a5947b6"
    ]
  }
}

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
