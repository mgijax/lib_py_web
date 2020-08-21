# errorlib.py
# Support for handling errors.
#
# This module defines a utilities for handling errors in cgi scripts and for
# debugging cgi scripts written in Python.  Try to keep things as simple as
# possible -- if an exception occurs here it might not get handled properly.
#
# Using the errorlib module
# -------------------------
# Begin by putting "import errorlib" in your python program.  Put the "main"
# program into a function called "main" as follows:
#
#       def main()
#               ...your code here...
#
# Put the following at the end of your python program:
#
#       print 'Content-type: text/html'
#       print
#       try:
#               main()
#       except:
#               errorlib.handle_error()
#
# If you like, you can specify a file name or file object for the dump, as in:
#
#       errorlib.handle_error( '/usr/local/etc/httpd/logs/my_log' )
#               or
#       errorlib.handle_error( sys.stdout ) # Will dump to browser.
#
# If your program raises its own exceptions, you will need to take care of
# those.  For example, if you raise SystemExit to take care of some error
# condition, you can use this:
#
#       print 'Content-type: text/html'
#       print
#       try:
#               main()
#       except SystemExit:
#               pass
#       except:
#               errorlib.handle_error()
#
# Functions are available for setting default page titles, banners, and
# footers.  As well, the error handling functions provide optional parameters
# where some of these may be overridden.

# Imports
# =======

import os
import sys
import time
import types
import traceback

# Constants
# =========

NL = '\n'
DELIMITER = 20 * '* ' + NL

# Global Variables
# ================

TITLE = 'MGI'
BANNER = ''
FOOTER = ''

# Functions related to global variables
# =====================================

def set_pageTitle (s):
        global TITLE
        TITLE = s
        return

def set_pageBanner (s):
        global BANNER
        BANNER = s
        return

def set_pageFooter (s):
        global FOOTER
        FOOTER = s
        return

def check (s, default):
        # if s is non-None and non-empty, return s.  Otherwise return default.
        #
        # used to see whether optional parameters are specified, or whether
        # to just use the module-level defaults.

        if s:
                return s
        return default


# Other Functions
# ===============

def message (
        pageTitle=None          # string; title for HTML page
        ):
        # Displays the standard MGD Server Error message.

        s = '''<HTML><HEAD>
                <TITLE>%s - Server Error</TITLE>
                </HEAD><BODY BGCOLOR="#FFFFFF">
                <CENTER>
                <H1>Mouse Genome Informatics</H1>
                </CENTER>
                <HR>
                <H2>MGI Server Error</H2>
                An error occurred when the server attempted to process your
                request.  To report the problem, send a message to User
                Support at the following address:<P>
                <CENTER>
                <A HREF="mailto:mgi-help@informatics.jax.org">mgi-help@informatics.jax.org</A>
                </CENTER><P> 
                Please include the following information in your message:
                <UL>
                <LI>Date and time
                <LI>Brief description of problem
                <LI>WWW Browser and version #
                <LI>Type of computer
                <LI>Query form used and search criteria
                </UL>
                <HR>
                </BODY></HTML>''' % check(pageTitle, TITLE)
        sys.stdout.write(s + NL)
        return


def dump (
        fd      # file descriptor to which to write
        ):
        # Dumps current environment and stack trace to a file.

        fd.write( DELIMITER )
        fd.write( 'Exception Report: ' + time.ctime(time.time()) + 2*NL )
        fd.write( 'Environment variables:' + NL )
        keys = list(os.environ.keys())
        keys.sort()
        for key in keys:
                fd.write( 2*' ' + key + ': ' + os.environ[key] + NL )
        fd.write( NL )

        sys.stderr = fd
        traceback.print_exc()

        fd.write( NL + '(End of Exception Report)' + NL )
        fd.write( DELIMITER )
        return


def handle_error (
        error_file=sys.stderr,  # file object or file name (optional)
        pageTitle=None          # string; title for page (optional)
        ):
        # Calls message() and dump(fd).
        # If the file does not exist or is not writable, errors will be
        # written to stderr, so look there if you have problems.
        
        if type(error_file) == bytes:
                try:
                        fd = open(error_file,'a')
                except:
                        fd = sys.stderr
        else: # type is file object
                fd = error_file

        if fd == sys.stdout:
                print('<HEAD><TITLE>%s - Exception Report</TITLE>' % \
                        check (pageTitle, TITLE))
                print('</HEAD><BODY BGCOLOR="#FFFFFF"><PRE>')
        else:
                message(pageTitle)

        dump( fd )
        fd.close()
        return


def show_error (
        message,                # string; message to show
        print_message=1,        # boolean; 1 to print message, 0 to return
        pageTitle=None,         # string; title for page (optional)
        pageBanner=None,        # string; banner for page (optional)
        pageFooter=None         # string; footer for page (optional)
        ):
        # Generates a page of HTML containing an error message.

        s = ''' <H2>MGI Query Error</H2>%s''' % message
        if print_message:
                print(s)
        else:
                return s
