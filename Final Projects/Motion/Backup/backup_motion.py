# Last edited: 03/10/2021

import cv2 as cv
import time
from datetime import datetime
import pytz
import shutil
from glob import glob
import os
import concurrent.futures
import smtplib
from email.message import EmailMessage
import imghdr
import os.path
from os import path
import psutil

import threading
import queue

p = queue.Queue()
q = queue.Queue()

class Motion:
    def __init__(self):
        # self.cap = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        self.cap = cv.VideoCapture(0)
        self.cap.set(cv.CAP_PROP_AUTOFOCUS, 0)
        self.fourcc = cv.VideoWriter_fourcc(*'XVID')
        self.out1 = cv.VideoWriter('output1.avi', self.fourcc, 20.0, (640, 480))
        self.out2 = cv.VideoWriter('output2.avi', self.fourcc, 20.0, (640, 480))

        ret, self.frame1 = self.cap.read()
        while ret == False:
            print("Camera Failed. Trying to re establish connection")
            ret, self.frame1 = self.cap.read()
        #self.frame1 = self.scaling(self.frame1, True)
        # self.frame1 = cv.flip(self.frame1, 1)
        ret, self.frame2 = self.cap.read()
        while ret == False:
            print("Camera Failed. Trying to re establish connection")
            ret, self.frame2 = self.cap.read()
        # self.frame2 = cv.flip(self.frame2, 1)
        #self.frame2 = self.scaling(self.frame2, True)

        self.frame = self.frame1.copy()
        self.ff = self.frame1.copy()
        self.f_send = self.frame1.copy()

        if p.empty() == False: 
            _ = p.get()
        
        p.put(self.frame1)

        if q.empty() == False: 
            _ = q.get()
        
        q.put(self.frame2)

        self.first = True
        self.second = False
        self.switch = False
        self.start = time.time()
        self.activator_1 = False 
        self.activator_2 = False
        self.take_1 = True 
        self.vid_no = 1
        self.detected = False
        self.pTime = 0
        self.face_number = 1
        self.send_mail = False
        self.frame_counter = 0
        self.motion_editor = False
        self.canceller = False
        self.enter_mail = True
        self.enter_process = True 
        self.stop_process = False
        self.f_counter = 0 
        self.fps = 0
        self.entered_face_detection = False
        self.x = 0 
        self.y = 0
        self.w = 0 
        self.h = 0
        self.space_low_email = False
        self.scale = 100
        self.space = 0
        self.motion = False  
        self.low_storage_mail = 0
        self.low_storage = False
        self.fps = 0
        self.cTime = 0
        self.pTime = 0
        self.thread_breaker = False
        # self.do_scale = False
        self.path_found = False
        self.allow_sync = False

        self.dateValue = datetime.now(pytz.timezone('Asia/Taipei'))
        self.date_time = self.dateValue.strftime("%d/%m/%Y, %H:%M:%S")

        for file in glob('motion_*.avi'):
            print (file)
            self.vid_no += 1
                            
        # for file in glob('temp_face_motion_*.avi'):
        #     print (file)
        #     for i in glob(file):
        #         os.remove(i)
    
    def process(self):
        while True: 
            if p.empty() == False and q.empty() == False: 
                f1 = p.get() 
                f2 = q.get()

                if p.empty() == True: 
                    p.put(f1)

                if q.empty() == True: 
                    q.put(f2)

                self.diff = cv.absdiff(f1, f2)
                self.gray = cv.cvtColor(self.diff, cv.COLOR_BGR2GRAY)
                self.blur = cv.GaussianBlur(self.gray, (5,5), 0)
                _, self.thresh = cv.threshold(self.blur, 20, 255, cv.THRESH_BINARY)
                self.dilated = cv.dilate(self.thresh, None, iterations=5)
                _, self.contours,_ = cv.findContours(self.dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)   

                counter = 0 

                self.motion_editor = False

                for contour in self.contours: 
                    (self.x, self.y, self.w, self.h) = cv.boundingRect(contour)

                    if cv.contourArea(contour) > 700:
                        # cv.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        # cv.putText(self.frame1, "DETECTED", (10, 40), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                        self.motion = True
                        self.detected = True
                        self.motion_editor = True
                        self.frame_counter+=1
                        if (self.frame_counter==10):
                            cv.rectangle(f1, (self.x, self.y), (self.x+self.w, self.y+self.h), (0, 255, 0), 1)
                            cv.imwrite('feed.jpg', f1)
                        if (self.frame_counter==1):
                            print(f"Motion detected at {self.date_time}")
                            cv.rectangle(f1, (self.x, self.y), (self.x+self.w, self.y+self.h), (0, 255, 0), 1)
                            cv.imwrite('feed.jpg', f1)
                            self.send_mail = True
                    
                    counter += 1
                    if counter>2: 
                        break
            if self.thread_breaker == True: 
                break

    
    def frame_edit(self):
        while True:
            self.dateValue = datetime.now(pytz.timezone('Asia/Taipei'))
            self.date_time = self.dateValue.strftime("%d/%m/%Y, %H:%M:%S") 
            cv.putText(self.ff, str(self.date_time), (10, 65), cv.FONT_HERSHEY_PLAIN, 1, (160, 50, 200), 2)  
            if self.motion_editor == True: 
                cv.rectangle(self.ff, (self.x, self.y), (self.x+self.w, self.y+self.h), (0, 255, 0), 1) 
                cv.putText(self.ff, "DETECTED", (10, 40), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
            if self.thread_breaker == True: 
                break

            
    def record(self):
        while True:
            # self.ff = self.frame1.copy()
            d_time = self.dateValue.strftime("(%d.%m.%Y) (%H-%M-%S)")

            if self.motion == True: 
                self.start = time.time()

            if self.first == True: 
                self.start = time.time()
                
                self.out1 = cv.VideoWriter('output1.avi', self.fourcc, 20.0, (640, 480))
                #print('first out1 initiated')
                #print(date_time)
                self.activator_1 = True
                self.first = False
                self.switch = True 
                self.take_1 = True
                self.start = time.time()
                self.second = True

            end = time.time()

            if self.second == True: 
                if (end-self.start)>=10:
                    self.start = time.time()
                    self.out2 = cv.VideoWriter('output2.avi', self.fourcc, 20.0, (640, 480))
                    #print('first out2 initiated')
                    #print(date_time)
                    self.activator_2 = True
                    self.take_1 = True
                    self.second = False

            end = time.time()

            if (end-self.start)>=10:
                self.start=end

                if self.switch == True:
                    self.out1.release()
                    if self.motion == False and self.detected == True :
                        self.detected = False
                        if self.take_1 == True: 
                            shutil.copyfile('output1.avi', f'motion_{self.vid_no} {d_time}.avi')
                            print(f'motion_{self.vid_no} {d_time}.avi saved')
                            self.frame_counter = 0
                            self.canceller = True
                            self.vid_no += 1
                            
                    #print("Out1 Released")
                    #print(date_time)
                    self.out1 = cv.VideoWriter('output1.avi', self.fourcc, 20.0, (640, 480))
                    self.activator_1 = True
                    #print("Out1 Initiated")
                    self.take_1 = False
                    #print(date_time)
                    self.switch = False

                elif self.switch == False:
                    self.out2.release()

                    if self.motion == False and self.detected == True :
                        self.detected = False
                        if self.take_1 == False: 
                            shutil.copyfile('output2.avi', f'motion_{self.vid_no} {d_time}.avi')
                            print(f'motion_{self.vid_no} {d_time}.avi saved')
                            self.frame_counter = 0
                            self.canceller = True
                            self.vid_no += 1

                    #print("Out2 Released")
                    #print(date_time)
                    self.out2 = cv.VideoWriter('output2.avi', self.fourcc, 20.0, (640, 480))
                    self.activator_2 = True
                    #print("Out2 Initiated")
                    self.take_1 = True 
                    #print(date_time)
                    self.switch = True
                    
            # self.ff = self.scaling(True)  

            if self.activator_1 == True: 
                self.out1.write(self.ff)

            if self.activator_2 == True: 
                self.out2.write(self.ff)
        
            if self.thread_breaker == True:
                self.out1.release()
                self.out2.release()
                self.cap.release()
                cv.destroyAllWindows()

                self.detected = False
                if self.take_1 == True: 
                    shutil.copyfile('output1.avi', f'motion_{self.vid_no} {d_time}.avi')
                    print(f'motion_{self.vid_no} {d_time}.avi saved')
                    self.frame_counter = 0
                    self.canceller = True
                    self.vid_no += 1 

                if self.take_1 == False: 
                    shutil.copyfile('output2.avi', f'motion_{self.vid_no} {d_time}.avi')
                    print(f'motion_{self.vid_no} {d_time}.avi saved')
                    self.frame_counter = 0
                    self.canceller = True
                    self.vid_no += 1
                
                for file in glob('output*.avi'):
                    # print (file)
                    for i in glob(file):
                        os.remove(i)

                break
            
        
    def scaling(self, frame, down_scale):
    
        if down_scale == True: 
            width = int(frame.shape[1] * (self.scale/100))
            height = int(frame.shape[0] * (self.scale/100))
            dsize = (width, height)
            frame = cv.resize(frame, dsize)
            
        
        elif down_scale == False: 
            width = int(frame.shape[1] * (100/self.scale))
            height = int(frame.shape[0] * (100/self.scale))
            dsize = (width, height)
            frame = cv.resize(frame, dsize)
        
        return frame

    def email(self):
        while True:
            if self.send_mail == True: 
                self.send_mail = False
                d_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%H")
                d_time = int(d_time)
                dd_time = self.dateValue.strftime("%d/%m/%Y, %H:%M:%S")
                greetings2 = "Have a nice day"
                if d_time >= 5 and d_time < 12:
                    greetings = "Good Morning"
                elif d_time >= 12 and d_time < 18:
                    greetings = "Good Afternoon"
                elif d_time >= 18 and d_time < 24:
                    greetings = "Good Evening"
                    greetings2 = "Good Night"
                elif d_time >= 0 and d_time < 5:
                    greetings = "Good Evening"
                    greetings2 = "Good Night"

                message = f'{greetings} \r\rMOTION DETECTED at {str(dd_time)}. \r\rThe recording of this motion will be saved under file name "motion_{self.vid_no} (Date) (Time).avi".\r \rThank you. {greetings2}.'
                sub = "MOTION DETECTED"

                if path.exists('feed.jpg') == True:
                    message = f'{greetings} \r\rMOTION DETECTED at {str(dd_time)}. \r\rThe recording of this motion is saved under file name "motion_{self.vid_no} (Date) (Time).avi".\rFor false alarm recognition,\rA file named "feed.jpg" is added in the attachments. \r \rThank you. {greetings2}. '

                if self.low_storage == True: 
                    message = f'{greetings} \r\rMemory running low. \rYour current disk space is {self.space} MB. \rTo continue recording, please free up some space.\r \rThank you. {greetings2}.'
                    sub = "Momory Running Low"

                msg = EmailMessage()
                
                msg.set_content(message)

                msg['Subject'] = sub
                msg['From'] = "intern1penco@gmail.com"
                msg['To'] = "moontasirsoumik@live.com"

                if self.low_storage == False: 
                    if path.exists('feed.jpg') == True:
                        with open ('feed.jpg', 'rb') as f:
                            file_data = f.read()
                            file_type = imghdr.what(f.name)
                            file_name = f.name
                        
                        msg.add_attachment(file_data, maintype='image', subtype = file_type, filename = file_name)

                #Send the message via our own SMTP server.
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login("intern1penco@gmail.com", "penco@123456")
                server.send_message(msg)
                server.quit()
                print("Email Sent")
                if path.exists('feed.jpg') == True:
                    os.remove('feed.jpg')
                
                self.low_storage = False 
            if self.thread_breaker == True: 
                break
    
    def space_check(self):
        while True:
            path = '/'
            bytes_avail = psutil.disk_usage(path).free
            megabytes_available = (bytes_avail / 1024 / 1024)

            if megabytes_available <= 1024: 
                self.low_storage = True
                if self.low_storage_mail < 1: 
                    self.low_storage_mail += 1 
                    self.send_mail = True
            else: 
                self.low_storage = False 

            self.space = megabytes_available 
            if self.thread_breaker == True: 
                break

    def frame_getter(self):
        while True: 
            ret, self.frame = self.cap.read()
            # self.frame = self.scaling(f, True)
            while ret == False:
                print("Camera Failed. Trying to re establish connection")
                ret, self.frame = self.cap.read()
            if self.thread_breaker == True: 
                break 

    def display(self):
        while True:
            self.motion = False
            self.cTime = time.time()
            elapsed_time = (self.cTime - self.pTime)
            if elapsed_time>0:
                self.fps = 1/(elapsed_time)
                cv.putText(self.ff, str(int(self.fps)), (600, 65), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                
            self.pTime = self.cTime
            self.motion = False

            self.frame1 = self.frame2 
            self.ff = self.frame2.copy()
            self.frame2 = self.frame 
            f1 = self.frame1.copy()
            f2  = self.frame2.copy()

            if p.empty() == False: 
                _ = p.get()
        
            p.put(f1)

            if q.empty() == False: 
                _ = q.get()
            
            q.put(f2)

            if self.thread_breaker == True: 
                break

    def sync(self): 
        while True:
            location = '/media/pi/Penco'
            if path.exists(location) == True:
                self.path_found = True 
            else: 
                self.path_found = False

            if self.path_found == True and self.allow_sync == True: 
                for file in glob('output*.avi'):
                    print (file)
                    shutil.copyfile(file, f'{location}/{file}')
                
                print("Sync Successful")
                self.allow_sync = False
            
            if self.allow_sync == True and self.path_found == False:
                print("Path not found. Sync disabled")
                self.allow_sync = False

            break
    

    def sync_runner(self): 
        p8 = threading.Thread(target = self.sync)
        p8.start()
    
    def runner(self):
        self.thread_breaker = False

        # self.cap = cv.VideoCapture('http://root:pass@192.168.0.112/axis-cgi/mjpg/video.cgi?')
        self.cap = cv.VideoCapture(0)
        self.cap.set(cv.CAP_PROP_AUTOFOCUS, 0)
        self.fourcc = cv.VideoWriter_fourcc(*'XVID')
        self.out1 = cv.VideoWriter('output1.avi', self.fourcc, 20.0, (640, 480))
        self.out2 = cv.VideoWriter('output2.avi', self.fourcc, 20.0, (640, 480))

        p1 = threading.Thread(target = self.process)
        p2 = threading.Thread(target = self.frame_edit)
        p3 = threading.Thread(target = self.record)
        p4 = threading.Thread(target = self.email)
        p5 = threading.Thread(target = self.space_check)
        p6 = threading.Thread(target = self.frame_getter)
        p7 = threading.Thread(target = self.display)

        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p5.start()
        p6.start()
        p7.start()
        

    def stopper(self):
        self.thread_breaker = True


# if __name__  == '__main__': 
#     m = Motion()
#     m.baal()
        

