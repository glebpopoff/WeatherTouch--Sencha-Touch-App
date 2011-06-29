#!/usr/bin/env python

from google.appengine.api import urlfetch
from UserString import MutableString
import urllib
import Cookie
import uuid
import os
import datetime
import time
import email.utils
import calendar
import logging
from django.utils import simplejson
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp 
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from Models import LocationStorageDB
import AppConfig

#ajax call to get zip/state based on GPS coords
class GeoCodeController(webapp.RequestHandler):
	
	#call reverse geocoding service and get json data
	def reverseGeo(self, urlStr):
		try:
			logging.debug('reverseGeo: %s' % urlStr)
			result = urlfetch.fetch(url=urlStr, deadline=30)
			if result.status_code == 200:
				jsonData = simplejson.loads(result.content)
			else:
				logging.error('SaveLocation: unable to translate Address into GPS coordinates...Attempt #1')
				self.response.out.write('Unable to translate Address into GPS coordinates...Attempt #1')
				return
		except:
			#lets try to resubmit the request
			try:
				result = urlfetch.fetch(url=urlStr, deadline=30)
				if result.status_code == 200:
					jsonData = simplejson.loads(result.content)
				else:
					logging.error('SaveLocation: unable to translate Address into GPS coordinates...Attempt #2')
					self.response.out.write('Unable to translate Address into GPS coordinates...Attempt #2')
					return
			except:
				logging.error('SaveLocation: unable to translate Address into GPS coordinates...Attempt #2')
				self.response.out.write('Unable to translate Address into GPS coordinates...Attempt #2')
				return
				
		return jsonData
	
	#get request
	def get(self):
		#get lat/lon parameter
		coordParam = ""
		coordParamName = "ll"
		if (coordParamName in self.request.params):
			coordParam = self.request.params[coordParamName]
		else:
			logging.error('GeoCode: lat/long params missing');
			self.response.out.write('Missing lat/long parameters')
			return

		logging.debug("GeoCode: ll=%s" % (coordParam))
		
		#get zipcode/state from reverse geocoding
		if (coordParam):
			urlStr = 'http://maps.google.com/maps/geo?ll=%s&output=json&sensor=true&key=%s' % (coordParam,AppConfig.googleMapsAPIKey)
			jsonData = self.reverseGeo(urlStr)	
			#lets see if have jsonData from reverse geocoding call
			if (jsonData):
				logging.debug("GeoCode: Got JSON data=%s" % jsonData)
				#self.response.out.write(jsonData)
				state = jsonData['Placemark'][0]['AddressDetails']['Country']['AdministrativeArea']['AdministrativeAreaName']
				city = jsonData['Placemark'][0]['AddressDetails']['Country']['AdministrativeArea']['Locality']['LocalityName']
				zip = jsonData['Placemark'][0]['AddressDetails']['Country']['AdministrativeArea']['Locality']['PostalCode']['PostalCodeNumber']
				
				self.response.headers['Content-Type'] = 'application/json; charset=utf-8'	
				self.response.out.write('{"status": "success", "zip": "%s", "city": "%s","state": "%s", "coords": "ll:%s"}' % (zip, city, state, coordParam))
				return
			else:
				logging.error('GeoCode: unable to translate GPS coordinates into address')
				self.response.out.write('Unable to translate GPS coordinates into address')
				return	
		else:	
			logging.error('GeoCode: invalid parameters');
			self.response.out.write('Application Error: Invalid App Parameters')
			return
			