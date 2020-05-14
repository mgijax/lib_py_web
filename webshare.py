# Name: webshare.py
# Purpose: provide access to info about shared web components (images, css,
#       etc.) as defined by an RcdFile.

import string
import rcdlib
import urllib.request, urllib.parse, urllib.error

###-------------------------------###
###--- public global variables ---###
###-------------------------------###

# error messages raised with 'error':

DUPLICATE_ALIAS = 'A alias (%s) was found which is already a name or alias'
RCDFILE_ERROR = 'Error in %s: %s'
READING_ERROR = 'Could not read successfully from %s'
MISSING_FIELD = 'In %s, entry for %s is missing required field %s'
SPACE_ERROR = 'Invalid space character found in %s field: "%s"'

###-------------------------###
###--- private functions ---###
###-------------------------###

def hasSpace (
        s               # string; to be checked to see if it contains ' '
        ):
        # Purpose: check 's' to determine if the string contains a space
        #       character (' ')
        # Returns: 0 if 's' does not contain a space, or 1 if it does 
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing

        return string.find(s, ' ') != -1

def getConfig (url):
        # Purpose: Take the url passed to it, and return a string representing
        #  what that URL returned.
        # Returns: A string of the url's contents
        # Assumes: A valid url being passed to it
        # Effect: Nothing
        # Throws: nothing

        configCGI =  urllib.request.urlopen(url)
        return configCGI.readlines()

###----------------------###
###--- public classes ---###
###----------------------###

