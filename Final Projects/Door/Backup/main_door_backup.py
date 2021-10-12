#https://gist.github.com/ozcanyarimdunya/a030e607a2e8f67e5969c8ee544bd11c
# Main file for door project
#  
# Last edited: 03/10/2021

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from door_feed import Ui_MainWindow
import door
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore
import threading


class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(__class__, self).__init__()
        self.setupUi(self)
        self.showFullScreen()

        self.btn_start.clicked.connect(lambda: self.btn_clicked())
        self.btn_recal.clicked.connect(lambda: self.not_video())
        self.click = 0 
        self.d = door.Door()
        self.label_status.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_feed.setMaximumSize(QtCore.QSize(1, 1))
        self.label_feed.setMinimumSize(QtCore.QSize(1, 1))
        self.d.start = False
        self.d.tts()
        self.label_status.setText("Step1: \n\nPlease keep the door closed\nPlease left click on the 4 corners of the door\nPlease make sure there's no obstacles in front\n\nStep 2: \n\nPlease keep the door closed\nPlease left click anywhere to confirm the door is open\nPlease make sure there's no obstacles in front\n\nStep 3: \n\nPress Start")
        self.d.door_open()
        self.d.door_closed()
        if self.d.done == True:

            self.d.thread_breaker = False
            p1 = threading.Thread(target= self.d.frame_getter)
            p2 = threading.Thread(target = self.d.process)
            p1.start()
            p2.start()

        self.vid_break = False 
        self.step_show = False 

    def btn_clicked(self):
        self.click += 1
        
        if (self.click % 2 != 0):
            self.step_show = False
            self.btn_start.setText("Pause")
            self.video()

    def video(self):
        self.label_status.setMaximumSize(QtCore.QSize(16777215, 22))
        self.label_feed.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_feed.setMinimumSize(QtCore.QSize(640, 480))
        self.label_status.setText("")
        while True:
            QApplication.processEvents()
            
            frame = self.d.f_show.copy()
            self.display(frame)
            if self.d.open == True: 
                self.label_status.setText("Door Open")
            elif self.d.open == False:
                self.label_status.setText("Door Closed") 

            if (self.click % 2 == 0):
                self.btn_start.setText("Start")
                self.label_status.setText("Video Paused") 
                break

            if self.step_show == True:  
                break

        
        if self.step_show == True: 
            self.step_show = False 
            self.label_status.setText("Step1: \n\nPlease keep the door closed\nPlease left click on the 4 corners of the door\nPlease make sure there's no obstacles in front\n\nStep 2: \n\nPlease keep the door closed\nPlease left click anywhere to confirm the door is open\nPlease make sure there's no obstacles in front\n\nStep 3: \n\nPress Start")
            
            pf1 = threading.Thread(target = self.recal)
            pf1.start()

    def not_video(self):
        self.step_show = True 

    def recal(self):
        QApplication.processEvents()
        self.btn_start.setText("Start")
        self.click = 0
        self.label_status.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_feed.setMaximumSize(QtCore.QSize(1, 1))
        self.label_feed.setMinimumSize(QtCore.QSize(1, 1))
        self.d.runner()
        self.label_status.setText('Ready for detection')
        

    def display(self, frame): 
        qformat = QImage.Format_Indexed8

        if len(frame.shape) == 3: 
            if (frame.shape[2]) == 4: 
                qformat = QImage.Format_RGBA888
            else: 
                qformat = QImage.Format_RGB888
        frame = QImage(frame, frame.shape[1], frame.shape[0], qformat)
        frame = frame.rgbSwapped()
        self.label_feed.setPixmap(QPixmap.fromImage(frame))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())
