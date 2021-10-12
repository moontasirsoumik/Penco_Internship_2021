#https://gist.github.com/ozcanyarimdunya/a030e607a2e8f67e5969c8ee544bd11c
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from feed1 import Ui_MainWindow
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore
import threading 


class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(__class__, self).__init__()
        self.setupUi(self)
        self.show()
        # self.btn_1.clicked.connect(lambda: self.btn_clicked('1'))
        self.pushButton.clicked.connect(lambda: self.btn_clicked())
        self.click = 0
        self.breaker = False

    def btn_clicked(self):
        print("Baal")
        self.click += 1
        
        if (self.click % 2 != 0):
            p1 = threading.Thread(target = self.video())
            p1.start()
            self.pushButton.setText("Pause")
            self.video()
        if (self.click % 2 == 0):
            self.not_video()
        
        # elif (self.click % 2 == 0):
        #     self.not_video()

    def video(self):
        #cap = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        QApplication.processEvents()
        cap = cv.VideoCapture(0)
        show = True
        while True:
            QApplication.processEvents()
            ret, frame = cap.read()     
            # self.label.setText(str(frame))
            self.display(frame)
            if show == True:
                cv.imshow("feed", frame)
                cv.destroyAllWindows()
                show = False
            if cv.waitKey(1) and 0xFF == ord('q'): 
                break 
            #cv.waitKey(1)
            
            if self.breaker == True:
                self.breaker = False
                break 
            

    def not_video(self):
        if (self.click % 2 == 0):
            self.pushButton.setText("Start")
            self.breaker = True
        # while True:
        #     if (self.click % 2 != 0):
        #         self.video()
        pass
         

    def display(self, frame): 
        qformat = QImage.Format_Indexed8

        if len(frame.shape) == 3: 
            if (frame.shape[2]) == 4: 
                qformat = QImage.Format_RGBA888
            else: 
                qformat = QImage.Format_RGB888
        frame = QImage(frame, frame.shape[1], frame.shape[0], qformat)
        frame = frame.rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(frame))
        # self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())
