import cv2
import time 
import mediapipe as np
import math

class handDetector():
    def __init__(self, mode=False, maxhands=2, detectcon=0.5, trackcon=0.5):
        self.mode=mode
        self.maxhands=maxhands
        self.detectcon=detectcon
        self.trackcon=trackcon
        
        self.nphands=np.solutions.hands
        self.hands=self.nphands.Hands(self.mode,self.maxhands, self.detectcon, self.trackcon)
        self.npDraw= np.solutions.drawing_utils
        self.tipIds=[4, 8, 12, 16, 20]

    def findhands(self, img, draw=True):
        imgRGB=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results=self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for singlehand in self.results.multi_hand_landmarks:
                if draw:
                    self.npDraw.draw_landmarks(img, singlehand, self.nphands.HAND_CONNECTIONS)
        
        return img

                

    def findpositions(self, img, handno=0, draw=True):

        xlist=[]
        ylist=[]
        boundarybox=[]

        
        self.lmlist=[]
        if self.results.multi_hand_landmarks:
            myhand=self.results.multi_hand_landmarks[handno]
            for id, lm in enumerate(myhand.landmark):
                
                #print(id,lm)
                h,w,c= img.shape
                cx, cy= int(lm.x*w), int(lm.y*h)
                xlist.append(cx)
                ylist.append(cy)
                
                #print(id, cx, cy) #location with id
                
                self.lmlist.append([id, cx,cy])
                #marking a specific id
                if draw:
                    cv2.circle(img, (cx,cy), 5, (2500,0,250), cv2.FILLED)

            xmin, xmax=min(xlist), max(xlist)
            ymin, ymax=min(ylist), max(ylist)

            boundarybox= xmin, ymin, xmax, ymax

            #if draw:
                #cv2.rectangle(img, (boundarybox[0]-20, boundarybox[1]-20), (boundarybox[2]+20, boundarybox[3]+20), (0,255,0), 2)

        return self.lmlist, boundarybox

    def fingersup(self):
        fingers=[]
        #thumb
        if self.lmlist[self.tipIds[0]][1] > self.lmlist[self.tipIds[0] - 1] [1]:
            fingers.append(1)
        else:
            fingers.append(0)
        #fingers
        for id in range(1,5):
            if self.lmlist[self.tipIds[id]][2] < self.lmlist[self.tipIds[id] - 2] [2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers


    def finddistance(self, p1, p2, img, draw=True):
        x1, y1=self.lmlist[p1][1], self.lmlist[p1][2]
        x2, y2=self.lmlist[p2][1], self.lmlist[p2][2]
        cx, cy= (x1+x2)//2, (y1+y2)//2
        
        cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2,y2), 15, (255,0,255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2,y2), (255,0,255), 2)
        cv2.circle(img, (cx, cy), 15, (255,0,255), cv2.FILLED)
        
        length=math.hypot(x2-x1, y2-y1)
        #print(length)

        return length, img, (x1,y1, x2,y2, cx,cy)
        


   

def main():
    ptime=0
    ctime=0

    cap=cv2.VideoCapture(0)

    detector=handDetector()

    while True:
        success, img=cap.read()

        img=detector.findhands(img)
        lmlist=detector.findpositions(img)
        if len(lmlist) !=0:
            print(lmlist[0])
        
        ctime=time.time()
        fps=1/(ctime-ptime)
        ptime=ctime

        cv2.putText(img, str(int(fps)), (5,100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (20,0,20),4)
        cv2.imshow("image", img)
        cv2.waitKey(1)



if __name__=="__main__":
    main()