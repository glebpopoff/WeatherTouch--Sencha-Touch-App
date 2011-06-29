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
from DesktopMain import DesktopAppHandler
from TouchMain import TouchAppHandler

#application controllers
def main():
    application = webapp.WSGIApplication([('/', DesktopAppHandler), 
										  ('/weather', GetWeather), 
										  ('/save', SaveLocation),
										  ('/location', GetLocation),
										  ('/geo', GeoCodeController),
										  ('/desktop', DesktopAppHandler),
										  ('/touch', TouchAppHandler)
										],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
