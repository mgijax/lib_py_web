#!/usr/local/bin/python

# Name: httpReader.py
# Purpose: provides an easy mechanism for retrieving HTML pages over the net,
#	including performing queries against CGI scripts.  Includes mechanisms
#	for timing-out slow responses.
# Notes: This module provides two publicly available mechanisms for reading
#	pages via HTTP.  For most cases, you should be able to use the
#	getURL() function -- this is a wrapper over the more flexible
#	httpReader class.  For some cases, you may want to use the class
#	directly.  This is okay, too, though a bit more complicated to use.

import httplib		# standard Python libraries
import urllib
import regex
import socket

import AlarmClock	# MGI libraries

###--- Global Variables ---###

error = 'httpReader.error'	# exception to be raised by this module
DEFAULT_TIMEOUT = 120		# two minutes is the default for timing out
server_re = regex.compile ('[a-zA-Z]+://\([^/]+\)')	# locate server in URL

###--- Public Function ---###

def getURL (url,			# string; URL from which to get a page
	parms = {},			# dictionary; string name:value pairs
					#	to pass as GET parameters
	timeout = DEFAULT_TIMEOUT	# integer; how many seconds to wait
					#	before giving up on the URL
	):
	# Purpose: connect to the given 'url', sending any specified 'parms'
	#	along, and retrieve an HTML page within the given 'timeout'
	# Returns: tuple of two items, either:
	#	(list of strings, None) if successful, or
	#	(None, error string) if unsuccessful (eg- because of timeout,
	#	or the connection cannot be made, or...)  For a timeout, the
	#	error string returned is "Connection timed out"
	# Assumes: nothing
	# Effects: makes an HTTP connection and reads from it
	# Throws: propagates 'error' if the server name cannot be found
	#	when parsing the 'baseURL'
	# Notes: The use of 'parms' is entirely optional.  If you'd rather
	#	encode any GET parameters as part of the 'url', you're welcome
	#	to do so.  We provide the ability to pass in a dictionary of
	#	'parms' only as a convenience.
	# Example: To get the weather report for Cherryfield, but only wait
	#	one minute for it, we could do...
	# getURL('http://www.wunderground.com/cgi-bin/findweather/getForecast'
	#	, {'query' : '04622' }, 60)

	r = httpReader (url, parms, timeout)
	return r.getPage()

###--- Public Class ---###