class SharedComponent:
        # IS: a web-accessible file which may be useful to multiple web
        #       products.  (an image, a css [style sheet], etc.)
        # HAS: attributes describing the file as needed, like a name, a url,
        #       dimensions for an image, etc.
        # DOES: provides accessor methods for the properties of this component

        ###-----------------------###
        ###--- private methods ---###
        ###-----------------------###

        def __init__ (self,
                name,   # string; preferred identifier for this component
                url     # string; where this component can be retrieved from
                ):
                # Purpose: constructor
                # Returns: nothing
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: Each SharedComponent has, as a minimum, a name and a
                #       URL.  All other fields are optional. PRIVATE.

                # string; preferred identifier for this SharedComponent
                self.name = name

                # string; where this SharedComponent can be retrieved from
                self.url = url

                # list of strings; each is an alternate name for this
                # SharedComponent
                self.aliases = []

                # string or integer; height of this SharedComponent, if
                # available
                self.height = None

                # string or integer; width of this SharedComponent, if
                # available
                self.width = None

                # string; value for the ALT attribute of this SharedComponent
                self.altTag = None
                return

        def addAlias (self,
                alias           # string; alternate name for this SharedComp.
                ):
                # Purpose: add the given 'alias' as an alternate name for this
                #       SharedComponent
                # Returns: nothing
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: only adds the given 'alias' if it is not already
                #       defined for this SharedComponent (no duplicates).
                #       PRIVATE.

                if alias not in self.aliases:
                        self.aliases.append (alias)
                return

        def setHeight (self,
                height          # string or integer; height of this
                                # ...SharedComponent (measured in pixels)
                ):
                # Purpose: sets the height (in pixels) of this SharedComponent
                # Returns: nothing
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: PRIVATE.

                self.height = height
                return

        def setWidth (self,
                width           # string or integer; width of this
                                # ...SharedComponent (measured in pixels)
                ):
                # Purpose: sets the width (in pixels) of this SharedComponent
                # Returns: nothing
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: PRIVATE.

                self.width = width
                return

        def setAltTag (self,
                altTag          # string; value for ALT attribute of any HTML
                                # ...tag produced
                ):
                # Purpose: sets the value of the ALT attribute for any HTML
                #       tag produced for this SharedComponent
                # Returns: nothing
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: PRIVATE.

                self.altTag = altTag
                return

        ###----------------------###
        ###--- public methods ---###
        ###----------------------###

        def getName (self):
                # Purpose: retrieve the current preferred name for this
                #       SharedComponent
                # Returns: string
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing

                return self.name

        def getUrl (self):
                # Purpose: retrieve the URL by which this SharedComponent can
                #       be accessed
                # Returns: string
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing

                return self.url

        def getHeight (self):
                # Purpose: get the height of this SharedComponet in pixels, if
                #       known
                # Returns: string or integer; height of this SharedComponent
                #       in pixels, or None if not known
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: The returned value is whatever type was passed into
                #       setHeight()

                return self.height

        def getWidth (self):
                # Purpose: get the width of this SharedComponet in pixels, if
                #       known
                # Returns: string or integer; width of this SharedComponent
                #       in pixels, or None if not known
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: The returned value is whatever type was passed into
                #       setWidth()

                return self.width

        def getAltTag (self):
                # Purpose: get the ALT attribute for this SharedComponent
                # Returns: string or None if one has not been set
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing

                return self.altTag

        def getAliases (self):
                # Purpose: get non-preferred names for this SharedComponent
                # Returns: list of strings, each a non-preferred name.  The
                #       list will be empty if this SharedComponent has no
                #       aliases.
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing

                return self.aliases

        def getImgTag (self):
                # Purpose: get an HTML <IMG...> tag representing this
                #       SharedComponent
                # Returns: string
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: If you'd rather not call this directly, you may use
                #       self.getHtmlTag() in case this component is a style
                #       sheet.

                # start with the required piece
                parts = [ 'IMG SRC="%s" BORDER=0' % self.url ]

                # add the optional pieces as needed

                if self.height:
                        parts.append ('HEIGHT="%s"' % self.height)
                if self.width:
                        parts.append ('WIDTH="%s"' % self.width)
                if self.altTag:
                        parts.append ('ALT="%s"' % self.altTag)

                # build and return the complete tag

                return '<%s>' % string.join(parts, ' ')

        def getStyleSheetTag (self):
                # Purpose: get an HTML <LINK...> tag which loads this
                #       SharedComponent as a style sheet
                # Returns: string
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: If you'd rather not call this directly, you may use
                #       self.getHtmlTag() in case this component is an image.

                return '<LINK REL="stylesheet" HREF="%s" TYPE="text/css">' % self.url

        def getHtmlTag (self):
                # Purpose: get the HTML tag appropriate for this component
                # Returns: string; an HTML tag
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: We determine what tag to use according to the
                #       filename's extension in self.url.  If it is '.css',
                #       then we assume this component is a style-sheet.
                #       Otherwise, we assume it is an image.

                pos = string.rfind (self.url, '.')
                if pos != -1:
                        if string.lower(self.url[pos:]) == '.css':
                                return self.getStyleSheetTag()

                return self.getImgTag()

        def getRcd (self):
                # Purpose: get a string representing this SharedComponent as
                #       a Rcd (one record in an RcdFile)
                # Returns: string
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: We have no way to directly get the original Rcd entry
                #       for this image, so we reconstruct it here from the
                #       data in 'self'.

                # list of output lines, starting with the two required fields
                lines = [
                        '[',
                        'name = %s' % self.name,
                        'url = %s' % self.url,
                        ]

                # add the optional fields if they are defined

                if self.height:
                        lines.append ('height = %s' % self.height)
                if self.width:
                        lines.append ('width = %s' % self.width)
                if self.altTag:
                        lines.append ('altTag = %s' % self.altTag)
                for alias in self.aliases:
                        lines.append ('alias = %s' % alias)

                # close the rcd entry and join the lines into a single string

                lines.append (']')
                return string.join (lines, '\n')

