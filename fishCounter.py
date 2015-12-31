#!/usr/bin/env python
#Dec 30 2015 update by Alex Chen
#Count fish number and save to SQLite database using openCV and setting from camera.set file
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse, time, datetime, cv2, sqlite3, sys
import numpy as np

#set argument control for recording interval and duration
parser = argparse.ArgumentParser()
parser.add_argument('-i','--interval',type=float,help='Set up time interval between counts. Unit is second. Default is 0', default=0, metavar='')
parser.add_argument('-d','--duration',type=int, help='Set up recording duration. Unit is minute. Default is 60 minutes.', default=60, metavar='') 

args = parser.parse_args()
#setup recodring interval and duration
interVal = int(args.interval)#Interval in second
Duration = int(args.duration)#Duration in minute

#Build a connection to sqlite database
conn = sqlite3.connect('FishCountData.db')  #Connect (and create) a database
c = conn.cursor()  #set the cursor to the database

#Create a table, if necessary
try:
	c.execute("CREATE TABLE FishCountTable (Year REAL,Month REAL,Day REAL,Time DATETIME, FishCount REAL)")
except:
	print("Table has created")
	
#Restore parameters from camera.set file
try:
	with open('camera.set','r') as infile:
		parameters = infile.readlines()
		rw = int(parameters[0].split()[1])
		rh = int(parameters[1].split()[1])
		zx, zy, zw, zh = float(parameters[2].split()[1]),float(parameters[3].split()[1]),float(parameters[4].split()[1]),float(parameters[5].split()[1])
		brt = int(parameters[6].split()[1])
		sat = int(parameters[7].split()[1])
		con = int(parameters[8].split()[1])
		wb = parameters[9].split()[2]
		blursize = int(parameters[10].split()[2])
		threshVal = int(parameters[11].split()[1])
		cannyMin = int(parameters[12].split()[1])
		cannyMax = int(parameters[12].split()[2])
except:
	print('Camera.set has not created yet. Please run cameraSetup.py first.')
	sys.exit(0)
#setup camera parameters
camera = PiCamera()
camera.resolution = (rw,rh)
camera.zoom = (zx,zy,zw,zh)
camera.brightness = brt
camera.saturation = sat
camera.contrast = con
camera.awb_mode = wb
rawCapture = PiRGBArray(camera)
time.sleep(0.1)

def countFish(*args):
	settime = datetime.datetime.now()+datetime.timedelta(minutes=Duration)
	for frame in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True):
		image = frame.array
		grayimage = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		blurimage = cv2.GaussianBlur(grayimage,(blursize,blursize),0)
		T, threshimage = cv2.threshold(blurimage, threshVal, 255, cv2.THRESH_BINARY) 
		edgedimage = cv2.Canny(threshimage, cannyMin, cannyMax)
		cv2.imshow('frame',image)
		(cnts, _) = cv2.findContours(edgedimage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		fishCountNum = len(cnts)
		print("I count %d fish in this image" %fishCountNum )
		#capture current time
		year,month,day = time.strftime('%Y'),time.strftime('%m'),time.strftime('%d')
		timing = time.strftime('%H:%M:%S')
		#save to database
		c.execute("INSERT INTO FishCountTable (Year,Month,Day,Time,FishCount) VALUES(?,?,?,?,?)", (year,month,day,timing,fishCountNum))
		conn.commit()
		key = cv2.waitKey(1) & 0xFF
		rawCapture.truncate(0)
		if key == ord("q"):
			break
		if datetime.datetime.now() > settime:
			break
		time.sleep(interVal)  
	print("Program has stopped!")
	camera.close()
	cv2.destroyAllWindows()

	
if __name__=='__main__':
	countFish()
