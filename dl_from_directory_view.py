import requests
import time
from bs4 import BeautifulSoup
import lxml
import os, os.path
import errno

# defs for safely creating directories
# adapted from https://stackoverflow.com/questions/23793987/write-file-to-a-directory-that-doesnt-exist
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else: raise

def safe_open(path, mode, encoding=''):
	mkdir_p(os.path.dirname(path))
	if encoding == '':
		return open(path, mode)
	else:
		return open(path, mode, encoding=encoding)

# individual file downloader (with configurable delay)
def dl_file(url, fileout_name):
	t0 = time.time()
	r = requests.get(url)
	response_delay = time.time() - t0
	with safe_open(fileout_name,'wb') as fileout_binary:
		fileout_binary.write(r.content)
	set_delay = max(10*response_delay, 1) # second argument is minimum delay; DEFAULT: 1
	print('SAVED: '+fileout_name) # optional
	print('DYNAMIC DELAY = ' + str(10*response_delay) + ', REAL DELAY = ' + str(set_delay)) # optional
	time.sleep(set_delay)

# folder parser and downloader
def dl_folder(url):
	dl_file(url, './parsing_temp.htm') # temporarily save directory view to file for parsing
	with open('parsing_temp.htm', encoding='UTF-8') as input_file:
		html_code = ' '.join(input_file.read().splitlines()) # clean up html code before passing it to BeautifulSoup (esp. deleting \n's which cause trouble when using BeautifulSoup's .contents)
		soup = BeautifulSoup(html_code, 'lxml', multi_valued_attributes=None) # pass html code to BeautifulSoup; returns a traversable xml tree
	os.remove('parsing_temp.htm') # delete temporary directory view file
	folder_path = '.' + soup.select_one('h1').get_text().replace('Index of ','') + '/' # use quirk that for every (sub)folder's directory view, the h1 line contains the relative path for that sub(folder), which can be used when cloning that sub(folder) locally

	for item in soup.select('tr')[3:-1]: # the slice [3:-1] is for excluding the first 3 row (table header, "parent directory" link, horizontal bar) and the last row (horizontal bar)
		if item.img['alt'] == '[DIR]': # use quirk that lines which are subfolders have a specific icon with alternate text '[DIR]'
			dl_folder(url+item.a['href']) # for downloading non-recursively, replace this line with "continue"
		else:
			dl_file(url+item.a['href'], folder_path+item.a['href'])

url = 'https://saranukromthai.or.th/sound/'
dl_folder(url)