class httpReader:
	# IS:	an object entrusted with reading HTML pages across HTTP
	#	connections within a certain timeframe
	# HAS:	a URL, an optional set of parameters, and a number of seconds
	#	to use as a timeout for the connection
	# DOES:	reads pages from URLs via HTTP
	#
	# Notes: At its heart, the httpReader class has several mutator and
	#	accessor methods for changing its configuration, and one
	#	method which actually does the work of retrieving an HTML
	#	page (getPage).  Using the class is as simple as doing:
	#
	#    x = httpReader ('http://kelso/dev/searches/allele_report',
	#		{ '_Marker_key' : '3' }, 60)
	#    page, error = x.getPage()
	#
	#	This will retrieve alleles of a specified marker and give up
	#	if it takes longer than 60 seconds.  We could then use some
	#	of the mutator methods to use the same httpReader object to
	#	run a new query.  For example:
	#
	#    x.setBaseURL ('http://kelso/dev/searches/probe_report.cgi')
	#    page, error = x.getPage()
	#
	#	This would then retrieve molecular probes and segments for
	#	the same marker with the same timeout value.

	def __init__ (self,
		baseURL,		# string; URL from which to get a page
		parms = {},		# dictionary; string name:value pairs
					#	to pass as GET parameters
		timeout=DEFAULT_TIMEOUT	# integer; how many seconds to wait
					#	before giving up on the URL
		):
		# Purpose: instantiates the object
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: propagates 'error' if the server name cannot be
		#	found within the 'baseURL'

		# propagates error
		self.parms = {}			# set up the defaults
		self.baseURL = ''
		self.server = ''
		self.timeout = timeout		# handle the parameters
		self.setBaseURL (baseURL)
		self.setParms (parms)
		return

	def setBaseURL (self,
		baseURL			# string; URL from which to get a page
		):
		# Purpose: tell 'self' to retrieve future pages from the
		#	given 'baseURL'
		# Returns: nothing
		# Assumes: nothing
		# Effects: uses 'server_re', so its properties will be changed
		# Throws: 'error' if we cannot find the server name within
		#	the 'baseURL'
		global server_re

		if server_re.match (baseURL) == -1:
			raise error, 'Cannot find server in the given URL'
		self.server = server_re.group(1)
		self.baseURL = baseURL
		return

	def setParm (self,
		name,		# string; name of the parameter
		value		# string; value of the parameter
		):
		# Purpose: set the 'value' for a GET parameter with the given
		#	'name'
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		self.parms[name] = value
		return

	def setParms (self,
		parms = {}		# dictionary; string name:value pairs
					#	to pass as GET parameters
		):
		# Purpose: update the set of GET parameters to be only those
		#	contained in 'parms'
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		self.parms = parms
		return

	def setTimeout (self,
		timeout=DEFAULT_TIMEOUT	# integer; how many seconds to wait
					#	before giving up on the URL
		):
		# Purpose: set the maximum number of seconds that this
		#	httpReader will wait for pages to be returned for
		#	subsequent page retrievals
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		self.timeout = timeout
		return

	def getServer (self):
		# Purpose: accessor -- retrieve the server name to which the
		#	httpReader expects to connect
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.server

	def getBaseURL (self):
		# Purpose: accessor -- retrieve the URL of the page which the
		#	httpReader expects to read (minus any GET parameters)
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.baseURL

	def getParm (self,
		name		# string; name of the parameter whose value
				#	we want to retrieve
		):
		# Purpose: accessor -- retrieve the value of the GET parameter
		#	corresponding to the given 'name', or None if this
		#	httpReader has no knowledge of that parameter 'name'
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		if self.parms.has_key (name):
			return self.parms[name]
		return None

	def getParms (self):
		# Purpose: accessor -- retrieve the set of GET parameters
		# Returns: dictionary mapping string parameter name to string
		#	parameter value, for all GET parameters that this
		#	httpReader knows about
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.parms

	def getTimeout (self):
		# Purpose: accessor -- retrieve the current timeout setting
		#	for this httpReader
		# Returns: integer
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.timeout

	def getPage (self):
		# Purpose: use the current settings (baseURL, timeout, parms)
		#	for this httpReader to retrieve the page they specify
		# Returns: tuple of two items, either:
		#	(list of strings, None) if successful, or
		#	(None, error string) if unsuccessful (eg- because of
		#	a timeout, or because the connection could not be
		#	made, or...)  For a timeout, the error string
		#	returned is "Connection timed out".
		# Assumes: nothing
		# Effects: opens an HTTP connection and reads from it
		# Throws: nothing

		# build the string send as the page request, including any
		# specified GET parameters:

		request = self.baseURL
		if self.parms:
			request = request + '?'
			for name in self.parms.keys():
				request = request + '%s=%s' % (
					urllib.quote(name),
					urllib.quote(self.parms[name]))
		try:
			AlarmClock.set (self.getTimeout())	# set timeout

			# open the connection and send the request

			conn = httplib.HTTP (self.server)
			conn.putrequest ('GET', request)
			conn.putheader ('User-Agent', 'Mozilla')
			conn.endheaders()

			# get the reply and read it into a list of strings

			(code, message, headers) = conn.getreply()
			fp = conn.getfile()
			page = fp.readlines()
			fp.close()
			error = None

		except AlarmClock.timeUp:	# the connection timed out,
			page = None		# so return None
			error = 'Connection timed out'

		except socket.error:
			page = None
			error = 'Could not connect to %s' % self.server

		except IOError:
			page = None
			error = 'Problem reading from %s' % self.server

		except:
			page = None
			error = 'Unexpected error'

		AlarmClock.clear ()

		return page, error

###--- Self-Testing Code ---###

if __name__ == '__main__':
	print 'Testing time-out feature'
	page, error = getURL('http://www.ebi.ac.uk/htbin/emblfetch?L33248',
		timeout = 1)
	if error:
		print 'PASS - %s' % error
	else:
		print 'FAILED - EMBL query did not time out. ' + \
			'retrieved %d lines' % len(page)

	print
	print 'Testing unknown host'
	page, error = getURL ('http://bob/')
	if error:
		print 'PASS - %s' % error
	else:
		print 'FAILED - did not kick out unknown host'

	print
	print 'Testing page retrieval'
	page, error = getURL ('http://devwww.informatics.jax.org/')
	if error:
		print 'FAILED - %s' % error
	else:
		print 'PASS - collected %d lines from devwww' % len(page)
#
# Warranty Disclaimer and Copyright Notice
# 
#  THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE SUITABILITY OR 
#  ACCURACY OF THIS SOFTWARE OR DATA FOR ANY PURPOSE, AND MAKES NO WARRANTIES, 
#  EITHER EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR A 
#  PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA WILL NOT 
#  INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS, OR OTHER RIGHTS.  
#  THE SOFTWARE AND DATA ARE PROVIDED "AS IS".
# 
#  This software and data are provided to enhance knowledge and encourage 
#  progress in the scientific community and are to be used only for research 
#  and educational purposes.  Any reproduction or use for commercial purpose 
#  is prohibited without the prior express written permission of the Jackson 
#  Laboratory.
# 
# Copyright © 1996, 1999, 2002 by The Jackson Laboratory
# All Rights Reserved
#

