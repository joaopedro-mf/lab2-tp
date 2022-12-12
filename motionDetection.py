# import the necessary packages
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2


def checkPointInROI(frame, point_x, point_y):
    x_min = int(frame.shape[1]/2 - frame.shape[1]*0.3)
    y_min = int(frame.shape[0]/2- frame.shape[0]*0.2)
    x_max = int(frame.shape[1]/2+ frame.shape[1]*0.3)
    y_max = int(frame.shape[0]/2+frame.shape[0]*0.2)
    cv2.rectangle(frame, (x_min,y_min ), (x_max, y_max), (0, 255, 255), 2)

    return (x_min < point_x < x_max) and (y_min < point_y < y_max)
    

  
# define a video capture object
#vid = cv2.VideoCapture(0)
#vid = cv2.VideoCapture('SUNP0001.mp4')
vid = cv2.VideoCapture('bus-front-gate-bus-camera-mobile-dvr.mp4')

avg = None
# lastUploaded = datetime.datetime.now()
# motionCounter = 0

#imagefirst = cv2.imread('data4/frame880.jpg')
imagefirst = cv2.imread('data2/frame5880.jpg')
frameFirst = imutils.resize(imagefirst, width=500)
grayFirst = cv2.cvtColor(frameFirst, cv2.COLOR_BGR2GRAY)
grayFirst = cv2.GaussianBlur(grayFirst, (21, 21), 0)
firstFrame = grayFirst

it= 0
while(True):
    it = 1+ it
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    #frame = f.array
    timestamp = datetime.datetime.now()
    text = "Unoccupied" 

    if it%50 == 0:
        continue
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # if the average frame is None, initialize it
    
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        #rawCapture.truncate(0)
        continue

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.2)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, 15 , 255,
        cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=3)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    motion = False
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        # if cv2.contourArea(c) < 500 or cv2.contourArea(c) > 5000:
        #    continue
        if cv2.contourArea(c) < 5000 :
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        motion  = checkPointInROI(frame,cX,cY)
        
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.circle(frame, (x,y), radius=2, color=(0, 255, 0), thickness=-1)
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"
    # draw the text and timestamp on the frame
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.35, (0, 0, 255), 1)

    frameDeltaBack = cv2.absdiff(firstFrame, gray)
    threshBack = cv2.threshold(frameDeltaBack, 120, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    threshBack = cv2.dilate(threshBack, None, iterations=3)
    cntsBack = cv2.findContours(threshBack.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cntsBack = imutils.grab_contours(cntsBack)
    backContrs  = False
    # loop over the contours
    for c in cntsBack:
        # if the contour is too small, ignore it
        #if cv2.contourArea(c) < 4000 or cv2.contourArea(c) > 5000:
        #    continue
        if cv2.contourArea(c) < 5000 :
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        backContrs  = checkPointInROI(frame,cX,cY)
        
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.circle(frame, (x,y), radius=2, color=(255, 0, 0), thickness=-1)
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        #text = "Occupied"
    
    if (motion and backContrs): print("tem passageiro miseravi")

    if True:
        # display the security feed
        cv2.imshow("Security Feed", frame)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break
    # clear the stream in preparation for the next frame
    #rawCapture.truncate(0)
vs.stop() 
vs.release()