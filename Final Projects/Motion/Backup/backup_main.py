# Last edited: 03/10/2021
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from feed import Ui_MainWindow
import motion
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore


class Main_feed(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(__class__, self).__init__()
        self.setupUi(self)
        self.showFullScreen()
        self.btn_start.clicked.connect(lambda: self.btn_clicked())
        self.btn_stop.clicked.connect(lambda: self.not_video())
        self.btn_sync.clicked.connect(lambda: self.sync_allow())
        self.click = 0 
        self.m = motion.Motion()
        self.pause = False
        self.stop = True
        # self.m.cap = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        self.m.cap = cv.VideoCapture(0)
        

    def btn_clicked(self):
        self.click += 1

        if self.stop == True:
            self.m.runner()
            self.stop = False

        if (self.click % 2 != 0):
            self.btn_start.setText("Pause")
            self.pause = False
            self.video()

        elif (self.click % 2 == 0):
            self.pause = True 
            self.btn_start.setText("Start")
            

    def video(self):
        while True:
            if self.pause == False and self.stop == False:
                QApplication.processEvents()
                cv.putText(self.m.ff, str(int(self.m.fps)), (600, 65), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                cv.putText(self.m.ff, str(self.m.date_time), (10, 65), cv.FONT_HERSHEY_PLAIN, 1, (160, 50, 200), 2) 
                self.display(self.m.ff)
            else:
                break


    def not_video(self): 
        self.stop = True
        self.m.stopper()
        self.click = 0 
        self.btn_start.setText("Start")
        
    def sync_allow(self): 
        self.m.allow_sync = True
        # self.m.sync()
        self.m.sync_runner()

        # self.p8.sync()

    def display(self, frame): 
        qformat = QImage.Format_Indexed8

        if len(frame.shape) == 3: 
            if (frame.shape[2]) == 4: 
                qformat = QImage.Format_RGBA888
            else: 
                qformat = QImage.Format_RGB888
        frame = QImage(frame, frame.shape[1], frame.shape[0], qformat)
        frame = frame.rgbSwapped()
        self.label_camera.setPixmap(QPixmap.fromImage(frame))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    feed = Main_feed()
    sys.exit(app.exec_())
