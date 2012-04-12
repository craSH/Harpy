#!/usr/bin/python

from blackmamba import *
from har import *
import sys
from urlparse import urlparse
from datetime import datetime

def process(request):

	try:
		# create the HTTP GET request from the URL
		raw_request = request.puke()
		
		# prepare response for late use
		response = Response()
		response._timings = Timings()
		if '_sequence' in request:
			response._sequence = request._sequence
		
		# wanted to do something like this... or get from headers maybe?
		#host = request.host
		#port = request.post
	
		# but urlparse works too
		urlp = urlparse(request.url)
		host = urlp.hostname.strip()
		default_port = 443 if urlp.scheme == 'https' else 80
		port = urlp.port if urlp.port else default_port
	
		# if the server IP address has been overridden, use that	
		if '_serverIPAddress' in request:
			host = request._serverIPAddress
	
		# else resolve the hostname
		else:
			# to resolve DNS asynchronously, call resolve() prior to connect()
			yield resolve(host)

		# connect
		start = datetime.now()
		yield connect(host, port)
		response._timings.connect = get_time_delta(start)
	
		# write
		start = datetime.now()
		yield write(raw_request)
		response._timings.send = get_time_delta(start)
		
		# read
		start = datetime.now()
		raw_response = yield read()
		response._timings.wait = get_time_delta(start)
		
		# set bogus recieve timing
		response._timings.recieve = 0
		
		# calculate endtime
		end = datetime.now()
		duration = ((end-start).microseconds)/1000

		# do something with Response object
		#print raw_response
		response.devour(raw_response)
		print response.status
		print response._timings

		# close the connection
		yield close()

	except SockError as e:
		print e


def get_time_delta(start):
	"""get microseconds since start. start is a datetime object."""
	end = datetime.now()
	duration = ((end-start).microseconds)/1000
	return duration


def request_gen():
	"""Request generator that reads from stdin"""
	for line in sys.stdin:
		yield Request(line)



if __name__=='__main__':

	# Create a generator. List comprehension syntax is nice
	taskgen = (process(request) for request in request_gen())

	# the debug() is a wrapper for run() which provides verbose error handling  
	debug(taskgen)
	#run(taskgen)


