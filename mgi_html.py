# mgdhtml.py
# functions for writing standard HTML elements to sys.stdout

import sys
import os
import string
import types
import time
import regex
import cgi
import urllib
from signal import signal, alarm, SIGALRM

# global variable:
TITLE='MGI'

def set_pageTitle (s):
	# sets the title for the ht_title() function
	global TITLE
	TITLE = s
	return

def ht_title(content):
	sys.stdout.write('<TITLE>%s - %s</TITLE>' % (TITLE, content))

def ht_h1(content):
	sys.stdout.write('<H1>' + content + '</H1>')

def ht_hr():
	sys.stdout.write('<HR>')

def ht_anchor(link, content):
	sys.stdout.write('<A HREF="' + link + '">' + content + '</A>')

##################################
# pieces formerly in mgi_utils.py:
##################################

# Aliases
#########
url_unescape = urllib.unquote	# For backward compatability


# Functions
###########

def mgiCopyright():
	"""Returns a string representation of the copyright for web pages."""

	s = '''\
<HR>
<SMALL><H4>WARRANTY DISCLAIMER AND COPYRIGHT NOTICE</H4>
THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE SUITABILITY OR 
ACCURACY OF THIS SOFTWARE OR DATA FOR ANY PURPOSE, AND MAKES NO WARRANTIES, 
EITHER EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR A 
PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA WILL NOT 
INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS, OR OTHER RIGHTS.  
THE SOFTWARE AND DATA ARE PROVIDED "AS IS".
<P>
This software and data are provided to enhance knowledge and encourage 
progress in the scientific community and are to be used only for research 
and educational purposes.  Any reproduction or use for commercial purpose 
is prohibited without the prior express written permission of the Jackson 
Laboratory.
<P>
</SMALL>
Copyright &#169 1996, 1999, 2000 by The Jackson Laboratory<BR>
All Rights Reserved<BR>
'''
	return s


def mgiRetrieve():
	"""Returns a string representation of the retrieve button for forms."""

	s = '''\
<HR>
<INPUT TYPE=submit VALUE="Retrieve"> <INPUT TYPE=reset VALUE="Reset Form">
<HR>
'''
	return s


def mgiMaxReturn():
	"""Returns a string representation of the maxreturn section of forms."""

	s = '''\
<b>Max number of items returned:</b>
<INPUT TYPE="radio" NAME="*limit" VALUE="10">10
<INPUT TYPE="radio" NAME="*limit" VALUE="100" CHECKED>100
<INPUT TYPE="radio" NAME="*limit" VALUE="500">500
<INPUT TYPE="radio" NAME="*limit" VALUE="0">No limit
<BR>
'''
	return s


def get_fields(content = None):
	"""Processes fields from an HTML form.
	#
	# Requires:
	#	content -- A string containing form content.  A value of None
	#		(default) means to read from sys.stdin.
	#
	# Effects:
	#	- Reads from sys.stdin
	#	
	# Notes:
	#	This needs work big-time. -- gtc
	#	The web interface (WI) is mostly through a migration away from
	#	using this function.  Its use should probably be discouraged.
	#	-- jsb
	#
	"""
	fields = {}
	operators = {}
	types = {}
	negates = {}

	# Note -- httpd 1.3 does not close stdin
	# read exactly CONTENT_LENGTH bytes or the script will hang
	if content is None:
		length = string.atoi(os.environ['CONTENT_LENGTH'])
		content = sys.stdin.read(length)

	tokens = string.splitfields(content, '&')
	for i in range(0, len(tokens)):
		mapping = string.splitfields(string.joinfields(
			string.splitfields(string.strip(tokens[i]), '+'), ' '),
			'=')
		mapping[1] = string.strip(url_unescape(mapping[1]))
		if mapping[1] == '':
			continue
		mapping = url_unescape(mapping[0]), mapping[1]
		type = string.splitfields(mapping[0], ':')
		if len(type) == 1:
			fields[type[0]] = mapping[1]
		elif type[0] == 'op':
			operators[type[1]] = mapping[1]
		elif type[0] == 'not':
#
#	Grabs all of fields that have a "checked" NOT operator.
#
			negates[type[1]] = mapping[1]
		elif type[0] == 'list':
			key = type[1]
			if fields.has_key(key) == 0:
				fields[key] = []
			fields[key].append(mapping[1])
		else:
			fields[type[1]] = mapping[1]
			types[type[1]] = type[0]
	for key in fields.keys():
		if types.has_key(key) and operators.has_key(key):
			operator = operators[key]
			if string.lower(operator) == 'is null':
				del fields[key]
				continue
			if key == 'symbol':
				l = string.split(fields[key], ',')
				for i in range(len(l)):
					l[i] = string.strip(l[i])

				if operator == 'begins':
					for i in range(len(l)):
						l[i] = l[i] + '%'
				elif operator == 'ends':
					for i in range(len(l)):
						l[i] = '%' + l[i]
				elif operator == 'contains':
					for i in range(len(l)):
						l[i] = '%' + l[i] + '%'
				elif string.lower(operator) == 'is null':
					del fields[key]
					continue
				else:
					fields[key] = l
					continue
				fields[key] = l
				operators[key] = 'like'
			elif types[key] == 'text':
				if operator == 'begins':
					fields[key] = fields[key] + '%'
				elif operator == 'ends':
					fields[key] = '%' + fields[key]
				elif operator == 'contains':
					fields[key] = '%' + fields[key] + '%'
				elif string.lower(operator) == 'is null':
					del fields[key]
					continue
				else:
					continue
				operators[key] = 'like'
#
#	Where NOT has been used alter the operator accordingly.
#
	for key in negates.keys():
		if operators.has_key(key):
			operator = operators[key]
			if operator == '=':
				operators[key] = '!' + operators[key]
			elif operator == 'like':
				operators[key] = 'not' + ' ' + operators[key]
			elif string.lower(operator) == 'is null':
				operators[key] = 'is not null'
	result =  fields, operators, types
	return result


def print_field(label, value):
	sys.stdout.write('<B>%s</B>\t' % label)
	if value is None:
		print  'NULL'
	else:
		print str(value)
	print '<BR>'


def escape(html):
	"""Escapes '&', '<' and '>' characters as SGML entities.
	#
	# Note:
	#	This was repaired in 10/97 to escape the '&' properly.  It was
	#	not being done before that.
	"""
	if html is not None and type(html) is types.StringType:
		html = cgi.escape(html)
	else:
		html = ''
	return html

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
# Copyright © 1996, 1999, 2000 by The Jackson Laboratory
# All Rights Reserved
#
