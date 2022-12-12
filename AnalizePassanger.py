import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2

firstFrame = None
avg = None

def checkPointInROI(frame, point_x, point_y):
    x_min = int(frame.shape[1]/2 - frame.shape[1]*0.3)
    y_min = int(frame.shape[0]/2- frame.shape[0]*0.2)
    x_max = int(frame.shape[1]/2+ frame.shape[1]*0.3)
    y_max = int(frame.shape[0]/2+frame.shape[0]*0.2)
    cv2.rectangle(frame, (x_min,y_min ), (x_max, y_max), (0, 255, 255), 2)

    return (x_min < point_x < x_max) and (y_min < point_y < y_max)

def setFirstFrame(frame):
    global firstFrame

    imagefirst = frame

    frameFirst = imutils.resize(imagefirst, width=500)
    grayFirst = cv2.cvtColor(frameFirst, cv2.COLOR_BGR2GRAY)
    grayFirst = cv2.GaussianBlur(grayFirst, (21, 21), 0)
    firstFrame = grayFirst

def inicialTransform(frameAnalise):
    frame = imutils.resize(frameAnalise, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    return frame, gray

def findBackGround(frameAnalise):
    global avg
    frame, gray = inicialTransform(frameAnalise)

    if avg is None:
        #print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        #rawCapture.truncate(0)
        return False, 0,0

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.2)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, 15 , 255,
        cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    motion = False
    cX,cY = 0,0
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it

        if cv2.contourArea(c) < 5000 :
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        if checkPointInROI(frame,cX,cY):
            motion = True
            break
        # (x, y, w, h) = cv2.boundingRect(c)
        # cv2.circle(frame, (x,y), radius=2, color=(0, 255, 0), thickness=-1)
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return motion, cX, cY

def findMoviment(frameAnalise):
    global firstFrame

    if firstFrame is None:
        setFirstFrame(frameAnalise)
        return False, 0,0
    
    frame, gray = inicialTransform(frameAnalise)

    frameDeltaBack = cv2.absdiff(firstFrame, gray)
    threshBack = cv2.threshold(frameDeltaBack, 120, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    threshBack = cv2.dilate(threshBack, None, iterations=2)
    cntsBack = cv2.findContours(threshBack.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cntsBack = imutils.grab_contours(cntsBack)
    backContrs  = False
    cX,cY = 0,0
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

        if checkPointInROI(frame,cX,cY):
            backContrs = True
            break
        
        # (x, y, w, h) = cv2.boundingRect(c)
        # cv2.circle(frame, (x,y), radius=2, color=(255, 0, 0), thickness=-1)
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        #text = "Occupied"
    return backContrs, cX, cY