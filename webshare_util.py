#! ./python

# downloads from the webshare product data about shared web components.  This
# consists of an Rcd file which we will store locally within the WI.

import sys
import string
import httpReader
import os


def saveWebshare(filePath, baseURL) :

# open the output file for writing

    try:
        f = open(filePath, "w")
    except:
        print("Error opening data/webshare.rcd file")
        sys.exit(1)

    f.write('# Note: This file is machine-generated, do not edit!\n')

    url = os.path.join(baseURL, 'components.cgi?format=rcd')

    try:
        lines, errors = httpReader.getURL (url)
        if errors:
            print("Errors occurred when reading from webshare product:")
            for error in errors:
                print("    " + error)
            raise IOError

        # HTTP headers come down with the response, so we need to skip down
        # until we get past the blank line which separates the headers from
        # the body

        lines = list(map (string.strip, lines))
        if '' in lines:
            pos = lines.index ('')
            lines = lines[pos+1:]

        for line in lines:
            f.write(line + '\n')
        print("Updated %s file" % filePath)
        f.close()

    except:
        print("Error generating data/webshare.rcd file; please try again.")
        f.close()
        sys.exit(1)

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

