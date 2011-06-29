#!/usr/bin/env python

import Cookie
import datetime
import time
import os
import email.utils
import calendar
import logging
from django.utils import simplejson
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp 
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from LocationController import SaveLocation
from LocationController import GetLocation
from WeatherController import GetWeather
from GeoController import GeoCodeController
from django.http import HttpResponseRedirect
import AppConfig

#main controller for touch supported devices
class TouchAppHandler(webapp.RequestHandler):
    def get(self):
		#defaults to Cupertino, CA
		defaultZip = 'z:95014'
		defaultLocationName = 'Cupertino, CA'
		appIDValue = ""
		#check cookie container
		if (AppConfig.appCookieName in self.request.cookies):
			#get application ID from cookies
			appIDValue = self.request.cookies[AppConfig.appCookieName]
		
		#do we have app ID?
		if (appIDValue):
			#if so, get saved locations
			locationRecords = db.GqlQuery("SELECT * FROM LocationStorageDB WHERE appid='%s' ORDER BY addeddate DESC" % appIDValue)
			for location in locationRecords:
				defaultLocationName = location.statetown
				if (location.zip):
					defaultZip = 'z:%s' % location.zip
					break;
				else:
					defaultZip = 'll:%f,%f' % (location.lat, location.lon)
					break;
		#set django html template vars			
		template_values = {"default_zip":defaultZip, 
						   "default_location":defaultLocationName, 
						   "google_maps_api_key":"<not used on the client side>"
						   }
		path = os.path.join(os.path.dirname(__file__), 'templates')
		path = os.path.join(path, 'index.html')
		self.response.out.write(template.render(path, template_values))