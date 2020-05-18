# mgdhtml.py
# functions for writing standard HTML elements to sys.stdout, and assorted
#       other HTML-related functions

import sys
import os
import string
import types
import time
import cgi
import urllib.request, urllib.parse, urllib.error
import random
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
url_unescape = urllib.parse.unquote   # For backward compatability


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
Copyright &#169 1996, 1999, 2002 by The Jackson Laboratory<BR>
All Rights Reserved<BR>
'''
        return s


def mgiRetrieve():
        """Returns a string representation of the retrieve button for forms."""

        s = '''\
<HR>
<INPUT TYPE="submit" VALUE="Search"> <INPUT TYPE=reset>
<HR>
'''
        return s


def mgiMaxReturn (
        fieldname = '*limit',           # string; name of the HTML form field
        counts = [ 100, 500, 0 ],       # list of integers; count options
        default = 500                   # integer; which count is the default?
        ):
        # Purpose: returns a string representing the "maximum number of items
        #       returned" section of an HTML form
        # Returns: string
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing
        # Notes: The default value for each parameter above is the standard
        #       set for the MGI WI, as of the 2.8 release.  A count of 0 is
        #       interpreted to be 'No limit'.

        unchecked = '<INPUT TYPE="radio" NAME="%s" VALUE="%s">%s'
        checked = '<INPUT TYPE="radio" NAME="%s" VALUE="%s" CHECKED>%s'

        list = [ '<B>Max number of items returned:</B>' ]

        for count in counts:
                if count == default:
                        template = checked
                else:
                        template = unchecked

                if count == 0:
                        list.append(template % (fieldname, count, 'No limit'))
                else:
                        list.append(template % (fieldname, count, count))

        list.append ('<BR>')
        return string.join (list, '\n')


def get_fields(content = None):
        """Processes fields from an HTML form.
        #
        # Requires:
        #       content -- A string containing form content.  A value of None
        #               (default) means to read from sys.stdin.
        #
        # Effects:
        #       - Reads from sys.stdin
        #       
        # Notes:
        #       This needs work big-time. -- gtc
        #       The web interface (WI) is mostly through a migration away from
        #       using this function.  Its use should probably be discouraged.
        #       -- jsb
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
#       Grabs all of fields that have a "checked" NOT operator.
#
                        negates[type[1]] = mapping[1]
                elif type[0] == 'list':
                        key = type[1]
                        if (key in fields) == 0:
                                fields[key] = []
                        fields[key].append(mapping[1])
                else:
                        fields[type[1]] = mapping[1]
                        types[type[1]] = type[0]
        for key in list(fields.keys()):
                if key in types and key in operators:
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
#       Where NOT has been used alter the operator accordingly.
#
        for key in list(negates.keys()):
                if key in operators:
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
                print('NULL')
        else:
                print(str(value))
        print('<BR>')


def escape(html):
        """Escapes '&', '<' and '>' characters as SGML entities.
        #
        # Note:
        #       This was repaired in 10/97 to escape the '&' properly.  It was
        #       not being done before that.
        """
        if html is not None and type(html) is bytes:
                html = cgi.escape(html)
        else:
                html = ''
        return html

###--- Other Functions ---###

def doSubSupTags (
        s               # string; source string you want marked up
        ):
        # Purpose: take string 's' and replace <...> with HTML superscript
        #       tags, and >...< with HTML subscript tags
        # Returns: marked-up copy of 's'
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing
        # Notes: In an effort to be resilient, this function does the best it
        #       can in the event of mismatched > and < signs.  It converts
        #       the most-local (innermost) pairs and converts any non-matched
        #       > signs to &gt; and any < signs to &lt; for the user's
        #       browser.  This function never creates nested tags.  See the
        #       examples.
        # Examples:
        #       doSubSupTags('Do >subscript< here')
        #         ==> 'Do <SUB>subscript</SUB> here'
        #       doSubSupTags('Text >down< then <up>')
        #         ==> 'Text <SUB>down</SUB> then <SUP>up</SUP>'
        #       doSubSupTags('My > >best>guess< <is>here<')
        #         ==> 'My &gt; &gt;best<SUB>guess</SUB> <SUP>is</SUP>here&lt;'

        gtPos = None    # int; position of last unmatched > found in 's'
        ltPos = None    # int; position of last unmatched < found in 's'
        lens = len(s)   # int; length of string 's'
        t = []          # list of strings; collects elements to be used in
                        #       building the string to return

        for i in range(0, lens):
                t.append (s[i])         # each element of 't' begins as a
                                        # single character from 's'

                if s[i] == '<':
                        # if we've previously seen a > to match this <,
                        # then replace both with subscript tags.

                        if gtPos != None:
                                t[i] = '</SUB>'
                                t[gtPos] = '<SUB>'
                                gtPos = None

                        # otherwise, just remember this < so we can hopefully
                        # find a matching > later.  (Replace a previously seen
                        # < with &lt;)

                        else:
                                if ltPos != None:
                                        t[ltPos] = '&lt;'
                                ltPos = i

                elif s[i] == '>':
                        # if we've previously seen a < to match this >,
                        # then replace both with superscript tags.

                        if ltPos != None:
                                t[i] = '</SUP>'
                                t[ltPos] = '<SUP>'
                                ltPos = None

                        # otherwise, just remember this > so we can hopefully
                        # find a matching < later.  (Replace a previously seen
                        # > with &gt;)

                        else:
                                if gtPos != None:
                                        t[gtPos] = '&gt;'
                                gtPos = i

        # if we ended with a < or > still unmatched, convert it as needed

        if gtPos != None:
                t[gtPos] = '&gt;'
        if ltPos != None:
                t[ltPos] = '&lt;'

        # join the elements in 't' into a single string and return it

        return string.join (t, '')

def stripHtmlTags (
        source,         # string or list of strings; text to have its HTML
                        #       tags removed
        subLF = 0       # boolean (0/1); 1 to substitue a newline character
                        #       for any <BR> or <P> tags found
        ):
        # Purpose: strip any HTML tags out of the 'source', so that it is left
        #       as plain text
        # Returns: string or list of strings, whichever type was passed in
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing

        # delimiter = what string is used to join the items of 'source' into
        #       a single string?  (or None, if 'source' is already a string)
        # s = what string should we strip the HTML tags from?

        if type(source) == list:
                s, delimiter = joinUnique (source)
        else:
                s = source
                delimiter = None

        # if we need to replace <BR> and <P> tags with line break characters,
        # then do so before we strip out all the tags.

        if subLF:
                s = s.replace('<[bB][rR]>', '\n')
                s = s.replace('<[pP]>', '\n')

        # finally, strip the HTML tags, leaving in place any delimiters in
        # mid-tag.  (This could happen if a tag was split across multiple
        # strings in 'source'.)

        s = deleteTags (s, delimiter)

        if delimiter:
                return string.split (s, delimiter)
        return s

###--- Private Functions ---###

def joinUnique (
        list            # list of strings to join together
        ):
        # Purpose: join the strings of 'list' into a single string, using
        #       a delimiter which does not already occur in any of the
        #       strings in 'list'
        # Returns: two-item tuple:  (string created, string delimiter used)
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing

        separator = None        # string; the delimiter we'll use to join

        # let's have a set of standard separators to try first...

        standard_separators = [ '@@', '##', '&&', ';;', '..', '::' ]

        for sep in standard_separators:

                # if 'sep' occurs in one of the strings of the 'list', then
                # break out and try the next 'standard_separator'

                for item in list:
                        if string.find (item, sep) != -1:
                                break

                # if this loop ended normally (without a 'break'), then we
                # found a delimiter that will work.  Remember it and break
                # out of the outer loop.

                else:
                        separator = sep
                        break

        # if we've not yet found a delimiter, then all of the standard ones
        # occurred somewhere in the 'list'.  We'll now simply add random
        # letters to a string until we arrive at one which doesn't occur in
        # one of the strings of 'list'.

        if not separator:
                sep = random.choice (string.letters)
                while 1:
                        # we need to see if the current 'sep' occurs in a
                        # string of 'list'.

                        for item in list:

                                # if it occurs, then add a new random letter
                                # to the end and try again.

                                if string.find (item, sep) != -1:
                                        sep = sep + \
                                                random.choice (string.letters)
                                        break

                        # if the 'for' loop terminates normally, then we have
                        # found a delimiter we can use.  Remember it and break
                        # out of the 'while' loop.

                        else:
                                separator = sep
                                break

        # finally, join the list into a string and return the two-item tuple

        return string.join (list, separator), separator

def deleteTags (
        s,              # string from which to remove HTML tags
        delimiter       # string used as a delimiter to join multiple other
                        #       strings together into 's'.  may be None.
        ):
        # Purpose: remove all HTML tags from string 's'
        # Returns: string
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing
        # Notes: if the 'delimiter' occurs in an HTML tag in 's', we should
        #       leave the delmiter in place and just remove the rest of the
        #       tag.  This ensures that the string may be split apart properly
        #       by the calling routine.

        t = ''          # string we're building to return
        openTags = []   # string; stack of tags that are still open, but which
                        #       are not the most recently opened tag
        tag = None      # string; currently open tag

        # we need to go through each character 'c' in our source string 's'...

        for c in s:
                if c == '<':
                        # if we find an '<' while we're already in an open
                        # tag, then store the already-open one in 'openTags'
                        # and start collecting characters for the new 'tag'.

                        if tag:
                                openTags.append (tag)
                        tag = '<'

                elif c == '>' and tag:
                        # if we've reached the close of a tag, then we need
                        # to strip it down to just the delimiters it contains
                        # (or an empty string if we're not using a delimiter)

                        if delimiter:
                                stripped = delimiter * \
                                        string.count (tag, delimiter)
                        else:
                                stripped = ''

                        # if we've stored previously opened tags, then pop the
                        # most recent one from the stack and add 'stripped' to
                        # it.  Otherwise, we've finished the outermost tag so
                        # we can add it to 't'.

                        if openTags:
                                tag = openTags[-1]
                                del openTags[-1]
                                tag = tag + stripped
                        else:
                                t = t + stripped
                                tag = None
                elif tag:
                        # we're just collecting letters for the currently
                        # open tag.

                        tag = tag + c
                else:
                        # we're not in a tag; we're just collecting characters
                        # for the string we're producing -- 't'

                        t = t + c

        # if we reached the end of the string with an open tag, then it may
        # have just been a < sign at the start.  Just add the string to t.

        if tag:
                t = t + tag
        return t

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
# Copyright (c) 1996, 1999, 2002 by The Jackson Laboratory
# All Rights Reserved
#
