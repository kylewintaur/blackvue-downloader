#!/usr/bin/python3
import requests
import urllib.request
import os,sys
import datetime
import time
import socket
import psutil    

pid = str(os.getpid())
pidfile = "/tmp/dashcam-downloader.pid"

if os.path.isfile(pidfile):
    print(pidfile + " already exists, exiting")
    sys.exit()
pFile = open(pidfile, 'w')
pFile.write(pid)
pFile.close()

try:
	dashcamIP = "192.168.1.123"
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	path = "/storage/Dashcam/"+date
	upperpath = "/home/dashcam/"
	url = "https://gotify.your-domain.com/message?token=?????????"
	timeout = 180
	socket.setdefaulttimeout(timeout)
	
	def checkForInactivity():
		# Will alert if no new files have been added in 24 hours
		return 0
	
	def getIP():
		# Use this to find IP - To do
		return 0
	
	def getVideoList(dashcamIP):
		# Get list of video URLs
		webpage = requests.get("http://"+dashcamIP+"/blackvue_vod.cgi")
		videoListText = webpage.text.replace(",s:1000000", "")
		videoListText = videoListText.replace("n:/Record/", "")
		videoList = []
		videoList = videoListText.splitlines()
		videoList.remove('v:1.00')
		global filteredVideoList
		filteredVideoList = [item for item in videoList if '_P' not in item]
	
	def downloadVideo(name,count):
		# Used to download videos
		message = "[" + str(count) + "/" + str(len(filteredVideoList)) + "] " + name
		log("Downloading",message,1)
		year = name[:4]
		month = name[4:6]
		day = name[6:8]
		
		try:
	        	os.mkdir(path)
		except FileExistsError:
		        pass
		try:
			urllib.request.urlretrieve("http://"+dashcamIP+"/Record/"+name, upperpath+year+"-"+month+"-"+day+"/"+name)
		except urllib.error.ContentTooShortError as e:
			log("Error",e,10)
			return 1
		except socket.timeout as e:
			return 1
		except Exception as e:
			log("Error",e,10)
			return 1
		return 0
	
	def log(title,message,priority):
		# Used for logging to Gotify
		try:
			resp = requests.post(url, json={
		    "message": message,
		    "priority": priority,
		    "title": title
		})
		except TypeError:
			pass
			return 1
		return 0
	
	def checkDirectory(name):
		global directoryList
		year = name[:4]
		month = name[4:6]
		day = name[6:8]
	
		try:
			directoryList = os.listdir(upperpath+year+"-"+month+"-"+day)
		except FileNotFoundError:
			os.mkdir(upperpath+year+"-"+month+"-"+day)
			directoryList = os.listdir(upperpath+year+"-"+month+"-"+day)
	
		if name in directoryList:
			fileURL = urllib.request.urlopen("http://"+dashcamIP+"/Record/"+name)
			size = fileURL.getheader('Content-Length')
			fileSize = os.stat(upperpath+year+"-"+month+"-"+day+"/"+name).st_size
			if int(size) > int(fileSize):
				return True
			else:
				return False
	def updateMetaData(name):
		year = str(name[:4])
		month = str(name[4:6])
		day = str(name[6:8])
		hour = str(name[9:11])
		minute = str(name[11:13])
		second = str(name[13:15])
		date = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second))
		modTime = time.mktime(date.timetuple())
		filePath = upperpath+year+"-"+month+"-"+day+"/"+name
		oldModTime = os.path.getmtime(filePath)
		os.utime(upperpath+year+"-"+month+"-"+day+"/"+name, (modTime, modTime))
		newModTime = os.path.getmtime(filePath)

	## Add get IP and inactivity functions
	# Start of script
	try:
		urllib.request.urlretrieve("http://"+dashcamIP+"/")
	except OSError as err:
		print(err)
		sys.exit()
	except:
		log("Download error",str(err),10)

	getVideoList(dashcamIP)

	try:
		os.mkdir(path)
	except FileExistsError:
		pass

	# Remove any videos from the list already downloaded
	filteredVideoList.sort()
	for i in filteredVideoList:
		if checkDirectory(i):
			filteredVideoList.remove(i)
	count = 0
	for i in filteredVideoList:
		count = count + 1
		downloadVideo(i,count)
		updateMetaData(i)
	
finally:
    os.unlink(pidfile)
