# Documentation
(This page in [English](documentation.md).)

โค้ดมี 3 ส่วน
1. [นิยามฟังก์ชันที่ใช้โหลดไฟล์เดี่ยวๆ](https://github.com/vivvienne/dl-from-directory-view/blob/main/documentation_th.md#1-นิยามฟังก์ชันที่ใช้โหลดไฟล์เดี่ยวๆ)
2. [นิยามฟังก์ชันที่ใช้อ่าน directory listing และโหลดไฟล์ตามผลอ่าน](https://github.com/vivvienne/dl-from-directory-view/blob/main/documentation_th.md#2-นิยามฟังก์ชันที่ใช้อ่าน-directory-listing-และโหลดไฟล์ตามผลอ่าน)
3. [สคริปของผู้ใช้ที่ระบุว่าจะโหลดอะไรอย่างไร]()

### 0. imports
```python
import requests
import time
from bs4 import BeautifulSoup
import lxml
import os, os.path
import errno
```

### 1. นิยามฟังก์ชันที่ใช้โหลดไฟล์เดี่ยวๆ
ฟังก์ชัน `mkdir_p(path)` และ `safe_open(path, mode, encoding='')` ต่อไปนี้ใช้สร้างโฟลเดอร์ย่อยสำหรับบันทึกไฟล์ที่โหลดมาลงเครื่อง โค้ดนี้ดัดแปลงจาก[ที่นี่](https://stackoverflow.com/questions/23793987/write-file-to-a-directory-that-doesnt-exist).

```python
# ฟังก์ชันสำหรับสร้างโฟลเดอร์ย่อยเมื่อจำเป็น เวลาจะบันทึกไฟล์ที่โหลดมา
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

ฟังก์ชัน `dl_file(url, fileout_name)` ต่อไปนี้โหลดไฟล์จาก url `url` และบันทึกเป็นไฟล์ชื่อ `fileout_name` (ใช้ relative path) ฟังก์ชันนี้ตั้งค่าได้ด้วยว่าต้องการให้พักนานแค่ไหนหลังโหลดแต่ละไฟล์เสร็จ และตั้งค่าได้ว่าต้องการให้รายงานผลต่างๆเวลาโหลดเสร็จหรือไม่
```python
# ฟังก์ชันโหลดไฟล์เดี่ยวๆ (ตั้งค่าได้ว่าจะโหลดเสร็จจะพักนานแค่ไหน และต้องการให้รายงานผลต่างๆหรือไม่)
def dl_file(url, fileout_name):
	t0 = time.time()
	r = requests.get(url)
	response_delay = time.time() - t0
	with safe_open(fileout_name,'wb') as fileout_binary:
		fileout_binary.write(r.content)
	set_delay = max(10*response_delay, 1) # ค่าที่สองคือเวลาพักสั้นสุด; ค่าปกติ: 1 (วินาที)
	print('SAVED: '+fileout_name) # รายงานผล (ไม่รายงานก็ได้)
	print('DYNAMIC DELAY = ' + str(10*response_delay) + ', REAL DELAY = ' + str(set_delay)) # รายงานผล (ไม่รายงานก็ได้)
	time.sleep(set_delay)
```

### 2. นิยามฟังก์ชันที่ใช้อ่าน directory listing และโหลดไฟล์ตามผลอ่าน
ฟังก์ชัน `dl_folder(url)` ต่อไปนี้โหลดทุกอย่างที่ระบุใน directory listing ที่ได้มาเวลาเรียกไปยัง url `url` อนึ่ง ฟังก์ชันนี้ใช้วิธีโหลดแบบกำปั้นทุบดินว่า
1. บันทึก directory listing เป็นไฟล์ html ไว้ชั่วคราวในเครื่อง
2. อ่านไฟล์นั้นด้วย BeautifulSoup แล้วไล่เก็บ url ของไฟล์และโฟลเดอร์ต่างๆที่จะโหลด
3. เรียก `dl_file()` เพื่อโหลดไฟล์เดี่ยวๆ และเรียก `dl_folder()` (แบบเวียนเกิด) เพื่อโหลดโฟลเดอร์ย่อย

```python
# ฟังก์ชันอ่าน directory listing แหละโหลดทุกอย่างในนั้น
def dl_folder(url):
	dl_file(url, './parsing_temp.htm') # เซฟ directory listing เป็นไฟล์ชั่วคราวในเครื่อง
	with open('parsing_temp.htm', encoding='UTF-8') as input_file:
		html_code = ' '.join(input_file.read().splitlines()) # ทำความสะอาดโค้ด html ก่อนส่งให้ BeautifulSoup (โดยเฉพาะลบ \n ที่สร้างปัญหาเวลาใช้ .contents ใน BeautifulSoup ทิ้ง)
		soup = BeautifulSoup(html_code, 'lxml', multi_valued_attributes=None) # ส่งโค้ด html ให้ BeautifulSoup; ได้ต้นไม้ xml คืนมา
	os.remove('parsing_temp.htm') # ลบไฟล์ directory listing ชั่วคราวทิ้ง
	
	# ใช้ลักษณะเฉพาะของ directory listing ว่าแท็ก <h1> แรกระบุ relative path ของ directory นั้น ซึ่งไปใช้ได้เวลาจะบันทึกไฟล์และโฟลเดอร์ที่โหลดมาลงในเครื่อง
	folder_path = '.' + soup.select_one('h1').get_text().replace('Index of ','') + '/'

	for item in soup.select('tr')[3:-1]: # ใช้ [3:-1] เพื่อตัด 3 แถวแรก (หัวตาราง, ลิงก์ "parent directory", เส้นนอน) กับแถวสุดท้าย (เส้นนอน) ทิ้ง
		if item.img['alt'] == '[DIR]': # ใช้ลักษณะเฉพาะว่าแถวที่เป็นโฟลเดอร์ หัวแถวเป็นไอคอนพิเศษที่ alternate text คือ '[DIR]'
			dl_folder(url+item.a['href']) # ถ้าจะโหลดแบบไม่เวียนเกิด เปลี่ยนบรรทัดนี้เป็น "continue"
		else:
			dl_file(url+item.a['href'], folder_path+item.a['href'])
```

### 3. สคริปของผู้ใช้ที่ระบุว่าจะโหลดอะไรอย่างไร (ตัวอย่าง)
```python
url = ...
dl_folder(url)
```