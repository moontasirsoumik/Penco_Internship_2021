# Program to detect whether a door is open or not 
# First need to keep the door close and put point on the 4 corners of the door
# Then need to open the door, and confirm that the door is opened by clicking anywhere on the display 
# The program will now run 
# If the camera is shifted, the program needs to be restarted and recallibrated 
# Uses Threading and Queueing method
# Added tts, if the door is kept open more than 5 seconds, the program reminds to close it every 5 seconds 

# Last edited: 03/10/2021

import cv2 as cv
import numpy as np 
import threading
import queue
from gtts import gTTS
from playsound import playsound
import time

p = queue.Queue()
q = queue.Queue()

class Door:
    def __init__ (self): 
        self.breaker  = False
        self.circles = np.zeros((4,2), np.int)
        self.counter = 0
        self.diff = (1,1,1)
        self.start_pixel = (125, 175)
        self.entered = False
        self.done = False
        self.open = False
        self.width, self.height = 250, 350
        self.start_time = 0 
        self.end_time = 0 
        # self.voice = False 
        self.cap = cv.VideoCapture(0)
        _, self.f_show = self.cap.read()
        self.thread_breaker = False
        self.broken1 = False
        self.broken2 = False
        self.start = True

    def tts(self):
        myText = "Please close the door"
        language = 'en'
        output = gTTS(text = myText, lang = language, slow = False)
        output.save("output.mp3")

    def mousePoints(self, event, x, y, flags, params): 
        if event == cv.EVENT_LBUTTONDOWN: 
            if self.counter<4:
                self.circles[self.counter] = x, y
                self.counter += 1 
                # print(circles)
            else: 
                self.counter+=1


    def door_open(self):
        # ff = cv.imread('1 (1).jpg')
        while True:
            ret, ff = self.cap.read()
            if ret:
                img = ff.copy()
                cv.putText(img, "Step 1", (20, 40), cv.FONT_HERSHEY_PLAIN, 2, (50, 100, 255), 2)

                if self.counter == 4: 
                    self.pts1 = np.float32([self.circles[0], self.circles[1], self.circles[2], self.circles[3]])
                    self.pts2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
                    matrix = cv.getPerspectiveTransform(self.pts1, self.pts2)
                    self.matrix = matrix
                    self.imgOutput = cv.warpPerspective(img, self.matrix, (self.width, self.height))
                    self.entered = True
                    

                    cv.imshow("Output Image", self.imgOutput)

                for x in range(0, 4): 
                    cv.circle(img, (self.circles[x][0], self.circles[x][1]), 3, (0, 255, 0), cv.FILLED)
                    if self.entered == True and x==3: 
                        self.breaker = True
                        print("breaker")

                cv.imshow("Image", img)
                cv.setMouseCallback("Image", self.mousePoints)
                cv.waitKey(1)
                if self.breaker == True:
                    cv.destroyAllWindows()
                    break

    
    def door_closed(self):
        img = self.imgOutput.copy()

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        _, threshold = cv.threshold(gray, 125, 255, cv.THRESH_BINARY)
        img = threshold.copy()
        mask = np.zeros((self.height+2, self.width+2), np.uint8)
        self.retval1 = cv.floodFill(img, mask, self.start_pixel, (0,255,0), self.diff, self.diff)

        self.retval1 = np.sum(np.sum(x) for x in self.retval1)

        self.close_large = True


        while True:
            _, ff = self.cap.read() 
            cv.putText(ff, "Step 2", (20, 40), cv.FONT_HERSHEY_PLAIN, 2, (50, 100, 255), 2)
            cv.imshow("feed", ff)
            cv.setMouseCallback('feed', self.mousePoints)

            img = ff.copy()
            img = cv.warpPerspective(ff, self.matrix, (self.width, self.height))
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

            _, threshold = cv.threshold(gray, 125, 255, cv.THRESH_BINARY)
            img = threshold.copy()

            mask = np.zeros((self.height+2, self.width+2), np.uint8)
            self.retval2= cv.floodFill(img, mask, self.start_pixel, (0,255,0), self.diff, self.diff)

            self.retval2 = np.sum(np.sum(x) for x in self.retval2)

            if self.counter == 5: 
                self.counter = 0 
                self.counter = 0 
                break
            cv.waitKey(1)

        if self.retval1>self.retval2: 
            self.close_large = True
        else: 
            self.close_large = False
        
        cv.destroyAllWindows()
        self.done = True 

    def frame_getter(self):
        self.cap = cv.VideoCapture(0)
        ret, frame = self.cap.read()
        frame2 = cv.warpPerspective(frame, self.matrix, (self.width, self.height))
        p.put(frame)
        q.put(frame2) 
        self.breaker = False

        while True: 
            ret, frame =self.cap.read()

            if q.empty() == False:
                _ = q.get()
            
            if p.empty() == False: 
                _ = p.get()

            if ret == False:
                self.cap = cv.VideoCapture(0)
                ret, frame = self.cap.read()
                frame2 = cv.warpPerspective(frame, self.matrix, (self.width, self.height))
                p.put(frame)
                q.put(frame2)

            if ret:
                p.put(frame)
                frame2 = cv.warpPerspective(frame, self.matrix, (self.width, self.height))
                q.put(frame2)

            if self.breaker == True:
                self.cap.release()
                break

            cv.waitKey(20)

            if self.thread_breaker == True: 
                self.broken2 = True
                break
    
    def process(self): 
        while True: 
            if p.empty() == False and q.empty() == False: 
                frame = p.get()
                frame2 = q.get()

                im = frame2.copy()
                gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

                _, threshold = cv.threshold(gray, 125, 255, cv.THRESH_BINARY)
                edges = threshold.copy()
                img = edges.copy()

                mask = np.zeros((self.height+2, self.width+2), np.uint8)
                
                retval= cv.floodFill(img, mask, self.start_pixel, (0,255,0), self.diff,self. diff)

                array2 = np.sum(np.sum(x) for x in retval)

                diff1 = abs(array2-self.retval1)
                diff2 = abs(array2-self.retval2)

                if diff2<diff1: 

                    self.open = True
                    self.end_time = time.time()

                    if (self.end_time - self.start_time) >= 5: 

                        playsound("output.mp3")
                        self.start_time = time.time()


                elif diff1<diff2: 

                    self.open = False
                    self.start_time = time.time() 
                
                self.f_show = frame.copy()

            
            if self.thread_breaker == True:
                self.broken1 = True
                break 


    def runner(self):
        if self.start == True:
            self.start = False
            self.tts()
            self.door_open()
            self.door_closed()
            if self.done == True:
                self.thread_breaker = False
                p1 = threading.Thread(target= self.frame_getter)
                p2 = threading.Thread(target = self.process)
                p1.start()
                p2.start()
        else: 
            self.breaker  = False
            self.circles = np.zeros((4,2), np.int)
            self.counter = 0
            self.diff = (1,1,1)
            self.start_pixel = (125, 175)
            self.entered = False
            self.done = False
            self.open = False
            self.width, self.height = 250, 350
            self.start_time = 0 
            self.end_time = 0 
            # self.voice = False 
            self.cap = cv.VideoCapture(0)
            _, self.f_show = self.cap.read()

            self.thread_breaker = True
            self.done = False
            self.door_open()
            self.door_closed()
            while True:
                if self.done == True:
                    if self.broken1 == True and self.broken2 == True:
                        self.broken1 = False
                        self.broken2 = False
                        self.thread_breaker = False
                        p1 = threading.Thread(target= self.frame_getter)
                        p2 = threading.Thread(target = self.process)
                        p1.start()
                        p2.start()
                    else: 
                        pass

        


