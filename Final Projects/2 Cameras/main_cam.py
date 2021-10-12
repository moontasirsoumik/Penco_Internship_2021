#https://gist.github.com/ozcanyarimdunya/a030e607a2e8f67e5969c8ee544bd11c
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from feed import Ui_MainWindow
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore
import threading
import queue
from datetime import datetime
import pytz
import time

p = queue.Queue()
q = queue.Queue()
r = queue.Queue()
fin = queue.Queue()
a = queue.Queue()
b = queue.Queue()

class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(__class__, self).__init__()
        self.setupUi(self)
        self.show()
        # self.btn_1.clicked.connect(lambda: self.btn_clicked('1'))
        self.pushButton.clicked.connect(lambda: self.btn_clicked())
        self.click = 0
        
        
        self.width1 = 0
        self.height1 = 0
        self.width2 = 0
        self.height2 = 0
        self.scale = 50
        self.start_hour = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%H")
        self.end_hour = 0 
        self.hour_counter = 0
        self.breaker = False
        self.vid_no = 1
        self.pTime = time.time()


        self.fourcc = cv.VideoWriter_fourcc(*'XVID')
        #out = cv.VideoWriter(f'cam_output_{vid_no}.avi', fourcc, 10.0, (640, 480))

        cap = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        ret, frame1 = cap.read()
        if ret:          
            self.width1 = int(frame1.shape[1] * (self.scale/100))
            self.height1 = int(frame1.shape[0] * (self.scale/100))

        cap = cv.VideoCapture('rtsp://28628262:@192.168.0.170:554/live/ch00_1')
        ret, frame2 = cap.read()
        if ret:
            self.width2 = int(frame2.shape[1] * (self.scale/100))
            self.height2 = int(frame2.shape[0] * (self.scale/100))
        #self.f1 = frame1
        #self.f2 = frame2
        
        # both = cv.hconcat([frame1, frame2])

        # self.h, self.w, _ = both.shape
        self.out1 = cv.VideoWriter(f'cam_output_{self.vid_no}.avi', self.fourcc, 10.0, (self.width1, self.height1))
        self.out2 = cv.VideoWriter(f'cam_output_{self.vid_no}.avi', self.fourcc, 10.0, (self.width2, self.height2))
        

    def btn_clicked(self):
        self.click += 1
        
        if (self.click % 2 != 0):
            self.pushButton.setText("Pause")
            self.video()
        
        # elif (self.click % 2 == 0):
        #     self.not_video()

         

    def cam1(self):
        cap = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        ret, frame1 = cap.read()
        if ret:
            self.width1 = frame1.shape[1]
            self.height1 = frame1.shape[0]

        p.put(frame1)
        while True:
            ret, frame1 = cap.read()
            if p.empty() == False:
                _ = p.get()
            if ret == False:
                cap = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
                ret, frame1 = cap.read()
                p.put(frame1)
            if ret:
                p.put(frame1)
            if self.breaker == True:
                cap.release()
                break

    def cam2(self):
        cap = cv.VideoCapture('rtsp://28628262:@192.168.0.170:554/live/ch00_1')
        ret, frame2 = cap.read()
        q.put(frame2)

        # width2 = frame2.shape[1]
        # height2 = frame2.shape[0]
        if ret:
            self.width2 = int(frame2.shape[1] * (self.scale/100))
            self.height2 = int(frame2.shape[0] * (self.scale/100))
        while True:
            ret, frame2 = cap.read()
            if q.empty() == False:
                _ = q.get()
            if ret == False:
                cap = cv.VideoCapture('rtsp://28628262:@192.168.0.170:554/live/ch00_1')
                ret, frame2 = cap.read()
                q.put(frame2)
            if ret:
                q.put(frame2)
            if self.breaker == True:
                cap.release()
                break


    def merge_stamp(self):
        p4 = threading.currentThread()
        
        while True:
            if p.empty != True:
                frame1 = p.get()
                
            if q.empty != True: 
                frame2 = q.get()

            dateValue = datetime.now(pytz.timezone('Asia/Taipei'))
            date_time = dateValue.strftime("%m/%d/%Y, %H:%M:%S")
            cv.putText(frame1, str(date_time), (10, 40), cv.FONT_HERSHEY_PLAIN, 1, (160, 50, 205), 2)
            cv.putText(frame2, str(date_time), (10, 40), cv.FONT_HERSHEY_PLAIN, 1, (160, 50, 205), 2)
            cTime = time.time()
            elapsed_time = cTime - self.pTime
            
            if elapsed_time>0:
                fps = 1/elapsed_time
                cv.putText(frame1, str(int(fps)), (int(self.width1 - 40), 40), cv.FONT_HERSHEY_PLAIN, 1, (255, 50, 50), 2)
                cv.putText(frame2, str(int(fps)), (int(self.width2 - 40), 40), cv.FONT_HERSHEY_PLAIN, 1, (255, 50, 50), 2)
            self.pTime = cTime
            
            if p.empty() != True:
                _ = p.get()
            p.put(frame1)
            
            if q.empty() != True:
                _ = q.get()
            q.put(frame2)

            if self.breaker == True:
                break

    def display(self):
        
        while True:
            if p.empty() != True and q.empty() != True:
                f1 = p.get()
                f2 = q.get()
                self.out1.write(f1)
                self.out2.write(f2)
                
                if a.empty() != True:
                    _ = p.get()
                a.put(f1)
                
                if b.empty() != True:
                    _ = q.get()
                b.put(f2)


                self.end_hour = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%H")

                if self.end_hour != self.start_hour:
                    self.start_hour = self.end_hour
                    self.hour_counter+=1
                    
                    if self.hour_counter == 24:
                        print(f"cam1_output_{self.vid_no} released")
                        print(f"cam2_output_{self.vid_no} released")
                        self.hour_counter = 0
                        self.vid_no += 1
                        
                        self.out1.release()
                        self.out2.release()
                        
                        self.out1 = cv.VideoWriter(f'cam_output_{self.vid_no}.avi', self.fourcc, 10.0, (self.width1, self.height1))
                        self.out2 = cv.VideoWriter(f'cam_output_{self.vid_no}.avi', self.fourcc, 10.0, (self.width2, self.height2))
                
            cv.waitKey(1)
            if self.breaker == True:
                self.out1.release()
                self.out2.release()
                break
  
    def video(self):
        #cap = cv.VideoCapture(0)
        self.breaker = False

        while True:
            #print("Baal")
            #QApplication.processEvents()

            #ret, frame = cap.read()    
            # self.label.setText(str(frame))
            if a.empty() != True:
                ff1 = a.get()
                self.display1(ff1)
            if b.empty() != True:
                ff2 = b.get()
                self.display2(ff2)
            #self.display2()
            
            # if cv.waitKey(1) and 0xFF == ord('q'): 
            #     break 
            #cv.waitKey()
            if (self.click % 2 == 0):
                self.pushButton.setText("Start")
                self.breaker = True
                break

    def not_video(self): 
        # while True:
        #     if (self.click % 2 != 0):
        #         self.video()
        pass
    
    
    def display1(self, frame): 
        qformat = QImage.Format_Indexed8
        if len(frame.shape) == 3: 
            if (frame.shape[2]) == 4: 
                qformat = QImage.Format_RGBA888
            else: 
                qformat = QImage.Format_RGB888
        frame = QImage(frame, frame.shape[1], frame.shape[0], qformat)
        frame = frame.rgbSwapped()
        self.label_cam1.setPixmap(QPixmap.fromImage(frame))
            # self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    def display2(self, frame): 
        qformat = QImage.Format_Indexed8
        if len(frame.shape) == 3: 
            if (frame.shape[2]) == 4: 
                qformat = QImage.Format_RGBA888
            else: 
                qformat = QImage.Format_RGB888
        frame = QImage(frame, frame.shape[1], frame.shape[0], qformat)
        frame = frame.rgbSwapped()
        self.label_cam2.setPixmap(QPixmap.fromImage(frame))
        print('baal')
        # self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    p1 = threading.Thread(target=form.cam1)
    p2 = threading.Thread(target=form.cam2)
    p4 = threading.Thread(target=form.merge_stamp)
    p5 = threading.Thread(target=form.display)    
    p1.start()
    p2.start()
    p4.start()
    p5.start()
    sys.exit(app.exec_())
    

