import cv2
import time
import numpy as npy
import hand_tracking_module_init as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#1. webcam settings including fps
#2. finding positions of tumb point and index finger point
#3. calulating distance betweeen two points
#4. defing and coverting range for volume acording to the increasing or decreasing distance with respect to the index finger point and the thumb point.
#5. sync of volume control labraries with the change in distance of index finger point and the thumb point.
#6. Ui like the volume bar and converting volume to percentage.

 
#with respect to distance between finger
#reducing resolution for smothening
#check fingers up for fixing a volume level


###################################
wacm, hcam=640, 480
###################################

cap=cv2.VideoCapture(0)
cap.set(3, wacm)
cap.set(4, hcam)
ptime=0

detector=htm.handDetector(detectcon=0.5, maxhands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volrange=volume.GetVolumeRange()

minvol=volrange[0]
maxvol=volrange[1]

volbar=400
volpercentage=0

area=0

volumecolour=(255,0,0)



while True:
    success, img= cap.read()
    #find hand
    img=detector.findhands(img)
    lmlist, boundarybox =detector.findpositions(img, draw=True)
    if len(lmlist) !=0:
        #print(lmlist[4], lmlist[8])

        #filtering for a smotthening effect
        area=(boundarybox[2]-boundarybox[0])*(boundarybox[3]-boundarybox[1])//100
        print(area)
        if 250<area<1000:
            #print("yes")

            #find distance between index and thumb #optimised
            length, img, lineinfo =detector.finddistance(4, 8, img)
            print(length)
            




#volume range -63-0
#convert volume

            
            volbar=npy.interp(length, [50, 240], [400,150])
            volpercentage=npy.interp(length, [50, 240], [0,100])

            #making it smother by reducing resolution

            smothness=5
            volpercentage=smothness*round(volpercentage/smothness)

            #cheking last finger is up or down
            fingers=detector.fingersup()
            #print(fingers)
            if not fingers[4]: #that is if the last finger is down
                volume.SetMasterVolumeLevelScalar(volpercentage/100,None)
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (255,255,255), cv2.FILLED)
                volumecolour=(255,0,255)
            else:
                volumecolour=(255,0,0)
            #print(length,vol)
            #volume.SetMasterVolumeLevel(vol, None)
            

            
                
    #drawing       
    cv2.rectangle(img, (50, 150), (85,400), (255,0,0), 3)
    cv2.rectangle(img, (50, int(volbar)), (85,400), (255,0,0), cv2.FILLED)
    cv2.putText(img, f'{int(volpercentage)} %', (40,450), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0),3)

    currentvolume=int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Volume Set : {int(currentvolume)} %', (300,50), cv2.FONT_HERSHEY_DUPLEX, 1, (volumecolour),2)

    ctime=time.time()
    fps=1/(ctime-ptime)
    ptime=ctime

    cv2.putText(img, str(int(fps)), (5,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (20,0,20),1)

    cv2.imshow("img", img)
    cv2.waitKey(1)