import sys
from types import *

TEMPLATEHEAD = 'templateHead.html'
TEMPLATEBODYSTART = 'templateBodyStart.html'
TEMPLATEBODYSTOP = 'templateBodyStop.html'


def getFile (path):
	doc = open(path, "r")
	results = ''
	for line in doc:
		results = results + line
	doc.close()
	return results

class Template:
		
	title = "<TITLE> Mouse Genome Informatics </TITLE>"
	helpLink = ""
	headerText = "Mouse Genome Informatics"
	headerSubText = ""
	body = []
	contentType = 'Content-type: text/html\n\n'
	javaScript_url = []
	javaScript = []
	css = []
	printType = 1

	def __init__ (self, path = 'test/'):
		self.path = path
		return
		
##	Content Type Section (This is Content-type: text/html by default)
	
	def getContentType(self):
		return self.contentType
	
	def setContentType(self, type):
		self.contentType = type

##	Page Title Section (This is what appears in the title bar)
	
	def getTitle(self):
		return self.title
	
	def setTitle(self, Title):
		self.title = '<TITLE> ' + Title + '</TITLE>'


##	Body Section
		
	def getBody(self):
		return self.body
		
	
	def setBody(self, Text):
		if type(Text) == StringType:
			self.body = [Text]
		else:
			self.body = Text
	
	def appendBody(self, Text):
		if type(Text) == StringType:
			self.body = self.body + [Text]
		else:
			self.body = self.body + Text	

## 	In the rare case that you dont want the Content Type tag printing out
##	invoke this method.

	def noContentType(self):
		self.printType = 0

##	The Custom CSS Sections (This Needs to be finished up!)
	
	def setCSS(self, url):
		if type(url) == StringType:
			self.css = ['<link rel="stylesheet" type="text/css" href="'+ url +'"/>']
		else:
			for eachUrl in url:
				self.css = self.css + ['<link rel="stylesheet" type="text/css" href="'+ eachUrl +'"/>']


	def appendCSS(self, url):
		if type(url) == StringType:
			self.css = self.css + ['<link rel="stylesheet" type="text/css" href="'+ url +'"/>']
		else:
			for eachUrl in url:
				self.css = self.css + ['<link rel="stylesheet" type="text/css" href="'+ eachUrl +'"/>']	
			
	def getCSS(self):
		return self.css
		
##	The Custom Javascript Include section. (This needs to be finished up!)
		
	def setJavaScriptInclude(self, url):
		if type(url) == StringType:
			self.javaScript_url = ['<script type="text/javascript" src="'+ url +'"></script>']
		else:
			for eachUrl in url:
				self.javaScript_url = self.javaScript_url['<script type="text/javascript" src="'+ eachUrl +'"></script>']
		
	def getJavaScriptInclude(self):
		return self.javaScript_url
		
	def appendJavaScriptInclude(self, url):
		if type(url) == StringType:
			self.javaScript_url = self.javaScript_url['<script type="text/javascript" src="'+ url +'"></script>']
		else:
			for eachUrl in url:
				self.javaScript_url = self.javaScript_url + ['<script type="text/javascript" src="'+ eachUrl +'"></script>']		

##	The Custom Script section. (This needs to be finished up!)
		
	def setJavaScript(self, script):
		if type(script) == StringType:
			self.javaScipt = [script]
		else:
			self.javaScript = script	
		
	def getJavaScript(self):
		return self.javaScript
		
	def appendJavaScript(self, script):
		if type(script) == StringType:
			self.javaScipt = [script]
		else:
			self.javaScript = script

##	This is for the help link, by setting this a div section will appear which will then generate an image on the page
##	that leads to the userdocs.
		
	def getHelpLink(self):
		return self.helpLink

	def setHelpLink(self, url):
		self.helpLink = url

##	Set the headerbards main text section (The first span atm)

	def getHeaderBarMainText(self):
		return self.headerText
	
	def setHeaderBarMainText(self, text):
		self.headerText = text

##	Set the subheader text (The second span atm)
		
	def getHeaderBarSubText(self):
		return self.headerSubText
	
	def setHeaderBarSubText(self, text):
		self.headerSubText = text	

##	Template sections.  This pulls in our mgi standard templates.

	def getTemplateHead(self):
		return getFile(self.path+TEMPLATEHEAD)

	def getTemplateBodyStart(self):
                return getFile(self.path+TEMPLATEBODYSTART)

	def getTemplateBodyStop(self):
                return getFile(self.path+TEMPLATEBODYSTOP)
                
##	Return JUST the title, javaScript, Css, templateHead and TemplateBodyStart                
## 	The Javascript and CSS part has yet to be implemented.

	def getNavigation(self):
		text = self.getContentType()
		text = text + self.getTemplateHead()
		text = text + self.getTitle()
		if len(self.css) != 0:
			for item in self.css:
				text = text + item
		if len(self.javaScript_url) != 0:
			for item in self.javaScript_url:
				text = text + item
		if len(self.javaScript) != 0:
			for item in self.javaScript:
				text = text + item					
		text = text + self.getTemplateBodyStart()
		return text

##	Return JUSt the headerbar.  This is used in the construction of the next method mostly.
	
	def getHeaderBar(self):
		if self.helpLink != '':
			head = '<div id="titleBarWrapper" userdoc="' + self.getHelpLink() +'">\n'	
		else:
			head = '<div id="titleBarWrapper">\n'
		head = head + '<span class="titleBarMainTitle">'
		head = head + self.getHeaderBarMainText()
		head = head + '</span><br>\n'
		if self.headerSubText != '':
			head = head + '<span class="titleBarSubTitle">'
			head = head + self.getHeaderBarSubText()
			head = head + '</span>\n'
		head = head + '</div>\n'
		return head

##	Return both the navigation, and the headerbar.

	def getNavigationAndHeader(self):
		head = self.getNavigation()
		head = head + self.getHeaderBar()
		return head

##	This method needs to be removed, but its being kept in for backwards compatability atm
##	until I can retrofit my old code.

	def getFullHeader(self):
		head = self.getNavigation()
        	head = head + '<h2 id="titleBar" '
        	if self.helpLink != '':
               		head = head + ' userdoc="' + self.getHelpLink() + '"'
        	head = head + '> ' + self.getHeaderBarMainText() + '</h2>'
        	return head

##	Return the whole document

	def getFullDocument(self):
		head = self.getNavigationAndHeader()
		if len(self.body) != 0:
			for item in self.body:
				head = head + item	
		head = head + self.getTemplateBodyStop()
		return head

##	Return the whole document, sans a header.
		
	def getFullDocumentNoHeader(self):
		head = self.getNavigation()
		if len(self.body) != 0:
			for item in self.body:
				head = head + item
		head = head + self.getTemplateBodyStop()
		return head