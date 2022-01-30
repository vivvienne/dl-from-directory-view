# dl-from-directory-view
An ad hoc python script for (recursively) downloading from urls shown as directory listings.

## Basic usage
1. Open up `dl_from_directory_view.py` in any editor.
2. Edit the line before the last line (`url = ''`), inserting the url to be downloaded between the two 's.
3. Open up any command line terminal and run `dl_from_directory_view.py`. For example in Windows, type the following in Powershell:
	```powershell
	python dl_from_directory_view.py
	```

## To download nonrecursively (only files, no subfolders)
Replace the line `dl_folder(url+item.a['href'])` with `continue`.

## More advanced usage
You can write custom python scripts inside `dl_from_directory_view.py` below the commented line `# CUSTOM PYTHON CODE STARTS HERE`, using the function `dl_folder(url)`. For example,

```python
# CUSTOM PYTHON CODE STARTS HERE
for year in range(1983, 2017):
	...
	url = url_head + 'year_' + str(i) + '/'
	dl_folder(url)
```

## Documentation
See [documentation page](documentation.md).