# mgi_cgi.py
# Support for processing HTML form content.
#
# INTRODUCTION
# 
# This module provides a class (FieldStorage) for processing form content.  A
# FieldStorage instance is a dictionary-like object with the field names as
# keys and Field (another class) objects as values.  Field objects have name,
# op and value attributes.
#
# The FieldStorage class will look for field names beginning with 'not:' and
# 'op:', processing the values along with the field value accordingly.  The
# result will be a Field object with op and value attributes that are
# available for generating SQL.
#
# USING THE FormContent CLASS
#
# See the web interface CGI scripts for examples.  You will probably want to
# create DEFAULT_FIELDS and DEFAULT_TYPES dictionaries as is done there.
 
# Imports
# =======
 
import cgi
import urllib
import string
import copy
import regsub
from types import *


# Global Constants
# ================

error = 'FieldStorageError'

def processDisplayFields(displayFields,nots) :
    # Purpose: Convert displayFields into a slightly more user
    #          readable format by modifying some operators and values.
    # Returns: a modified version of displayFields
    # Assumes: nothing
    # Effects: nothing
    for key in displayFields.keys():
        if displayFields[key]['val'] is None:
            if displayFields[key]['op'] == 'is null':
                displayFields[key]['val'] = 'null'
                displayFields[key]['op'] = 'is'
	    elif displayFields[key]['op'] == 'is not null':
		displayFields[key]['val'] = 'not null'
		displayFields[key]['op'] = 'is'
            else:
                del displayFields[key]  
    # Modify operators if NOT has been checked.
    for key in nots:
        if displayFields.has_key(key):
            if displayFields[key]['op'] == '=':
                displayFields[key]['op'] = '!='
            elif displayFields[key]['op'] == 'is':
                displayFields[key]['op'] = 'is not'
            else: # The operator is 'like', 'begins', etc.
                displayFields[key]['op'] = 'not '+displayFields[key]['op']
    return displayFields       

# Classes
# =======

class Field:

    opList = {
        '='         :'equals',
        'begins'    :'begins with',
        '!='        :'is not equal to',
    }


    def __init__(self, name, op, value):
        self.name = name
        self.op = op
        self.value = value

    def __repr__(self) :
        rep = ''
        if len(self.name) > 0  :
            rep = '<B>'+str(self.name) + ':</B> '
            if self.op != None and self.value != None:
                op = self.op
                if self.op in self.opList.keys() :
                    op = self.opList[self.op]
                rep = rep + str(op) + ' <i>' + str(self.value) + '</i>'
        return rep


