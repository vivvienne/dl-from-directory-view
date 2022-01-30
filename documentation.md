# Documentation
(หน้านี้เป็น[ภาษาไทย](documentation_th.md))

The code consists of three parts
1. [Predefined functions for downloading individual files](https://github.com/vivvienne/dl-from-directory-view/blob/main/documentation.md#1-predefined-functions-for-downloading-individual-files)
2. [Predefined function for parsing directory listings and downloading accordingly](https://github.com/vivvienne/dl-from-directory-view/blob/main/documentation.md#1-predefined-functions-for-downloading-individual-files)
3. [Script specifying what and how to download (provided by the user)](https://github.com/vivvienne/dl-from-directory-view/blob/main/documentation.md#3-script-specifying-what-and-how-to-download-example)

### 0. Imports
```python
import requests
import time
from bs4 import BeautifulSoup
import lxml
import os, os.path
import errno
```

### 1. Predefined functions for downloading individual files
The following functions `mkdir_p(path)` and `safe_open(path, mode, encoding='')` are for safely creating subdirectories during the saving to disk process. The code is adapted from [here](https://stackoverflow.com/questions/23793987/write-file-to-a-directory-that-doesnt-exist).

```python
# defs for safely creating subfolders as needed when saving files to disk
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
```

The following function `dl_file(url, fileout_name)` downloads the file at url `url` and saves it as `fileout_name` (in relative path). You can also configure how long you want to delay after each download finishes, and whether you want status reports ("file saved", "delay for ... seconds") to be shown.

```python
# individual file downloader (with configurable delay and status report messages)
def dl_file(url, fileout_name):
	t0 = time.time()
	r = requests.get(url)
	response_delay = time.time() - t0
	with safe_open(fileout_name,'wb') as fileout_binary:
		fileout_binary.write(r.content)
	set_delay = max(10*response_delay, 1) # second argument is minimum delay; DEFAULT: 1 (sec)
	print('SAVED: '+fileout_name) # status report (optional)
	print('DYNAMIC DELAY = ' + str(10*response_delay) + ', REAL DELAY = ' + str(set_delay)) # status report (optional)
	time.sleep(set_delay)
```

### 2. Predefined function for parsing directory listings and downloading accordingly
The following function `dl_folder(url)` downloads from the url `url`, assuming that the server returns a request to that url as a directory listing. The function operates in an ad hoc manner, namely

1. Save the directory listing file as a local html file.
2. Parse that file using BeautifulSoup, collecting urls for files and folders to be downloaded.
3. Call on `dl_file()` to download individual files and on `dl_folder()` (recursively) to download subfolders.

```python
# directory listing parser and downloader
def dl_folder(url):
	dl_file(url, './parsing_temp.htm') # temporarily save directory listing to html file for parsing
	with open('parsing_temp.htm', encoding='UTF-8') as input_file:
		html_code = ' '.join(input_file.read().splitlines()) # clean up html code before passing it to BeautifulSoup (esp. deleting \n's which cause trouble when using BeautifulSoup's .contents)
		soup = BeautifulSoup(html_code, 'lxml', multi_valued_attributes=None) # pass html code to BeautifulSoup; returns a traversable xml tree
	os.remove('parsing_temp.htm') # delete temporary directory listing file
	
	# use quirk that for directory listing, the first <h1> tag contains the relative path for that directory, which can be used (below) when creating copies of files and folders inside locally
	folder_path = '.' + soup.select_one('h1').get_text().replace('Index of ','') + '/'

	for item in soup.select('tr')[3:-1]: # the slice [3:-1] is to exclude the first 3 row (table header, "parent directory" link, horizontal bar) and the last row (horizontal bar)
		if item.img['alt'] == '[DIR]': # use quirk that rows which are folders start with a specific icon whose alternate text is '[DIR]'
			dl_folder(url+item.a['href']) # to download non-recursively, replace this line with "continue"
		else:
			dl_file(url+item.a['href'], folder_path+item.a['href'])
```

### 3. Script specifying what and how to download (Example)
```python
# CUSTOM PYTHON CODE STARTS HERE
url = '' # THE URL TO DOWNLOAD GOES HERE BETWEEN THE TWO 'S
dl_folder(url)
```