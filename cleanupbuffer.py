#!/usr/bin/python

import os
import fnmatch
count = 0
for root, dir, files in os.walk("/usr/src/web/login/static/photo/"):
        files.sort()
        files.reverse()
        for items in fnmatch.filter(files, "*"):
                count = count +1
                if count > 40:
                	os.remove("/usr/src/web/login/static/photo/" + items)
                	
        