class SharedComponents:
        # IS: a mapping from string names/aliases to their corresponding
        #       SharedComponent objects.
        # HAS: a set of SharedComponent objects, each identified by a name and
        #       zero or more aliases
        # DOES: retrieves a SharedComponent when given a name or alias
        # Notes: Each name/alias must be unique.  If any duplicates appear, an
        #       exception will be raised at the time of instantiation.

        def __init__ (self,
                filepath        # string; path to the RcdFile which defines
                                # ...the shared web components
                ):
                # Purpose: constructor
                # Returns: nothing
                # Assumes: nothing
                # Effects: reads from 'filepath' in the file system
                # Throws: 'error' if any errors occur

                # maps from an alias (string) to the preferred name (string)
                # for its SharedComponent
                self.aliasToName = {}

                # maps from a name (string) to its associated SharedComponent
                self.nameToComponent = {}

                # string; path to the RcdFile with the definitions
                self.rcdFilePath = filepath

                # load the RcdFile from the path given

                try:
                        rcdfile = rcdlib.RcdFile (filepath, rcdlib.Rcd, 'name')
                except message:
                        raise Exception(RCDFILE_ERROR % (filepath, str(message)))

                # each name or alias cited in the RcdFile should appear as a
                # key in 'namesAliases' so that we can use it to check for
                # duplicates.  Initialize it to start with all the names.

                namesAliases = {}
                for name in list(rcdfile.keys()):
                        if hasSpace(name):
                                raise Exception(SPACE_ERROR % ('name', name))
                        namesAliases[name] = 1

                # walk through each defined rcd (one per shared component):

                for (name, rcd) in list(rcdfile.items()):

                        # check for the required 'url' field

                        url = rcd['url']
                        if not url:
                                raise Exception(MISSING_FIELD % (
                                                filepath, name, 'url'))

                        # instantiate a new SharedComponent

                        component = SharedComponent (name, url)

                        # go through any aliases: checking for duplication,
                        # mapping them to the name, and adding them to the
                        # 'component'

                        aliases = rcd.getAsList('alias')
                        for alias in aliases:
                                if alias in namesAliases:
                                        raise Exception(DUPLICATE_ALIAS % alias)
                                if hasSpace(alias):
                                        raise Exception(SPACE_ERROR % ('alias',
                                                alias))

                                self.aliasToName[alias] = name
                                component.addAlias(alias)
                                namesAliases[alias] = 1 

                        # handle the optional height, width, and alt fields

                        height = rcd['height']
                        width = rcd['width']
                        altTag = rcd['alt']

                        if height:
                                component.setHeight(height)
                        if width:
                                component.setWidth(width)
                        if altTag:
                                component.setAltTag(altTag)

                        # associate the complete 'component' with its 'name'

                        self.nameToComponent[name] = component
                return

        def get (self,
                nameOrAlias     # string; name or alias for a SharedComponent
                ):
                # Purpose: get the SharedComponent corresponding to the given
                #       'nameOrAlias'
                # Returns: SharedCompoment, or None if one is not associated
                #       with 'nameOrAlias'
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing

                # first check for a direct association by name

                if nameOrAlias in self.nameToComponent:
                        return self.nameToComponent[nameOrAlias]

                # failing that, look for an alias which is mapped to a name
                # we can use to look up a SharedComponent

                if nameOrAlias in self.aliasToName:
                        name = self.aliasToName[nameOrAlias]
                        return self.nameToComponent[name]

                return None             # 'nameOrAlias' was unknown

        def getNames (self):
                # Purpose: get a list of preferred names for SharedComponent
                #       objects
                # Returns: list of strings, each a name for a SharedComponent;
                #       list may be empty
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing

                return list(self.nameToComponent.keys())

        def getAliases (self):
                # Purpose: get a list of non-preferred names for
                #       SharedCompoment objects
                # Returns: list of strings, each a name for a SharedCompoment;
                #       list may be empty
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing

                return list(self.aliasToName.keys())

        def getRcdFile (self):
                # Purpose: get the RcdFile used to define this set of
                #       SharedComponent objects
                # Returns: string; contents of the original RcdFile joined
                #       into a single string.
                # Assumes: nothing
                # Effects: re-reads the file from the file system
                # Throws: 'error' if we have problems re-reading the file

                try:
                        fp = open (self.rcdFilePath, 'r')
                        lines = fp.readlines()
                        fp.close()
                except:
                        raise Exception(READING_ERROR % self.rcdFilePath)

                return string.join (lines, '')
