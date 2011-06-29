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

#ajax call to persist location
class SaveLocation(webapp.RequestHandler):
	
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
		
	#save data
	def saveLocation(self,zip,cityState,lat,lon,appID):
		logging.error('saveLocation: Saving Data [Zip=%s,CityState=%s,Lat=%s,Lon=%s]' % (zip,cityState,lat,lon))
		#validate app key (persisted as a cookie)
		if (not appID):
			logging.error('saveLocation: invalid app id')
			self.response.out.write('Unable to save location: invalid app id')
			return
		
		if (zip or (lat and lon)):
			appSubKey = zip
			if (not zip):
				appSubKey = '%s_%s' % (lat,lon)
			dbKey = '%s_%s' % (appID,appSubKey)
			logging.debug('saveLocation: creating new instance. Using key=%s' % dbKey)
			location_k = db.Key.from_path('LocationStorageDB', dbKey)
			locRec = db.get(location_k)
			if (not locRec):
				locRec = LocationStorageDB(key_name=dbKey)
				locRec.appid = appID
				locRec.lat = lat
				locRec.lon = lon
				locRec.zip = zip
				locRec.statetown = cityState
				logging.debug('save: about to save')
				locRec.put()
			else:
				logging.debug('saveLocation: instance already exists')
				
			self.response.headers['Content-Type'] = 'application/json; charset=utf-8'	
			self.response.out.write('{"status": "success", "zip": "z:%s", "location": "%s", "coords": "ll:%s,%s"}' % (zip, locRec.statetown, locRec.lat, locRec.lon))
		else:
			logging.error('saveLocation: invalid zip or lat/lon')
			self.response.out.write('Unable to save location: invalid zip or lat/lon')
		return
	
	#get request
	def get(self):
		appIDValue = ''
		if (AppConfig.appCookieName in self.request.cookies):
			#get application ID from cookies
			appIDValue = self.request.cookies[AppConfig.appCookieName]
		
		#validate application id
		if (not appIDValue):
			logging.error('SaveLocation: unable to retrieve application ID from cookies or request parameters');
			self.response.out.write('Application Error: Invalid App ID Value')
			return
		
		#get zip parameter
		zipParam = ""
		zipParamName = "zip"
		if (zipParamName in self.request.params):
			zipParam = self.request.params[zipParamName]
		else:
			logging.error('SaveLocation: zip param missing');

		#get state/city
		stateCityParam = ""
		stateCityParamName = "statetown"
		if (stateCityParamName in self.request.params):
			stateCityParam = self.request.params[stateCityParamName]
		else:
			logging.error('SaveLocation: state/town param missing');
		
		#get latitude
		latParam = ""
		latParamName = "lat"
		if (latParamName in self.request.params):
			latParam = self.request.params[latParamName]
		else:
			logging.error('SaveLocation: latitude param missing');
		
		#get longitude
		lonParam = ""
		lonParamName = "lon"
		if (lonParamName in self.request.params):
			lonParam = self.request.params[lonParamName]
		else:
			logging.error('SaveLocation: longitude param missing');
		
		logging.debug("SaveLocation: Zip=%s,StateCity=%s,Lat=%s,Lon=%s" % (zipParam, stateCityParam, latParam, lonParam))
		
		#save if we have all four parameters
		if (zipParam and stateCityParam and latParam and lonParam):
			self.saveLocation(zipParam, stateCityParam, float(latParam), float(lonParam), appIDValue)
			return
		
		#we only have zip or statecityparam
		if (stateCityParam or zipParam):
			#get lat/lon from reverse geo service
			logging.debug('SaveLocation: get lat/lon by city/state or zip');
			#reverse geocoding http://maps.googleapis.com/maps/api/geocode/json?address=Farmington,CT+06032&sensor=true
			if (not zipParam):
				zipParam = ''
			if (not stateCityParam):
				stateCityParam = ''
			
			#tidy up the statecity string in case it's something like that farmington,%20ct
			stateCityParam = urllib.unquote(stateCityParam)
			if (',' in stateCityParam):
				parts = stateCityParam.split(',')
				tmp = MutableString()
				tmp = ''
				for m in parts:
					tmp = "%s,%s" % (urllib.quote(m.strip()), tmp)
				stateCityParam = tmp
			
			urlStr = 'http://maps.google.com/maps/geo?q=%s+%s&output=json&sensor=true&key=%s' % (stateCityParam,zipParam,AppConfig.googleMapsAPIKey)
			jsonData = self.reverseGeo(urlStr)	
			#lets see if have jsonData from reverse geocoding call
			if (jsonData):
				logging.debug("SaveLocation: Got JSON data=%s" % jsonData)
				#self.response.out.write(jsonData)
				lon = jsonData['Placemark'][0]['Point']['coordinates'][0]
				lat = jsonData['Placemark'][0]['Point']['coordinates'][1]
				#if we don't have zipcode then the call above won't return it
				#need to call reverse geo again and get zipcode by lat/lon
				if (not zipParam):
					try:
						urlStrZipLookup = 'http://maps.google.com/maps/geo?ll=%s,%s&output=json&sensor=true&key=%s' % (lat,lon,AppConfig.googleMapsAPIKey)
						jsonDataZip = self.reverseGeo(urlStrZipLookup)
						if (jsonDataZip):
							zipParam = jsonDataZip['Placemark'][0]['AddressDetails']['Country']['AdministrativeArea']['Locality']['PostalCode']['PostalCodeNumber']
					except:
						logging.error('SaveLocation: unable to retrieve zip code based on geocode URL %s' % urlStrZipLookup);
				
				#lets not store city/state that user entered and use nicely formatted google maps address string
				stateCityParam = jsonData['Placemark'][0]['address']
				logging.debug("SaveLocation: Lat=%s,Lon=%s" % (lat,lon))
				self.saveLocation(zipParam, stateCityParam, lat, lon, appIDValue)
				return
			else:
				logging.error('SaveLocation: unable to translate Address into GPS coordinates')
				self.response.out.write('Unable to translate Address into GPS coordinates')
				return	
		else:	
			logging.error('SaveLocation: invalid parameters');
			self.response.out.write('Application Error: Invalid App Parameters')
			return
			
