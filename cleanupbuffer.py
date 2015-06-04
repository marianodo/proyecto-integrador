import os
import fnmatch


search_dir = "/usr/src/web/login/static/photo"
os.chdir(search_dir)
files = filter(os.path.isfile, os.listdir(search_dir))
files = [os.path.join(search_dir, f) for f in files] # add path to each file
files.sort(key=lambda x: os.path.getmtime(x))
files.reverse()
for i,items in enumerate(files):
	if i > 40:
		os.remove(items)