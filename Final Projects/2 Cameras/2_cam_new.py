# Program to detect whether a door is open or not 
# First need to keep the door close and put point on the 4 corners of the door
# Then need to open the door, and confirm that the door is opened by clicking anywhere on the display 
# The program will now run 
# If the camera is shifted, the program needs to be restarted and recallibrated 
# Uses Threading and Queueing method
# Added tts, if the door is kept open more than 5 seconds, the program reminds to close it every 5 seconds 

# Last edited: 23/09/2021

import cv2 as cv
import numpy as np 
import threading
import queue
import time
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from feed import Ui_MainWindow
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets

p = queue.Queue()
q = queue.Queue()
fq = queue.Queue()

class Camera(QMainWindow, Ui_MainWindow):
    def __init__ (self): 
        super(__class__, self).__init__()
        self.setupUi(self)
        self.show()
        # self.btn_1.clicked.connect(lambda: self.btn_clicked('1'))
        self.pushButton.clicked.connect(lambda: self.btn_clicked())
        # cap1 = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        cap1 = cv.VideoCapture(0)
        ret, self.frame1 = cap1.read()
        #cap2 = cv.VideoCapture('rtsp://28628262:@192.168.0.170:554/live/ch00_1')
        cap2 = cv.VideoCapture(0)
        ret, self.frame2 = cap2.read()
        
        
        self.click = 0

    def cam1(self):
        pTime = time.time()
        # cap1 = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        cap1 = cv.VideoCapture(0)
        ret, self.frame1 = cap1.read()
        
        while True:
            cTime = time.time()
            ret, self.frame1 = cap1.read()
            if ret == False:
                # cap1 = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
                cap1 = cv.VideoCapture(0)
                ret, self.frame1 = cap1.read()
            elapsed_time = cTime - pTime
            if elapsed_time>0:
                fps = 1/elapsed_time
                cv.putText(self.frame1, str(int(fps)), (10, 40), cv.FONT_HERSHEY_PLAIN, 1, (160, 50, 205), 2)
            pTime = cTime 
            
    def cam2(self):
        #cap2 = cv.VideoCapture('rtsp://28628262:@192.168.0.170:554/live/ch00_1')
        cap2 = cv.VideoCapture(0)
        ret, self.frame2 = cap2.read()
        pTime = time.time()
        
        while True:
            cTime = time.time()
            ret, self.frame2 = cap2.read()
            if ret == False:
                #cap2 = cv.VideoCapture('rtsp://28628262:@192.168.0.170:554/live/ch00_1')
                cap2 = cv.VideoCapture(0)
                ret, self.frame2 = cap2.read()
            elapsed_time = cTime - pTime
            if elapsed_time>0:
                fps = 1/elapsed_time
                cv.putText(self.frame2, str(int(fps)), (10, 40), cv.FONT_HERSHEY_PLAIN, 1, (160, 50, 205), 2)
            pTime = cTime
    
    def btn_clicked(self):
        self.click += 1
        
        if (self.click % 2 != 0):
            self.pushButton.setText("Pause")
            self.video()
        
        # elif (self.click % 2 == 0):
        #     self.not_video()

    def video(self):
        # cap = cv.VideoCapture(0)

        while True:
            QApplication.processEvents()
            # ret, frame = cap.read()
    
            # self.label_feed.setText(str(frame))
            self.display1(self.frame1)
            self.display2(self.frame2)

            if cv.waitKey(1) and 0xFF == ord('q'): 
                 break 
            #cv.waitKey()
            if (self.click % 2 == 0):
                self.pushButton.setText("Start")
                break

    def not_video(self): 
        # while True:
        #     if (self.click % 2 != 0):
        #         self.video()
        pass
         

    def display1(self, frame_): 
        qformat = QImage.Format_Indexed8

        if len(frame_.shape) == 3: 
            if (frame_.shape[2]) == 4: 
                qformat = QImage.Format_RGBA888
            else: 
                qformat = QImage.Format_RGB888
        frame_ = QImage(frame_, frame_.shape[1], frame_.shape[0], qformat)
        frame_ = frame_.rgbSwapped()
        self.label_cam1.setPixmap(QPixmap.fromImage(frame_))
        # self.label_feed.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVC
        
    def display2(self, frame_): 
        qformat = QImage.Format_Indexed8

        if len(frame_.shape) == 3: 
            if (frame_.shape[2]) == 4: 
                qformat = QImage.Format_RGBA888
            else: 
                qformat = QImage.Format_RGB888
        frame_ = QImage(frame_, frame_.shape[1], frame_.shape[0], qformat)
        frame_ = frame_.rgbSwapped()
        self.label_cam2.setPixmap(QPixmap.fromImage(frame_))
        # self.label_feed.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)



if __name__ == "__main__": 
    app = QApplication(sys.argv)
    c = Camera()

    p1 = threading.Thread(target=c.cam1)
    p2 = threading.Thread(target = c.cam2)
    p1.start()
    p2.start()
        
    sys.exit(app.exec_())

    
    



