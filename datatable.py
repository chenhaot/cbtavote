from google.appengine.ext import db


class Election(db.Model):
  name = db.StringProperty()
  candidate = db.StringProperty()
  cid = db.IntegerProperty()


class Vote(db.Model):
  election = db.StringProperty()
  candidate = db.StringProperty()
  cid = db.IntegerProperty()
  vid = db.StringProperty()
  rank = db.IntegerProperty()
