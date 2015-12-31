#!/usr/bin/env python
#Dec 30 2015 update by Alex Chen #
#Open Pi camera and stream video to adjust parameters for finding fish contour
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse, time, cv2

parser = argparse.ArgumentParser()
#setup camera resolution
parser.add_argument('-rw','--resolutionWidth',type=int,help='Pi camera resolution in width. Max. is 1920.',choices=range(1,1920),default=560,metavar='')
parser.add_argument('-rh','--resolutionHeight',type=int,help='Pi camera resolution in height. Max. is 1080.',choices=range(1,1080),default=420,metavar='')
#setup camera zoom/crop 
parser.add_argument('-zx','--zoomX',type=float,help='Region of Interest on X-axis. A value between 0 and 1. Default is 0. Increase value to crop image from the left.',default=0.0,metavar='')
parser.add_argument('-zy','--zoomY',type=float,help='Region of Interest on Y-axis. A value between 0 and 1. Default is 0. Increase value to crop image from the top.',default=0.0,metavar='')
parser.add_argument('-zw','--zoomW',type=float,help='Region of Interest in width proportion. A value between 0 and 1. Default is 1. Decrease value to shrink width from the right. ',default=1.0,metavar='')
parser.add_argument('-zh','--zoomH',type=float,help='Region of Interest in height proportion. A value between 0 and 1. Default is 1. Decrease value to shrink height from the bottom.',default=1.0,metavar='')
#setup camera other parameters
parser.add_argument('-b','--brightness',type=int,help='Pi camera brightness. A value between 0 and 100. Default is 50. Increase value to increase brightness.',choices=range(0,100),default=50,metavar='')
parser.add_argument('-s','--saturation',type=int,help='Pi camera saturation. A value between -100 and 100. Default is 0. Increase value to increase saturation.',choices=range(-100,100),default=0,metavar='')
parser.add_argument('-c','--contrast',type=int,help='Pi camera contrast. A value between -100 and 100. Default is 0. Increase value to increase contrast.',choices=range(-100,100),default=0,metavar='')
parser.add_argument('-wb','--whitebalance',help="Pi camera white balance mode. Choices of 'auto','off','sunlight','cloudy','shade','tungsten','fluorescent','incandescent','flash','horizon'. ",\
					choices=['auto','off','sunlight','cloudy','shade','tungsten','fluorescent','incandescent','flash','horizon'],default='auto',metavar='')
#setup openCV parameters
parser.add_argument('-gb','--gaussianBlur',type=int,help='Gaussin kernel size, must be a positive and odd number. Higher the value, more blurry the image. Default is 19.',default=19, metavar='')
parser.add_argument('-th','--threshold',type=int,help='A thresholding value for converting grascale image to black and white. A value between 0 and 255. Default is 90.',choices=range(0,255),default=90,metavar='')
parser.add_argument('-ce','--cannyEdge',type=int, nargs=2, help='Min. and max. thresholding values for Canny edged detection. Two values between 0 and 225. Default is 50 150.',default=[50,150], metavar='')
parser.add_argument('-v','--views',nargs='+', default='origin', help='Show different processed views. Options include "gray","blur","thresh",and "edge"',choices=['gray','blur','thresh','edge','origin'], metavar='')

args = parser.parse_args()

#setup camera variables
rw = args.resolutionWidth
rh = args.resolutionHeight
zx, zy, zw, zh = args.zoomX, args.zoomY, args.zoomW, args.zoomH
brt = args.brightness
sat = args.saturation
con = args.contrast
wb = args.whitebalance
#setup opencv parameters
blursize = args.gaussianBlur
threshVal = args.threshold
cannyMin = int(args.cannyEdge[0])
cannyMax = int(args.cannyEdge[1])
view = args.views

camera = PiCamera()
camera.resolution = (rw,rh)
camera.zoom = (zx,zy,zw,zh)
camera.brightness = brt
camera.saturation = sat
camera.contrast = con
camera.awb_mode = wb
rawCapture = PiRGBArray(camera)
time.sleep(0.1)

def streamCamera(*args):
	for frame in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True):
		image = frame.array
		grayimage = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		blurimage = cv2.GaussianBlur(grayimage,(blursize,blursize),0)
		T, threshimage = cv2.threshold(blurimage, threshVal, 255, cv2.THRESH_BINARY) 
		edgedimage = cv2.Canny(threshimage, cannyMin, cannyMax)
		cv2.imshow('camera view',image)
		if 'gray' in view:
			cv2.imshow('Grayscale',grayimage)
		if 'blur' in view:
			cv2.imshow('Gaussian Blur',blurimage)
		if 'thresh' in view:
			cv2.imshow('Thresholding',threshimage)
		if 'edge' in view:
			cv2.imshow('Canny edge detection',edgedimage)
		rawCapture.truncate(0)
		key = cv2.waitKey(1)&0xFF			
		if key == ord('q'):
			break
		if key == ord('s'):
			filename='imageCaptured_'+str(time.strftime('%Y-%m-%d_%H:%M:%S'))+'.jpg'
			cv2.imwrite(filename,image)
	camera.close()
	cv2.destroyAllWindows()

	
def saveSetting(*args):
	ans = raw_input('Do you want to save the camera settings? (Y/N): ')
	if ans.upper()=='Y' or ans.upper()=='YES':
		with open('camera.set', 'w') as outfile:
			outfile.write('resolutionWidth\t'+str(rw)+'\n')
			outfile.write('resolutionHeight\t'+str(rh)+'\n')
			outfile.write('zoomX\t'+str(zx)+'\n')
			outfile.write('zoomY\t'+str(zy)+'\n')
			outfile.write('zoomW\t'+str(zw)+'\n')
			outfile.write('zoomH\t'+str(zh)+'\n')
			outfile.write('brightness\t'+str(brt)+'\n')
			outfile.write('saturation\t'+str(sat)+'\n')
			outfile.write('contrast\t'+str(con)+'\n')
			outfile.write('white balance\t'+str(wb)+'\n')
			outfile.write('Gaussian Blur\t'+str(blursize)+'\n')
			outfile.write('Threshold_Binary\t'+str(threshVal)+'\n')
			outfile.write('CannyEdgeDetect\t'+str(cannyMin)+'\t'+str(cannyMax))
			print('Camera parameters have saved in "camera.set" ')
	else: pass
		
	
if __name__=='__main__':
	streamCamera()
	saveSetting()
		
