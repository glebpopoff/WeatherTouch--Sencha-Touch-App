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
class DesktopAppHandler(webapp.RequestHandler):
    def get(self):
		ua = self.request.user_agent
		b = AppConfig.mobileDetectionB.search(ua)
		v = AppConfig.mobileDetectionV.search(ua[0:4])
		if (b or v):
			self.redirect('/touch')
			return
			
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'templates')
		path = os.path.join(path, 'desktop.html')
		self.response.out.write(template.render(path, template_values))