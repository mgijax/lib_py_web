#! ./python
#
# FTPManager.py - A library which handles writing files to the FTP site.
#
# Author: 
#
#       Josh Winslow
#
# Date written: 
#
#       September 2002
#

import tempfile
import rand
import os

tempdir = "/home/jw/public_html/ftp/"
template = "test"
class FTPManager:
    # A FTPManager instance is the gateway for writing all files
    # to the ftp site.
    sessions = {}
    ftpPath = '/home/jw/public_html/ftp/'
    ftpURL = 'http://rohan/~jw/ftp/'   

    def __init__(self,ftpPath,ftpURL,logPath='/logs/ftp/') :
        global tempdir,template
        # Inputs: none.
        # Returns: none.
        # Assumes: none.
        # Effects: sets the variables which control the creation of 
        #          temporary directories and files.
        # Comments: none.    
        self.ftpPath = ftpPath
        self.ftpURL = ftpURL
        self.logPath = logPath
        tempfile.tempdir = self.ftpPath
    
    def createSession(self):
        global tempdir,template
        # Inputs: none.
        # Returns: A sessionID which must be used to write files to the ftp
        #          site and get the url of the directory of the files.
        # Assumes: none.
        # Effects: creates a directory associated with the sessionKey
        # Comments: none.    
        sessionID = rand.rand()
        while sessionID in self.sessions.keys():
            sessionID = rand.rand()
        dirPath = tempfile.mktemp()
        os.mkdir(dirPath)
        self.sessions[sessionID] = dirPath[len(self.ftpPath):]
        return sessionID             

    def writeFiles(self,sessionID, fileDict) :
        # Inputs: a sessionID, obtained from createSession, and a dictionary
        #         of files.  The keys for the dictionary should be filenames;
        #         their values should be the contents of the files.
        # Returns: none.
        # Assumes: none.
        # Effects: writes all the files from fileDict to the FTP site in the
        #          directory specified by the sessionID.
        # Comments: none.    
        dirName = self.sessions[sessionID]
        self.log('Attempting to write %i files for sessionID %s.' % \
                 (len(fileDict.keys()),sessionID))
        for key in fileDict.keys() :
            fd = open(str(self.ftpPath)+str(dirName)+"/"+str(key),'w')
            fd.write(str(fileDict[key]))
            fd.flush()
            fd.close()
            os.system('chmod 777 %s/*' % self.ftpPath+dirName )
            os.system('chgrp www %s' % self.ftpPath+dirName)
            os.system('ghgrp www %s/*' % self.ftpPath+dirName)
        self.log('Writing sucessful!  %i files logged for %s.' %\
                 (len(fileDict.keys()),sessionID))
            
    def closeSession(self,sessionID) :
        # Inputs:  a sessionID, obtained from createSession.
        # Returns: none.
        # Assumes: none.
        # Effects: removes the sessionID from the active list, preventing any
        #          further files from being written.
        # Comments: none.    
        del self.sessions[sessionID]
        
    def getURL(self,sessionID) :
        # Inputs: a sessionID, obtained from createSession.
        # Returns: Returns the URL to the directory associated with the 
        #          sessionID.
        # Assumes: none.
        # Effects: none.
        # Comments: none.
        dirName = self.sessions[sessionID]
        s = str(self.ftpURL)+str(dirName)+'/'
        return s
    def log(self,logText) :
        print 'logging!'
        
