from AnalizePassanger import findBackGround, findMoviment
from requestsServer import sendImageApi
#from painelIndentificacao import setLedMotorista, setLedPassageiro
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import numpy as np
from threading import Thread
import os

debug = True

statusPasssageiro = ["Livre","Em Desembarque", "Finalizado"]
statusSaidaPorta  = [ "Seguro", "Atencao",]

act_statusPassageiro = statusPasssageiro[0]
act_statusSaidaPorta = statusSaidaPorta[0]

ult_mudancaPassageiro_peso, ult_mudancaPassageiro_hora  = 3, datetime.datetime.now()

def internalCameraAnalize():
    global debug, statusPasssageiro, act_statusPassageiro, ult_mudancaPassageiro_peso, ult_mudancaPassageiro_hora

    if not debug:
        vid = cv2.VideoCapture(0)
    else:
        #vid = cv2.VideoCapture('SUNP0001.mp4')
        vid = cv2.VideoCapture('bus-front-gate-bus-camera-mobile-dvr.mp4')
    it= 0
    while(True):
        timestamp = datetime.datetime.now()
        it = 1+ it

        _, frame = vid.read()

        if it%50 == 0:
            continue
        
        resultMotion, x,y = findBackGround(frame)
        resultBackground , x, y = findBackGround(frame)

        if (timestamp- ult_mudancaPassageiro_hora ).total_seconds() >5:
            ult_mudancaPassageiro_peso, ult_mudancaPassageiro_hora = 10, datetime.datetime.now()

        if (resultMotion and resultBackground):
            if (ult_mudancaPassageiro_peso == 0):
                act_statusPassageiro = statusPasssageiro[1]
                ult_mudancaPassageiro_peso, ult_mudancaPassageiro_hora = 20, datetime.datetime.now()

            elif(ult_mudancaPassageiro_peso <= 10):
                ult_mudancaPassageiro_peso = ult_mudancaPassageiro_peso - 1
        elif(act_statusPassageiro == statusPasssageiro[1] 
                and not resultBackground 
                and not resultMotion) :
            if (ult_mudancaPassageiro_peso == 0):
                act_statusPassageiro = statusPasssageiro[0]
                ult_mudancaPassageiro_peso, ult_mudancaPassageiro_hora = 10, datetime.datetime.now()

            elif(ult_mudancaPassageiro_peso <= 20):
                ult_mudancaPassageiro_peso = ult_mudancaPassageiro_peso - 1
        

        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Status: {}".format(act_statusPassageiro), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.35, (0, 0, 255), 1)

        if debug:
        # display the security feed
            cv2.imshow("Security Feed", frame)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break
    vid.stop() 
    vid.release()

def updateSinalizao():
    global debug, act_statusPassageiro, act_statusSaidaPorta, statusPasssageiro, statusSaidaPorta

    if debug:
        red_image, green_image = np.zeros((200,200,3), np.uint8), np.zeros((200,200,3), np.uint8)
        red_image [:,:,:] = (0,0,255) 
        green_image [:,:,:] = (0,255,0)

        while True:
            if (act_statusPassageiro == statusPasssageiro[0]):
                cv2.imshow("Sinalizao Motorista", green_image)                
            else:
                cv2.imshow("Sinalizao Motorista", red_image)
            
            if(act_statusSaidaPorta == statusSaidaPorta[0]):
                cv2.imshow("Sinalizao Passageiro", green_image)
            else:
                cv2.imshow("Sinalizao Passageiro", red_image)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break 

def externalCameraAnalize():
    global debug, statusSaidaPorta, act_statusSaidaPorta
    images_simulate = os.listdir('data3/')

    while True:
        for imagePath in images_simulate:
            img = cv2.imread('data3/'+imagePath)

            if img is type(None): continue
            if debug:
                cv2.imshow('camera externa', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 
        
            response  = sendImageApi(img)
            
            if response['car'] > 0 or response['moto'] > 0:
                act_statusSaidaPorta  = statusSaidaPorta[1]
            else:
                act_statusSaidaPorta  = statusSaidaPorta[0]



threadInternalCameraAnalize = Thread(target=internalCameraAnalize)
threadExternalCameraAnalize = Thread(target=externalCameraAnalize)
threadSinalizacao = Thread(target=updateSinalizao)
# run the thread
threadInternalCameraAnalize.start()
threadExternalCameraAnalize.start()
threadSinalizacao.start()
# wait for the thread to finish
print('Waiting for the thread...')
threadInternalCameraAnalize.join()
threadExternalCameraAnalize.join()
threadSinalizacao.join()