class FieldStorage:
    def __init__(self, originalFields={}, fieldTypes={}):
        # Store a safe copy for posible later use
        self.originalFields = copy.deepcopy(originalFields)
        # Make sure we don't chnage the originals in case the caller uses them
        fields = copy.deepcopy(originalFields)

        delim = ':'
        #get the arguments from standard in
        form = cgi.FieldStorage()

        # preserve the original submission from the form or URL
        self.cgiFieldStorage = form

        nots = []
        keys = form.keys()

        # 1st pass - Get operators and values.   
        for key in keys:
            # due differences in the way browsers use escape characters
            # (or don't) in the text they submit, we first retrieve the
            # value and then unquote the key (TR 2739)

            item = form[key]
            key = urllib.unquote(key)
            # determine the type of the argument.  If none specified,
            # use the default
            if string.find(key, delim) != -1:
                fieldType = string.split(key, delim)[0]
                fieldName = string.split(key, delim)[1]
            elif fieldTypes.has_key(key):
                fieldType = fieldTypes[key]
                fieldName = key
            else:
                raise KeyError, key

            if fieldType == 'op':
                fields[fieldName]['op'] = item.value
            elif fieldType == 'not':
                nots.append(fieldName)
            elif fieldType == 'string':
                fields[fieldName]['val'] = item.value
            elif fieldType == 'int':
                fields[fieldName]['val'] = \
                    string.atoi(item.value)
            elif fieldType == 'float':
                try:
                    fields[fieldName]['val'] = \
                        string.atof(item.value)
                except:
                    raise error, 'Unable to convert the ' \
                        + 'value "' + str(item.value) \
                        + '" to a number for field "' \
                        + fieldName + '".'
            elif fieldType == 'int_list':
                if type(item) is ListType:
                    fields[fieldName]['val'] = []
                    for miniItem in item:
                        fields[fieldName]['val'].append(
                            string.atoi(
                                miniItem.value))
                elif type(item.value) is StringType:
                    fields[fieldName]['val'] = []
                    for s in string.split(item.value, ','):
                        fields[fieldName]['val'].append(
                            string.atoi(s))
                else: # It's an instance
                    fields[fieldName]['val'] = \
                        item.value
            elif fieldType == 'string_list':
                if type(item) is ListType:
                    fields[fieldName]['val'] = []
                    for miniItem in item:
                        fields[fieldName]['val'].append(
                            miniItem.value)
                elif type(item.value) is StringType:
                    item.value = regsub.gsub(', ', ',',
                        item.value)
                    fields[fieldName]['val'] = \
                        string.split(item.value, ',')
                else: # It's an instance
                    fields[fieldName]['val'] = \
                        item.value
            elif fieldType == 'option_list':
                if type(item) is ListType:
                    fields[fieldName]['val'] = []
                    for miniItem in item:
                        fields[fieldName]['val'].append(
                            miniItem.value)
                else: # It's an instance
                    fields[fieldName]['val'] = [item.value]
    
        # Now that the initial construction is taken care of, save the 
        # operators and values before they are made into SQL.
        displayFields = copy.deepcopy(fields)
        # Modify the operators for display
        self.displayFields = processDisplayFields(displayFields,nots)
      
        # 2nd pass - Modify values as necessary.  Delete field if None.
        for key in fields.keys():
            if fields[key]['val'] is None:
                if fields[key]['op'] == 'is null':
                    fields[key]['val'] = 'null'
                    fields[key]['op'] = 'is'
		elif fields[key]['op'] == 'is not null':
                    fields[key]['val'] = 'null'
                    fields[key]['op'] = 'is not'
                else:
                    del fields[key]
            elif fields[key]['op'] == 'begins':
                fields[key]['op'] = 'like'
                if type(fields[key]['val']) is StringType:
                    fields[key]['val'] = fields[key]['val']\
                        + '%'
                elif type(fields[key]['val']) is ListType:
                    for i in range(len(fields[key]['val'])):
                        fields[key]['val'][i] = \
                            fields[key]['val'][i] \
                            + '%'
            elif fields[key]['op'] == 'ends':
                fields[key]['op'] = 'like'
                if type(fields[key]['val']) is StringType:
                    fields[key]['val'] = '%' \
                        + fields[key]['val']
                elif type(fields[key]['val']) is ListType:
                    for i in range(len(fields[key]['val'])):
                        fields[key]['val'][i] = '%' \
                            + fields[key]['val'][i]
            elif fields[key]['op'] == 'contains':
                fields[key]['op'] = 'like'
                if type(fields[key]['val']) is StringType:
                    fields[key]['val'] = '%' \
                        + fields[key]['val'] \
                        + '%'
                elif type(fields[key]['val']) is ListType:
                    for i in range(len(fields[key]['val'])):
                        fields[key]['val'][i] = '%' \
                            + fields[key]['val'][i]\
                            + '%'

        # Modify operators if NOT has been checked.
        for key in nots:
            if fields.has_key(key):
                if fields[key]['op'] == '=':
                    fields[key]['op'] = '!='
                elif fields[key]['op'] == 'is':
                    fields[key]['op'] = 'is not'
                else: # The operator is 'like', 'begins', etc.
                    fields[key]['op'] = 'not ' \
                        + fields[key]['op']

        self.fields = fields

    def __getitem__(self, key):
        op = self.fields[key]['op']
        value = self.fields[key]['val']
        name = key

        return Field(name, op, value)

    def addField (self,
        key,        # string; name of field
        op,     # string; operator
        value       # variable type; value of field
        ):
        # Purpose: allow us to programmatically add additional fields
        #   to the FieldStorage object, even though they may not
        #   have come in as input parameters
        # Returns: nothing
        # Assumes: nothing
        # Effects: adds an 'op'erator and 'value' for a new
        #   parameter 'key', or overwrites the old ones if an
        #   entry for 'key' already exists
        # Throws: nothing
        # Notes: I added this method as a result of TR 2097.  It
        #   became useful to add default parameter values in a
        #   different way for special cases, like querying
        #   expression data by edinburghKey.

        self.fields[key] = { 'op' : op, 'val' : value }
        return

    def keys(self):
        return self.fields.keys()


    def has_key(self, key):
        return self.fields.has_key(key)


    def __repr__(self):
        s = '<dl>\n'
        keys = self.fields.keys()
        keys.sort()
        for key in keys:
            s = s + '<dt>' + key + '\n'
            s = s + '<dd>' + str(self.fields[key]) + '\n'
        s = s + '</dl>\n'
        return s
        
    def getCgiFieldStorage (self):
            # Purpose: get the cgi.FieldStorage object for the fields that
            #       were actually submitted (not including the extra
            #       parsing or the default values handled in the
            #       constructor for mgi_cgi.FieldStorage)
            # Returns: cgi.FieldStorage -- this is a copy, so you can
            #       modify it without worrying about side effects
            # Assumes: nothing
            # Effects: nothing
            # Throws: nothing

            return copy.copy(self.cgiFieldStorage)

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