#ajax call to get a list of saved locations for appID
class GetLocation(webapp.RequestHandler):
	def get(self):
		appIDValue = ''
		defaultLocation = ",{\"lookup_id\": \"%s\", \"location\": \"%s\", \"zip\": \"%s\", \"lat\": \"%s\", \"lon\": \"%s\"}" % (
						'z:95014', 'Cupertino, CA', '95014', '', '')
		if (AppConfig.appCookieName in self.request.cookies):
			#get application ID from cookies
			appIDValue = self.request.cookies[AppConfig.appCookieName]

		#validate application id
		if (not appIDValue):
			logging.error('GetLocation: unable to retrieve application ID from cookies or request parameters');
			jsonData = defaultLocation

		#get saved locations
		locationRecords = db.GqlQuery("SELECT * FROM LocationStorageDB WHERE appid='%s' ORDER BY addeddate DESC" % appIDValue)
		jsonData = MutableString()
		jsonData = ''
		for location in locationRecords:
			if (location.zip):
				lookupID = 'z:%s' % location.zip
			else:
				lookupID = 'll:%f,%f' % (location.lat, location.lon)

			jsonData = "%s,{\"lookup_id\": \"%s\", \"location\": \"%s\", \"zip\": \"%s\", \"lat\": \"%s\", \"lon\": \"%s\"}" % (
							jsonData, lookupID, location.statetown, location.zip, location.lat, location.lon)

		#empty result set
		if (jsonData == ''):
			jsonData = defaultLocation

		#remove first char
		jsonData = jsonData[1:]

		self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
		self.response.out.write("{\"results\":[%s]}" % jsonData)