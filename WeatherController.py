#!/usr/bin/env python

from google.appengine.api import urlfetch
from UserString import MutableString
import Cookie
import uuid
import os
import datetime
from datetime import tzinfo,timedelta
import time
import email.utils
import calendar
import logging
from django.utils import simplejson
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp 
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from django.template.defaultfilters import date as django_date_filter
import AppConfig

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

#ajax call to get weather data
class GetWeather(webapp.RequestHandler):
    def get(self):
		zipCode = ''
		zipCodeParamName = "loc"
		if (zipCodeParamName in self.request.params):
			zipCode = self.request.params[zipCodeParamName]
			
		#validate parameters
		if (not zipCode):
			self.response.out.write('invalid parameters')
			return	
		
		cookieValue = ''
		if (AppConfig.appCookieName in self.request.cookies):
			#read cookie
			cookieValue = self.request.cookies[AppConfig.appCookieName]
		else:
			cookieValue = uuid.uuid1() 
			logging.debug('base: setting new cookie: %s' % cookieValue);
			userCookie = Cookie.BaseCookie()
			userCookie[AppConfig.appCookieName] = cookieValue
			expires = datetime.datetime.utcnow() + datetime.timedelta(days=360)
			timestamp = calendar.timegm(expires.utctimetuple())
			userCookie[AppConfig.appCookieName]["expires"] = email.utils.formatdate(timestamp,localtime=False,usegmt=True)
			for morsel in userCookie.values():
				self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))
			
		#call weather service and get JSON
		#because of python timeouts we'll to try catch the exception and resubmit
		devKey = AppConfig.weatherBugAPIKey
		urlSuffix = 'nf=5&ih=1&ht=t&ht=i&ht=d&ht=ws&ht=wd&ht=h&ht=cp&l=en&c=US'
		if (zipCode[0:1] == 'z'):
			#lookup by zip
			urlStr = 'http://i.wxbug.net/REST/Direct/GetForecast.ashx?zip=%s&api_key=%s&%s' % (zipCode[2:], devKey, urlSuffix)
		else:
			#lookup by lat/lon
			coords = zipCode[2:].split(',')
			urlStr = 'http://i.wxbug.net/REST/Direct/GetForecast.ashx?la=%s&lo=%s&api_key=%s&%s' % (coords[0], coords[1], devKey, urlSuffix)
		#self.response.out.write(urlStr)
		try:
			result = urlfetch.fetch(url=urlStr, deadline=30)
			if result.status_code == 200:
				jsonData = simplejson.loads(result.content)
			else:
				self.response.out.write('unable to retrieve data (1 of 2). Invalid http code')
				return
		except:
			#lets try to resubmit the request
			try:
				result = urlfetch.fetch(url=urlStr, deadline=30)
				if result.status_code == 200:
					jsonData = simplejson.loads(result.content)
				else:
					self.response.out.write('unable to retrieve data (2 of 2). Invalid http code.')
					return
			except:
				self.response.out.write('unable to retrieve data (2 of 2). Exception.')
				return
		
		#image for first day (http://img.weather.weatherbug.com/forecast/icons/localized/500x420/en/trans/cond026.png)
		lastWeekDayStr = ''
		webapp_json_data = MutableString()
		last_hourly_data = MutableString()
		#parse JSON and get stuff we need for the app
		for dayObj in jsonData["forecastList"]:
			imgIcon = ''
			if (dayObj['dayIcon'] != None):
				imgIcon = dayObj['dayIcon']
			else:
				imgIcon = dayObj['nightIcon']
			
			if (not dayObj['high']):
				dayObj['high'] = ''
			
			if (not dayObj['dayDesc']):
				dayObj['dayDesc'] = dayObj['nightDesc']
			
			#build ourly forecast data
			hourly_data = MutableString()
			if (dayObj['hourly']):
				#build hourly json
				for hourlyObj in dayObj['hourly']:
					chancePrecip = ''
					dateTimeStr = ''
					dateTimeStamp = ''
					desc = ''
					humidity = ''
					icon = ''
					temperature = ''
					windDir = ''
					windSpeed = ''
					weekDayStr = ''
					precipChance = ''
					
					if (hourlyObj['chancePrecip']):
						chancePrecip = hourlyObj['chancePrecip']
					if (hourlyObj['dateTime']):
						dateTimeStamp = hourlyObj['dateTime']
						EST = Zone(-5,False,'EST')
						GMT = Zone(0,False,'GMT')
						#format: 2011-06-27 09:00:00-05:00
						#dateTimeGMTStr = datetime.fromtimestamp(int(hourlyObj['dateTime'])/1000).strftime('%Y-%m-%d %H:%M:%S')
						#t = datetime.strptime(dateTimeGMTStr,'%Y-%m-%d %H:%M:%S')
						dateTimeGMTStr = datetime.datetime.fromtimestamp(int(hourlyObj['dateTime'])/1000).strftime('%Y-%m-%d %H:%M:%S')
						t = datetime.datetime.strptime(dateTimeGMTStr,'%Y-%m-%d %H:%M:%S')
						t = t.replace(tzinfo=GMT)
						dateTimeObj = t.astimezone(EST)#.strftime('%I %p') #09 AM (leading zeros)
						dateTimeStr = django_date_filter(dateTimeObj, 'g A') # 9 AM (w/o leading zeros)
						weekDayStr = django_date_filter(dateTimeObj, 'l') #Friday
						if (weekDayStr != ''):
							if (lastWeekDayStr == weekDayStr):
								weekDayStr = ''
							else:
								lastWeekDayStr = weekDayStr
						
					if (hourlyObj['desc']):
						desc = hourlyObj['desc']			
					if (hourlyObj['humidity']):
						humidity = hourlyObj['humidity']
					if (hourlyObj['icon']):
						icon = hourlyObj['icon']
					if (hourlyObj['temperature']):
						temperature = hourlyObj['temperature']
					if (hourlyObj['windDir']):
						windDir = hourlyObj['windDir']
					if (hourlyObj['windSpeed']):
						windSpeed = hourlyObj['windSpeed']
					if (hourlyObj['chancePrecip']):
						precipChance = hourlyObj['chancePrecip']
					
					#time in GMT!!
					nowDate = time.time()
					wsTime = int(hourlyObj['dateTime'])/1000
					if (wsTime >= nowDate):
						hourly_data = '%s,{"chancePrecip": "%s","dateTimeStr": "%s","dateTime": "%s", "desc": "%s","humidity": "%s","icon":"%s","temperature":"%s","windDir":"%s","windSpeed":"%s", "weekDay":"%s", "precipChance":"%s"}' % (
									hourly_data,
									chancePrecip,
									dateTimeStr,
									dateTimeStamp,
									desc,
									humidity,
									icon,
									temperature,
									windDir,
									windSpeed,
									weekDayStr,
									precipChance
									)
			
			hourly_data = "[%s]" % (hourly_data[1:])
			webapp_json_data = "%s,{\"daydesc\": \"%s\", \"name\": \"%s\", \"low\": \"%s\", \"imgIcon\": \"%s\", \"high\": \"%s\", \"pred\": \"%s\", \"hourly\": %s}" % (
									webapp_json_data, 
									dayObj['dayDesc'], 
									dayObj['dayTitle'], 
									dayObj['low'], 
									imgIcon, 
									dayObj['high'], 
									dayObj['nightPred'],
									hourly_data
									)
			
		webapp_json = "{\"results\":[%s]}" % (webapp_json_data[1:]);
		self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
		self.response.out.write(webapp_json)