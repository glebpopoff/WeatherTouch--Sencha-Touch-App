#!/usr/bin/env python

from google.appengine.ext import db

#location storage
class LocationStorageDB(db.Model):
	appid = db.StringProperty()
	zip = db.StringProperty()
	lat = db.FloatProperty()
	lon = db.FloatProperty()
	statetown = db.StringProperty()
	addeddate = db.DateTimeProperty(auto_now_add=True)