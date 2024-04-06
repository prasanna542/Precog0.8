import base64
from doctest import master
import io
import os
import re
import socket
import tempfile
import PIL.Image
import PIL.ImageTk
import sys
from tkinter import *
from tkinter import messagebox
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Combobox
import pkg_resources
import pyrebase
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import Button, Frame, Label, StringVar, OptionMenu, messagebox, filedialog
from matplotlib import ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import pygame
import serial
import serial.tools.list_ports
import numpy as np
import threading
import time
import tkinter.font as tkFont
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from tkinter import font
import json
import os
import sys
import tkinter as tk
from tkinter import Button, Frame, Label, StringVar, OptionMenu, Toplevel, messagebox, filedialog
from fpdf import FPDF
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import pygame
import requests
import serial
import serial.tools.list_ports
import numpy as np
import threading
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from math import isnan
from tkinter import Text, Toplevel, Scrollbar, END
import json
import requests
import firebase_admin
from firebase_admin import credentials, storage,firestore
from os.path import basename
import uuid
from scipy.signal import butter, filtfilt, find_peaks
import time



# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS2', os.path.abspath('.'))
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)



def get_embedded_image_data(filename):
    # Define the path to the embedded image file
    if getattr(sys, 'frozen', False):
        # If the application is frozen (compiled with PyInstaller)
        filepath = sys._MEIPASS + "\\" + filename
    else:
        # If running in a development environment
        filepath = filename
    
    # Read the binary data of the image file
    with open(filepath, "rb") as f:
        binary_data = f.read()
    
    return binary_data



def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))



def check_internet_connection():
    try:
        # Attempt to connect to a well-known website
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


# firebase config for authentication


firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


# firebase config for database transactions
# cred = credentials.Certificate(resource_path("apadb-v2-replica-firebase-adminsdk-jqwml-c8d95c6f27.json"))
cred = credentials.Certificate(firebaseConfig2)
firebase_admin.initialize_app(cred, {'storageBucket': 'apadb-v2-replica.appspot.com'})

db = firestore.client()

#class to show loading screen 
class LoadingScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Loading...")
        self.geometry("200x100")
        self.resizable(False, False)

        self.label = ttk.Label(self, text="Loading...", font=("Helvetica", 14))
        self.label.pack(pady=20)

        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.pack(pady=10)
        self.progress_bar.start(10)
# ================================================================= triple sensor logic ============================================================

class TripleSensorLogic:
    def __init__(self,root,patient_name,no_of_sensors,dob,hospitalName,gender,height,weight,ank,rad,uid):
        self.patient = patient_name
        self.rad_value = rad
        self.ank_value = ank
        self.height= height


        self.root = root
        self.data2 = [(0, 0)] * 6000
   

        self.is_running = threading.Event()
        self.recording_data = []
        self.is_recording = False
        self.update_interval = int(0)  # Set default update interval

        # Initialize Pygame mixer
        pygame.mixer.init()

        self.create_widgets()
        self.setup_serial()
        self.start_data_acquisition()
        self.animate()

        self.data_thread = None



    def check_and_destroy(self):
        if self.stop_button['state'] == tk.NORMAL:
            self.stop_animation()
            self.top_frame.destroy()
            self.footer_label.destroy()
            self.main_frame.destroy()
            recordNewTestSelected()
            
        else:
            self.top_frame.destroy()
            self.footer_label.destroy()
            self.main_frame.destroy()
            recordNewTestSelected()



    def create_widgets(self):
        self.top_frame = Frame(frame1,bg="black")
        self.top_frame.pack(side=LEFT,expand=1,fill=BOTH)
            
        self.backbtn = Button(self.top_frame,bg="black",image=backbtnimageneon2,activebackground="black",border=0,highlightthickness=0,command=lambda:(self.top_frame.destroy(), self.footer_label.destroy(),self.main_frame.destroy(),recordNewTestSelected()))
        self.backbtn.pack(side=LEFT,pady=10,padx=(10,0))

        self.main_frame = Frame(frame2, bg='black')
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.fig = Figure(figsize=(6, 4), facecolor='#000000')

        self.ax1 = self.fig.add_subplot(311)  # Adjusted to (2, 1, 1) for 2 rows, 1 column, 1st subplot
        self.ax1.set_facecolor('#000000')
        self.ax1.grid(True, color='#555555', linestyle='--', linewidth=0.5)
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='white')

        self.ax2 = self.fig.add_subplot(312)  # Adjusted to (2, 1, 2) for 2 rows, 1 column, 2nd subplot
        self.ax2.set_facecolor('#000000')
        self.ax2.grid(True, color='#555555', linestyle='--', linewidth=0.5)
        self.ax2.tick_params(axis='x', colors='white')
        self.ax2.tick_params(axis='y', colors='white')


        self.ax3 = self.fig.add_subplot(313)  # Adjusted to (2, 1, 2) for 2 rows, 1 column, 2nd subplot
        self.ax3.set_facecolor('#000000')
        self.ax3.grid(True, color='#555555', linestyle='--', linewidth=0.5)
        self.ax3.tick_params(axis='x', colors='white')
        self.ax3.tick_params(axis='y', colors='white')


        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        control_frame = Frame(self.main_frame, bg='#000000')
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=10, expand=0)

        self.serialLabel = Label(control_frame, text="Serial Port", bg='#000000', fg='#fe007e', font=("Lucida Sans", 10))
        self.serialLabel.pack(side=tk.TOP, pady=5, padx=5)

        self.port_var = StringVar(self.root)
        self.port_var.set("Select Port")

        self.port_menu = OptionMenu(control_frame, self.port_var, *["Select Port"])
        self.port_menu.config(bg='#000000', fg='white', width=10, font=("Lucida Sans", 10), highlightthickness=2, highlightbackground="grey")
        self.port_menu.pack(side=tk.TOP, pady=5, padx=5)

        self.baud_var = StringVar(self.root)
        self.baud_var.set("9600")  # Set default baud rate
        baud_rates = ["9600", "19200", "38400", "57600", "115200"]

        self.baud_menu = OptionMenu(control_frame, self.baud_var, *baud_rates)
        self.baud_menu.config(bg='#000000', fg='white', width=10, font=("Lucida Sans", 10), highlightthickness=2, highlightbackground="grey")
        self.baud_menu.pack(side=tk.TOP, pady=5, padx=5)

        self.refresh_ports_button = Button(control_frame, text='Refresh Ports', command=self.update_ports_list, width=15, bg='#404040', fg='white', font=("Lucida Sans", 10))
        self.refresh_ports_button.pack(side=tk.TOP, pady=5, padx=5)

        self.update_ports_list()

        self.start_button = Button(control_frame, text='Connect', command=lambda:(self.start_animation(),self.start_recording_button.config(state=tk.NORMAL)), width=15, bg='#38B18E', fg='black', font=("Lucida Sans", 10))
        self.start_button.pack(side=tk.TOP, pady=5, padx=5)

        self.stop_button = Button(control_frame, text='Disconnect', command=lambda:(self.stop_animation(),self.start_recording_button.config(state=tk.DISABLED)), state=tk.DISABLED, width=15, bg='#38B18E', fg='black', font=("Lucida Sans", 10))
        self.stop_button.pack(side=tk.TOP, pady=5, padx=5)
        

        self.baud_label = Label(control_frame, text="Record Option", bg='#000000', fg='#fe007e', font=("Lucida Sans", 10))
        self.baud_label.pack(side=tk.TOP, pady=(25,5), padx=5)

        self.start_recording_button = Button(control_frame, text='Start Recording', state=tk.DISABLED,command=self.start_recording, width=15, bg='#404040', fg='white', font=("Lucida Sans", 10))
        self.start_recording_button.pack(side=tk.TOP, pady=5, padx=5)

        self.stop_recording_button = Button(control_frame, text='Stop Recording', command=self.stop_recording, state=tk.DISABLED, width=15, bg='#404040', fg='white', font=("Lucida Sans", 10))
        self.stop_recording_button.pack(side=tk.TOP, pady=5, padx=5)

        self.generate_report_button = Button(control_frame, text='Generate Report', command=lambda:(self.generate_report(self.file_path)), state=tk.DISABLED, width=15, bg='#404040', fg='white', font=("Lucida Sans", 10))
        self.generate_report_button.pack(side=tk.TOP, pady=5, padx=5)

        self.patientName_Label = Label(control_frame, text=f"Patient Name:{self.patient}", bg='#000000', fg='white', font=("Lucida Sans", 10))
        self.patientName_Label.pack(side=tk.TOP, pady=(25,5), padx=5)

        self.footer_label= Label(frame3,bg="white",text="Copyright © 2024 Acuradyne Systems")
        self.footer_label.pack(expand=1,fill=BOTH)

    def setup_serial(self):
        self.ser = None

    def start_data_acquisition(self):
        aa = time.time() #starting epoch 
        self.data1 = np.zeros(6000)
        self.data2 = np.zeros(6000)
        self.data3 = np.zeros(6000)


        self.data_lock = threading.Lock()

        def acquire_data():
            while self.is_running.is_set():
                try:
                    line = self.ser.readline().decode().strip()
                    value1, value2, value3, timestamp = map(float, line.split(','))

                    with self.data_lock:
                        self.data1 = np.append(self.data1, value1)
                        self.data1 = self.data1[-6000:]

                        self.data2 = np.append(self.data2, value2)
                        self.data2 = self.data2[-6000:]

                        self.data3 = np.append(self.data3, value3)
                        self.data3 = self.data3[-6000:]


                        if self.is_recording:
                            self.recording_data.append((value1, value2, value3, timestamp))

                except (serial.SerialException, ValueError, IndexError):
                    pass

        self.acquire_data = acquire_data

    def animate(self):
        self.lines1, = self.ax1.plot(self.data1, label='Sensor 1', color='#34ebc9', linewidth=1.0)
        self.lines2, = self.ax2.plot(self.data2, label='Sensor 2', color='#ffcc00', linewidth=1.0)
        self.lines3, = self.ax3.plot(self.data3, label='Sensor 3', color='green', linewidth=1.0)


        def update_plot(frame):
            with self.data_lock:
                self.lines1.set_ydata(self.data1)
                self.ax1.relim()
                self.ax1.autoscale_view(True, True, True)

            with self.data_lock:
                self.lines2.set_ydata(self.data2)
                self.ax2.relim()
                self.ax2.autoscale_view(True, True, True)

            with self.data_lock:
                self.lines3.set_ydata(self.data3)
                self.ax3.relim()
                self.ax3.autoscale_view(True, True, True)


        animation = FuncAnimation(self.fig, update_plot, interval=self.update_interval, cache_frame_data=False)

        self.ax1.set_xticks(np.arange(0, 6001, 1200))
        self.ax1.set_xticklabels(['0','1', '2', '3', '4', '5'])
        self.ax2.set_xticks(np.arange(0, 6001, 1200))
        self.ax2.set_xticklabels(['0','1', '2', '3', '4', '5'])
        self.ax3.set_xticks(np.arange(0, 6001, 1200))
        self.ax3.set_xticklabels(['0','1', '2', '3', '4', '5'])


        # Add labels to the axes
        # self.ax1.set_xlabel('Time (s)', color='grey', fontsize=10)
        # self.ax1.set_ylabel('Amplitude', color='grey', fontsize=10)
        # self.ax2.set_xlabel('Time (s)', color='grey', fontsize=10)
        self.ax2.set_ylabel('Amplitude', color='grey', fontsize=10)
        self.ax3.set_xlabel('Time (s)', color='grey', fontsize=10)
        # self.ax3.set_ylabel('Amplitude', color='grey', fontsize=10)


        self.canvas.draw()
        self.root.mainloop()

    def start_animation(self):
        self.start_button.config(state=tk.DISABLED)
        self.backbtn.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        with self.data_lock:
            self.data1 = np.zeros(6000)
            self.lines1.set_ydata(self.data1)
            self.ax1.relim()
            self.ax1.autoscale_view(True, True, True)

            self.data2 = np.zeros(6000)
            self.lines2.set_ydata(self.data2)
            self.ax2.relim()
            self.ax2.autoscale_view(True, True, True)

            self.data3 = np.zeros(6000)
            self.lines3.set_ydata(self.data3)
            self.ax3.relim()
            self.ax3.autoscale_view(True, True, True)


        selected_port = self.port_var.get()
        selected_baud = 115200

        if selected_port != "Select Port":
            try:
                self.ser = serial.Serial(selected_port, selected_baud, timeout=1)
                self.start_animation_thread()
            except serial.SerialException as e:
                self.show_error_message(f"Error opening serial port: {e}")
                self.stop_animation()

    def start_animation_thread(self):
        self.is_running.set()
        self.data_thread = threading.Thread(target=self.acquire_data, daemon=True)
        self.data_thread.start()

    def stop_animation(self):
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)


        self.bb = time.time()
        if((self.bb - self.aa) >10):
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()

        else:
            print("10 sec thamb")

        

    def start_recording(self):
        self.play_sound("csLRo1Kk.mp3") 
        self.start_recording_button.config(state=tk.DISABLED)
        self.stop_recording_button.config(state=tk.NORMAL)
        self.is_recording = True
        self.recording_data = []

    def generate_report(self, path):
        api_url = 'https://p7wk7vk2jaops7kow6kbikrz440cmqwj.lambda-url.ap-south-1.on.aws/'

        # Read the JSON file
        with open(path, 'r') as file:
            json_data = json.load(file)
            
        headers = {'Content-Type': 'application/json'}

        # Add additional fields to the JSON data
        json_data["d_notch_rad"] = 20
        json_data["d_notch_ank"] = 100
        json_data["person_height"]= 120

        # Make the POST request with the JSON data
        response = requests.post(api_url, json=json_data, headers=headers)

        # # Close loading screen
        # loading_screen.destroy()

        # Check the response status
        if response.status_code == 200:
            print("POST request successful!")
            print("Response:", response.json())

            # self.main_frame.destroy()
            
            # Display parameters in a new window
            self.show_parameters(response.json())
        else:
            print("POST request failed with status code:", response.status_code)
            print("Response:", response.text)


    def show_parameters(self, parameters):
        top_level = Toplevel(self.root,bg="white")
        # # top_level.attributes('-topmost', 1)
        # top_level.title("Parameter Details")
        # Get the screen width
        screen_width = top_level.winfo_screenwidth()
        screen_height = top_level.winfo_screenheight()
        x_position = (screen_width - 1024) // 2
        y_position = (screen_height - 600) // 2

        top_level.geometry(f'1024x600+{x_position}+{y_position}')
        top_level.attributes("-topmost", True) 
        top_level.resizable(False, False)  # Prevent resizing
        top_level.overrideredirect(True)


        def on_frame_configure(event):
            screen_height = root.winfo_height()
            font_size = int(screen_height / 60)

            label_precog.config(font=("helvetica",font_size+14))
            label_heading.config(font=("helvetica",font_size+16))
            label_parameter.config(font=("helvetica",font_size+12))
            label_value.config(font=("helvetica",font_size+12))
            label_pulserate.config(font=("helvetica",font_size))
            value_pulserate.config(font=("helvetica",font_size))
            label_pulseratevariance.config(font=("helvetica",font_size))
            value_pulseratevar.config(font=("helvetica",font_size))
            label_pulseratevarper.config(font=("helvetica",font_size))
            value_pulseratevarper.config(font=("helvetica",font_size))
            label_pulsewavevel.config(font=("helvetica",font_size))
            value_pulsewavevel.config(font=("helvetica",font_size))
            label_ejectiondur.config(font=("helvetica",font_size))
            value_ejectiondur.config(font=("helvetica",font_size))
            label_relcresttime.config(font=("helvetica",font_size))
            value_relcresttime.config(font=("helvetica",font_size))
            label_avgpulseheight.config(font=("helvetica",font_size))
            value_avgpulseheight.config(font=("helvetica",font_size))
            label_avgpulsewidth.config(font=("helvetica",font_size))
            value_avgpulsewidth.config(font=("helvetica",font_size))
            label_dicroticwavetime.config(font=("helvetica",font_size))
            value_dicroticwavetime.config(font=("helvetica",font_size))
            label_dicroticwaveheight.config(font=("helvetica",font_size))
            value_dicroticwaveheight.config(font=("helvetica",font_size))
            label_footer.config(font=("helvetica",font_size))

            # screen_width = top_level.winfo_width()
            # font_size = int(screen_width / 80)
            # top_level.config(font=("helvetica",font_size))
       
        frame_main = Frame(top_level,bg="white")
        frame_main.pack(expand=1,fill="both",padx=30,pady=30)

        frame1_inner = Frame(frame_main,bg="white")
        frame1_inner.pack(expand=1,fill="both",side="top")

        frame2_inner = Frame(frame_main,bg="white")
        frame2_inner.pack(expand=1,fill="both") 

        frame3_inner = Frame(frame_main,bg="white")
        frame3_inner.pack(expand=1,fill="both") 

        frame3_1_inner = Frame(frame3_inner,bg="white")
        frame3_1_inner.pack(side="left",expand=1,fill="both")

        frame3_2_inner = Frame(frame3_inner,bg="white")
        frame3_2_inner.pack(side="right",expand=1,fill="both")


        frame4_inner = Frame(frame_main,bg="black",height=2)
        frame4_inner.pack(expand=0,fill="x") 


        frame5_inner = Frame(frame_main,bg="white")
        frame5_inner.pack(expand=1,fill="both") 

        frame5_1_inner = Frame(frame5_inner,bg="white")
        frame5_1_inner.pack(side="left",expand=1,fill="both")

        frame5_2_inner = Frame(frame5_inner,bg="white")
        frame5_2_inner.pack(side="right",expand=1,fill="both")


        frame6_inner = Frame(frame_main,bg="black",height=2)
        frame6_inner.pack(expand=0,fill="x") 


        frame7_inner = Frame(frame_main,bg="white")
        frame7_inner.pack(expand=1,fill="both") 

        frame7_1_inner = Frame(frame7_inner,bg="white")
        frame7_1_inner.pack(side="left",expand=1,fill="both")

        frame7_2_inner = Frame(frame7_inner,bg="white")
        frame7_2_inner.pack(side="right",expand=1,fill="both")


        frame8_inner = Frame(frame_main,bg="black",height=2)
        frame8_inner.pack(expand=0,fill="x") 



        frame9_inner = Frame(frame_main,bg="white")
        frame9_inner.pack(expand=1,fill="both") 


        frame9_1_inner = Frame(frame9_inner,bg="white")
        frame9_1_inner.pack(side="left",expand=1,fill="both")

        frame9_2_inner = Frame(frame9_inner,bg="white")
        frame9_2_inner.pack(side="right",expand=1,fill="both")


        frame10_inner = Frame(frame_main,bg="black",height=2)
        frame10_inner.pack(expand=0,fill="x")

        frame11_inner = Frame(frame_main,bg="white")
        frame11_inner.pack(expand=1,fill="both") 

        frame11_1_inner = Frame(frame11_inner,bg="white")
        frame11_1_inner.pack(side="left",expand=1,fill="both")

        frame11_2_inner = Frame(frame11_inner,bg="white")
        frame11_2_inner.pack(side="right",expand=1,fill="both")


        frame12_inner = Frame(frame_main,bg="black",height=2)
        frame12_inner.pack(expand=0,fill="x")

        frame13_inner = Frame(frame_main,bg="white")
        frame13_inner.pack(expand=1,fill="both") 

        frame13_1_inner = Frame(frame13_inner,bg="white")
        frame13_1_inner.pack(side="left",expand=1,fill="both")

        frame13_2_inner = Frame(frame13_inner,bg="white")
        frame13_2_inner.pack(side="right",expand=1,fill="both")


        frame14_inner = Frame(frame_main,bg="black",height=2)
        frame14_inner.pack(expand=0,fill="x")


        frame15_inner = Frame(frame_main,bg="white")
        frame15_inner.pack(expand=1,fill="both") 

        frame15_1_inner = Frame(frame15_inner,bg="white")
        frame15_1_inner.pack(side="left",expand=1,fill="both")

        frame15_2_inner = Frame(frame15_inner,bg="white")
        frame15_2_inner.pack(side="right",expand=1,fill="both")

        frame16_inner = Frame(frame_main,bg="black",height=2)
        frame16_inner.pack(expand=0,fill="x")



        frame17_inner = Frame(frame_main,bg="white")
        frame17_inner.pack(expand=1,fill="both") 

        frame17_1_inner = Frame(frame17_inner,bg="white")
        frame17_1_inner.pack(side="left",expand=1,fill="both")

        frame17_2_inner = Frame(frame17_inner,bg="white")
        frame17_2_inner.pack(side="right",expand=1,fill="both")


        frame18_inner = Frame(frame_main,bg="black",height=2)
        frame18_inner.pack(expand=0,fill="x")


        frame19_inner = Frame(frame_main,bg="white")
        frame19_inner.pack(expand=1,fill="both") 

        frame19_1_inner = Frame(frame19_inner,bg="white")
        frame19_1_inner.pack(side="left",expand=1,fill="both")

        frame19_2_inner = Frame(frame19_inner,bg="white")
        frame19_2_inner.pack(side="right",expand=1,fill="both")


        frame20_inner = Frame(frame_main,bg="black",height=2)
        frame20_inner.pack(expand=0,fill="x")


        frame21_inner = Frame(frame_main,bg="white")
        frame21_inner.pack(expand=1,fill="both") 

        frame21_1_inner = Frame(frame21_inner,bg="white")
        frame21_1_inner.pack(side="left",expand=1,fill="both")

        frame21_2_inner = Frame(frame21_inner,bg="white")
        frame21_2_inner.pack(side="right",expand=1,fill="both")


        frame22_inner = Frame(frame_main,bg="black",height=2)
        frame22_inner.pack(expand=0,fill="x")

        frame23_inner = Frame(frame_main,bg="white")
        frame23_inner.pack(expand=1,fill="both") 

        frame23_1_inner = Frame(frame23_inner,bg="white")
        frame23_1_inner.pack(side="left",expand=1,fill="both")

        frame23_2_inner = Frame(frame23_inner,bg="white")
        frame23_2_inner.pack(side="right",expand=1,fill="both")

        frame24_inner = Frame(frame_main,bg="black",height=2)
        frame24_inner.pack(expand=0,fill="x")

        frame25_inner = Frame(frame_main,bg="white")
        frame25_inner.pack(expand=0,fill="x")




        # #content 
        label_precog = Label(frame1_inner,text="PRECOG",bg="white",fg="#464DB6")
        label_precog.pack(side="left")

        back_btn = Button(frame2_inner,image=backbtnimageblue2,border=0,highlightthickness=0,bg="white",command=lambda:(top_level.destroy()))
        back_btn.pack(side=LEFT)

        label_heading = Label(frame2_inner,text="Preview: Cardio Vascular Risk Analysis",fg="#464DB6",bg="white")
        label_heading.pack(side=LEFT)

        self.label_download_status = Label(frame2_inner,bg="white",fg="#464DB6")
        self.label_download_status.pack(side=RIGHT)

        download_button = Button(frame2_inner,image=downloadbutton2,border=0,highlightthickness=0,command=lambda:(self.download_parameters_pdf(parameters)))
        download_button.pack(side="right")

        label_parameter = Label(frame3_1_inner,text="Parameters",bg="white",fg="#464DB6")
        label_parameter.pack()
        
        label_value = Label(frame3_2_inner,text="Observed value",bg="white",fg="#464DB6")
        label_value.pack()

        label_pulserate = Label(frame5_1_inner,text="Pulse rate (BPM)",border=0,bg="white")
        label_pulserate.pack()

        value_pulserate = Label(frame5_2_inner,text=f"{parameters['pulse_rate']['mean']}",border=0,bg="white")
        value_pulserate.pack()

      
        label_pulseratevariance = Label(frame7_1_inner,text="Pulse rate variance",border=0,bg="white")
        label_pulseratevariance.pack()


        value_pulseratevar = Label(frame7_2_inner,text=f"{parameters['pulse_rate']['var']}",border=0,bg="white")
        value_pulseratevar.pack()  


        label_pulseratevarper = Label(frame9_1_inner,text="%Pulse rate variance (%)",border=0,bg="white")
        label_pulseratevarper.pack()

        value_pulseratevarper = Label(frame9_2_inner,text=f"{parameters['pulse_rate']['var_percent']}",border=0,bg="white")
        value_pulseratevarper.pack()  


        label_pulsewavevel = Label(frame11_1_inner,text="Pulse wave velocity(m/s)",border=0,bg="white")
        label_pulsewavevel.pack()

        value_pulsewavevel = Label(frame11_2_inner,text=f"{parameters['pulse_wave']['velocity']}",border=0,bg="white")
        value_pulsewavevel.pack()  



        label_ejectiondur = Label(frame13_1_inner,text="Ejection duration (ms)",border=0,bg="white")
        label_ejectiondur.pack()

        value_ejectiondur = Label(frame13_2_inner,text=f"{parameters.get('eject_duration')}",border=0,bg="white")
        value_ejectiondur.pack()  


        label_relcresttime = Label(frame15_1_inner,text="Rel. crest time (s)",border=0,bg="white")
        label_relcresttime.pack()

        value_relcresttime = Label(frame15_2_inner,text=f"{parameters.get('rel_crest_time')}",border=0,bg="white")
        value_relcresttime.pack()  



        label_avgpulseheight = Label(frame17_1_inner,text="Avg. pulse height (mV)",border=0,bg="white")
        label_avgpulseheight.pack()

        value_avgpulseheight = Label(frame17_2_inner,text=f"{parameters['pulse']['height']}",border=0,bg="white")
        value_avgpulseheight.pack()  


        label_avgpulsewidth = Label(frame19_1_inner,text="Avg. pulse width dur. (ms)",border=0,bg="white")
        label_avgpulsewidth.pack()

        value_avgpulsewidth = Label(frame19_2_inner,text=f"{parameters['pulse']['width']}",border=0,bg="white")
        value_avgpulsewidth.pack()  


        label_dicroticwavetime = Label(frame21_1_inner,text="Dicrotic wave time (ms)",border=0,bg="white")
        label_dicroticwavetime.pack()

        value_dicroticwavetime = Label(frame21_2_inner,text=f"{parameters.get('dicr_wave_time')}",border=0,bg="white")
        value_dicroticwavetime.pack()  


        label_dicroticwaveheight = Label(frame23_1_inner,text="Avg. dicrotic wave height (mV)",border=0,bg="white")
        label_dicroticwaveheight.pack()

        value_dicroticwaveheight = Label(frame23_2_inner,text=f"{parameters.get('dicr_height_mean')}",border=0,bg="white")
        value_dicroticwaveheight.pack()  

        label_footer = Label(frame25_inner,text="Copyright © 2024 Acuradyne Systems")

        frame_main.bind("<Configure>", on_frame_configure)




    def download_parameters_pdf(self, json_data):
        if json_data:
            # Ask the user for the file path and name
            # file_path = filedialog.asksaveasfilename(defaultextension=".apa", filetypes=[("PDF files", "*.pdf")])
            # file_path = 
            # Get the user's downloads folder path
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            file_name = "Precog_Report.apa"
            self.today_timestamp = datetime.now().date()
            self.today_milliseconds = int(datetime.now().timestamp() * 1000)
            self.final_file_path = f"{self.patient}_{self.today_timestamp}_{self.today_milliseconds}_{file_name}"
            # Construct the new file path by appending the desired file name to the downloads folder path
            file_path = os.path.join(downloads_folder, self.final_file_path)




            if not file_path:
                # User canceled the save operation
                return


            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Load logo image
            try:
                # Save the binary image data to temporary files
                desktop_icon_data = get_embedded_image_data("images\\desktopicon.png")
                desktop_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                desktop_icon_temp_file.write(desktop_icon_data)
                desktop_icon_temp_file.close()

                precog_icon_data = get_embedded_image_data("images\\Precog.png")
                precog_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                precog_icon_temp_file.write(precog_icon_data)
                precog_icon_temp_file.close()

                # Now use the paths to the temporary files in the pdf.image() function
                pdf.image(desktop_icon_temp_file.name, x=86, y=10, w=12)
                pdf.image(precog_icon_temp_file.name, x=100, y=12, w=30)

                # Don't forget to clean up the temporary files after using them
                os.unlink(desktop_icon_temp_file.name)
                os.unlink(precog_icon_temp_file.name)
            except Exception as e:
                print("Error loading image:", e)

            # Define colors
            header_color = (89, 124, 146)  # #597C92

            # Move cursor to a new line after the logo
            pdf.ln(30)

            # Add Test Details heading with font color #597C92
            pdf.set_font("Times", size=15, style='B')
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test Details", ln=True, align='L', fill=False)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Add Test Details with background color #E5F7DF
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_font("Arial", size=12)
            # Get the current date and time
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            test_details = [
                f"Name : {self.patient}",
                f"Date : {current_date}",
                f"Age/Gender : ",
                f"Time : {current_time}",
                f"Patient ID :",
                f"Referred by :",
                f"Weight/Height : /{self.height}",
                f"BP :",
                f"Tech./Clinician name :",
                ""
            ]
            cell_width = pdf.w / 2
            for i in range(len(test_details)):
                linebreak=False
                if i%2!=0:
                    linebreak=True
                if i==len(test_details)-1:
                    linebreak=True
                pdf.cell(cell_width, 10, txt=test_details[i], ln=linebreak, fill=True)

            pdf.cell(0, 10, txt="", ln=True)

            # Add CARDIO VASCULAR RISK ANALYSIS text
            pdf.set_font("Times", size=15, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="CARDIO VASCULAR RISK ANALYSIS", ln=True, align='C')
            
            # Add Test report and observations text
            pdf.set_font("Arial", size=14, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test report and observations", ln=True, align='C')
            # pdf.ln(10)  # Add a line break

            # Adding table headers with colors
            pdf.set_fill_color(*header_color)
            pdf.set_text_color(255, 255, 255)  # White font color for headers
            pdf.cell(65, 10, txt="Parameter", ln=0, align='C', fill=True)
            pdf.cell(65, 10, txt="Values", ln=0, align='C', fill=True)
            pdf.cell(65, 10, txt="Unit", ln=1, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Adding table data with colors
            parameters = [
                ["Pulse Rate", str(json_data.get("pulse_rate", {}).get("mean", "-")), "bpm"],
                ["Pulse Rate Variance", str(json_data.get("pulse_rate", {}).get("var", "-")), "-"],
                ["Stiffness Index", str(json_data.get("si_mean", "-")), "-"],
                ["Augmentation Index", str(json_data.get("ai_mean", "-")), "%"],
                ["Pulse Wave Velocity", str(json_data.get("pulse_wave", {}).get("velocity", "-")), "m/s"],
                ["Ejection Duration", str(json_data.get("eject_duration", "-")), "ms"],
                ["Relative Crest Time Ratio", str(json_data.get("rel_crest_time", "-")), "s"],
                ["Average Pulse Height", str(json_data.get("pulse", {}).get("height", "-")), "mV"],
                ["Average Pulse Width Duration", str(json_data.get("pulse", {}).get("width", "-")), "ms"],
                ["Dichrotic Wave Time", str(json_data.get("dicr_wave_time", "-")), "ms"],
                ["Average Dicrotic Wave Height", str(json_data.get("pulse_wave", {}).get("transit_time", "-")), "mV"],
                ["Delay Time", str(json_data.get("delay_time", "-")), "ms"]
            ]

            for i, parameter in enumerate(parameters):
                for j, val in enumerate(parameter):
                    if j == 0:  # First column background color
                        pdf.set_fill_color(207, 236, 237)  # #CFECED
                        pdf.set_font("Arial", size=12)  # Set font size to 12 for content
                        pdf.cell(65, 10, txt=val, ln=0, align='L', fill=True)
                    elif j in (1, 2):  # Second and third column background color
                        pdf.set_fill_color(229, 247, 223)  # #E5F7DF
                        pdf.set_font("Arial", size=12)  # Set font size to 12 for content
                        pdf.cell(65, 10, txt=val, ln=0, align='C', fill=True)
                    else:
                        pdf.set_font("Arial", size=14)  # Reset font size to 14 for headers
                        pdf.cell(65, 10, txt=val, ln=0, align='C', fill=True)
                pdf.cell(0, 10, txt="", ln=True)  # Adding a new line after each row

            pdf.output(file_path)
            print(f"PDF report generated successfully: {file_path}")
            self.label_download_status.config(text="Done! Check downloads folder")   
           
        else:
            print("No JSON data received")

    def play_sound(self,sound_data):
        # Save the sound data to a temporary file
        temp_file_path = "temp_sound.mp3"
        with open(temp_file_path, "wb") as f:
            f.write(sound_data)
        
        # Initialize the mixer module
        pygame.mixer.init()
        
        try:
            # Load and play the sound file
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Error playing sound: {e}")
        finally:
            # Clean up: close the mixer and delete the temporary file
            pygame.mixer.quit()
            os.remove(temp_file_path)

    def stop_recording(self):
        self.play_sound("sounds\\beep-06.mp3")
        self.stop_recording_button.config(state=tk.DISABLED)
        self.start_recording_button.config(state=tk.NORMAL)
       
        self.is_recording = False

        if self.recording_data:
            self.save_data()

    def save_data(self):
        file_name = "graphData.json"
        self.today_timestamp = int(datetime.now().timestamp())
        self.today_milliseconds = int(datetime.now().timestamp() * 1000)
        self.final_file_path = f"{self.patient}_{self.today_timestamp}_${self.today_milliseconds}$_{file_name}"
        self.file_path = os.path.join("readings",self.final_file_path)

        try:
            json_data = {"Signal-1": [], "Signal-2": [], "Signal-3": []}

            for data_point in self.recording_data:
                json_data["Signal-1"].append(data_point[0])  # Add values to Signal-1 array
                json_data["Signal-2"].append(data_point[1])  # Add zeros to Signal-2 array
                json_data["Signal-3"].append(data_point[2])  # Add timestamp values to Signal-3 array

            with open(self.file_path, 'w') as file:
                json.dump(json_data, file, indent=2)

            messagebox.showinfo("Success", "Data saved successfully.")
            self.generate_report_button.config(state=tk.NORMAL)

            
        except Exception as e:
            self.show_error_message(f"Error saving data: {e}")




# # ==============================================================



    def update_ports_list(self):
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        menu = self.port_menu["menu"]
        menu.delete(0, "end")
        for port in available_ports:
            menu.add_command(label=port, command=lambda p=port: self.port_var.set(p))

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

# =============================================================== double sensor logic =========================================================

class DoubleSensorLogic:



                                                                                                                            
# ============================ old logic for double sensor ends here ======================
        
    def __init__(self, root,patientName,noofsensor,dob,hospitalName,gender,height,weight,d_notch_ank, d_notch_rad,uid):  
    
        self.patient = patientName
        self.noofsensor = noofsensor
        self.dob = dob
        self.hospitalName = hospitalName
        self.gender = gender
        self.weight = weight
        self.rad_value = d_notch_rad
        self.ank_value = d_notch_ank
        self.height= height
        self.uid = uid              

        self.graphcolor = "red"
        self.color_thread = None  # Initialize color determination thread
        
        # self.weight = weight
        # self.age = age
        # self.gender = gender

        print(self.patient)
        self.root = root
  
     # Create a lock for shared resources
        self.is_running = threading.Event()
        self.recording_data = []
        self.is_recording = False
        self.update_interval = int(0)  # Set default update interval

        self.start_time = None
        self.timer_running = False

        # Initialize Pygame mixer
        pygame.mixer.init()

        self.create_widgets()
        # self.start_animation()
        self.setup_serial()
        self.start_data_acquisition()
        self.animate()
        

        self.data_thread = None

    def disconnect_and_go_home(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            

        except Exception as e:
            pass
            # Handle any exceptions that may occur
            # messagebox.showerror("Error", f"An error occurred while disconnecting and going back: {str(e)}")

        # Destroy frames
        self.top_frame.destroy()
        self.footer_label.destroy()
        self.main_frame.destroy()
        
        # Call the function to go back
        Modules()

    def disconnect_and_go_helpsupport(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            

        except Exception as e:
            pass
            # Handle any exceptions that may occur
            # messagebox.showerror("Error", f"An error occurred while disconnecting and going back: {str(e)}")

        # Destroy frames
        self.top_frame.destroy()
        self.footer_label.destroy()
        self.main_frame.destroy()
        
        # Call the function to go back
        help_support(self.patient,self.noofsensor,self.dob,self.hospitalName,self.gender,self.weight,self.rad_value,self.ank_value,self.height,self.uid)

    def disconnect_and_go_back(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            

        except Exception as e:
            pass
            # Handle any exceptions that may occur
            # messagebox.showerror("Error", f"An error occurred while disconnecting and going back: {str(e)}")

        # Destroy frames
        self.top_frame.destroy()
        self.footer_label.destroy()
        self.main_frame.destroy()
        
        # Call the function to go back
        recordNewTestSelected()

    def on_frame_configure(self, event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)

        self.label_precog.config(font=("helvetica",font_size+14))
        self.home_btn.config(font=("helvetica",font_size))
        self.back_btn.config(font=("helvetica",font_size))
        self.help_btn.config(font=("helvetica",font_size))


        # label_add_patient.config(font=("helvetica",font_size+14))
        # entry_name.config(font=("helvetica",font_size))
       
    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            time_string = f"{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_string)
            self.timer_label.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def go_to_generate_report(self):
        try:
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
        except Exception as e:
            pass

        generate_report(self.file_path,self.patient, self.noofsensor,self.dob,self.hospitalName,self.gender,self.weight,self.rad_value,self.ank_value,self.height,self.uid)

    def create_widgets(self):
       

        self.top_frame = Frame(frame1,bg="white")
        self.top_frame.pack(side=LEFT,expand=1,fill=BOTH)
            
        frame1_1 = Frame(self.top_frame, bg="white")
        frame1_1.pack(expand=1, fill="both", side="left")

        frame1_2 = Frame(self.top_frame, bg="white")
        frame1_2.pack(expand=1, fill="both", side="right")
        #content 
        self.label_precog = Label(frame1_1,text="PRECOG",bg="white",fg="#464DB6")
        self.label_precog.pack(anchor=W,padx=5)

        self.home_btn = Button(frame1_2,text="Home",bg="white",border=0,highlightthickness=0,fg="#464DB6",command=lambda:(self.disconnect_and_go_home()))
        self.home_btn.pack(side=RIGHT,anchor=E,padx=5)

        self.help_btn = Button(frame1_2,text="Help & support",bg="white",border=0,highlightthickness=0,fg="#464DB6",command=lambda:( self.top_frame.destroy(),self.footer_label.destroy(),self.main_frame.destroy(),self.disconnect_and_go_helpsupport()))
        self.help_btn.pack(side=RIGHT,anchor=E,padx=5)


        self.back_btn = Button(frame1_1,image=backbtnimageblue2,border=0,highlightthickness=0,bg="white",command=lambda:(self.disconnect_and_go_back()))
        self.back_btn.pack(anchor=W,padx=5,pady=(5,0))

        self.top_frame.bind("<Configure>", self.on_frame_configure)

        self.main_frame = Frame(frame2, bg='white')
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.fig = Figure(figsize=(6, 4), facecolor='white')
        self.ax = self.fig.add_subplot(211)
        self.ax.set_facecolor('white')
        self.ax.grid(True, color='#DCE6FE', linestyle='--', linewidth=0.5)
        self.ax.tick_params(axis='x', colors='#2B318A')
        self.ax.tick_params(axis='y', colors='#2B318A')


        self.ax2 = self.fig.add_subplot(212)  # Adjusted to (2, 1, 2) for 2 rows, 1 column, 2nd subplot
        self.ax2.set_facecolor('white')
        self.ax2.grid(True, color='#DCE6FE', linestyle='--', linewidth=0.5)
        self.ax2.tick_params(axis='x', colors='#2B318A')
        self.ax2.tick_params(axis='y', colors='#2B318A')





#         self.fig = Figure(figsize=(6, 4), facecolor='#000000')
#         self.ax1 = self.fig.add_subplot(211)  # Adjusted to (2, 1, 1) for 2 rows, 1 column, 1st subplot
#         self.ax1.set_facecolor('#000000')
#         self.ax1.grid(True, color='#555555', linestyle='--', linewidth=0.5)
#         self.ax1.tick_params(axis='x', colors='white')
#         self.ax1.tick_params(axis='y', colors='white')

#         self.ax2 = self.fig.add_subplot(212)  # Adjusted to (2, 1, 2) for 2 rows, 1 column, 2nd subplot
#         self.ax2.set_facecolor('#000000')
#         self.ax2.grid(True, color='#555555', linestyle='--', linewidth=0.5)
#         self.ax2.tick_params(axis='x', colors='white')
#         self.ax2.tick_params(axis='y', colors='white')



        self.ax.spines['top'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')



        self.ax2.spines['top'].set_color('white')
        self.ax2.spines['bottom'].set_color('white')
        self.ax2.spines['left'].set_color('white')
        self.ax2.spines['right'].set_color('white')


        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        control_frame = Frame(self.main_frame, bg='white')
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=10, expand=0)

        serial_frame = Frame(control_frame, bg='white', highlightthickness=1, highlightbackground='#2B318A')
        serial_frame.pack(padx=2, pady=10, expand=0)

        recording_frame = Frame(control_frame, bg='white', highlightthickness=1, highlightbackground='#2B318A')
        recording_frame.pack(padx=2, pady=10, expand=0)

        self.serialLabel = Label(serial_frame, text="Serial Port", bg='white', fg='#464DB6', font=("helvetica", 10))
        self.serialLabel.pack(side=tk.TOP, pady=5, padx=5)

        self.port_var = StringVar()
        self.port_var.set("Select Port")

        self.port_menu = OptionMenu(serial_frame, self.port_var, *["Select Port"])
        self.port_menu.config(bg='white', fg='#464DB6', width=11, font=("helvetica", 12), highlightthickness=2, highlightbackground="grey")
        self.port_menu.pack(side=tk.TOP, pady=0, padx=5)


        running_port = self.detect_active_port()
        self.port_var.set(running_port)

        self.port_checker_thread = threading.Thread(target=self.check_for_new_ports)
        self.port_checker_thread.start()




        # self.baud_var = StringVar(self.root)
        # self.baud_var.set("9600")  # Set default baud rate
        # baud_rates = ["9600", "19200", "38400", "57600", "115200"]

        # self.baud_menu = OptionMenu(control_frame, self.baud_var, *baud_rates)
        # self.baud_menu.config(bg='#000000', fg='white', width=10, font=("Lucida Sans", 10), highlightthickness=2, highlightbackground="grey")
        # self.baud_menu.pack(side=tk.TOP, pady=5, padx=5)

        self.refresh_ports_button = Button(serial_frame, image=refreshportbtn3, highlightthickness=0,border=0, command=self.check_for_new_ports)
        self.refresh_ports_button.pack(side=tk.TOP, pady=5, padx=5)

        self.update_ports_list()

        self.start_button = Button(serial_frame, image=connectbtn3,border=0,highlightthickness=0, command=lambda:(self.start_animation(),self.start_recording_button.config(state=tk.NORMAL)))
        self.start_button.pack(side=tk.TOP)

        self.stop_button = Button(serial_frame, image=disconnectbtn3, border=0,highlightthickness=0,command=lambda:(self.stop_animation(),self.start_recording_button.config(state=tk.DISABLED)), state=tk.DISABLED)
        self.stop_button.pack(side=tk.TOP)

        self.baud_label = Label(recording_frame, text="Record Option",bg="white",fg="#464DB6", font=("helvetica", 10))
        self.baud_label.pack(side=tk.TOP,padx=10,pady=5)

        self.start_recording_button = Button(recording_frame, image=startrecordingbtn3, border=0,highlightthickness=0,state=tk.DISABLED,command=self.start_recording)
        self.start_recording_button.pack(side=tk.TOP,padx=5)

        self.stop_recording_button = Button(recording_frame, image=stoprecordingbtn3,border=0,highlightthickness=0, command=self.stop_recording, state=tk.DISABLED)
        self.stop_recording_button.pack(side=tk.TOP)

        self.generate_report_button = Button(recording_frame,image=generatereportbtn3 ,border=0,highlightthickness=0, command=lambda:(self.main_frame.destroy(),self.top_frame.destroy(),self.footer_label.destroy(),self.go_to_generate_report()), state=tk.DISABLED)
        self.generate_report_button.pack(side=tk.TOP)

        self.patientName_Label = Label(control_frame, bg="white",fg="#464DB6",text=f"Patient Name: {self.patient}",font=("Lucida Sans", 12))
        self.patientName_Label.pack(side=tk.TOP)


        self.timer_label  = Label(control_frame, text="00:00",bg="white",fg="#464DB6", font=("Lucida Sans", 12))
        self.timer_label.pack(side=tk.BOTTOM)
        self.timer_label2  = Label(control_frame, text="Timer",bg="white",fg="#464DB6", font=("helvetica", 12))
        self.timer_label2.pack(side=tk.BOTTOM)

        self.footer_label= Label(frame3,bg="white",text="Copyright © 2024 Acuradyne Systems")
        self.footer_label.pack(expand=1,fill=BOTH,pady=0)

    def detect_active_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                ser = serial.Serial(port.device, timeout=1)
                if ser.is_open:
                    ser.close()
                    return port.device
                    
            except (OSError, serial.SerialException):
                pass
        return None

    def check_for_new_ports(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            with self.data_lock:
                self.data = np.zeros(6000)
                self.lines.set_ydata(self.data)
                self.ax.relim()
                self.ax.autoscale_view(True, True, True)
            
        except Exception as e:
            pass

        self.update_ports_list()
            # self.start_button.config(state=state)
        # while True:
        # if self.main_frame.winfo_exists():
        active_port = self.detect_active_port()
        if active_port:
            self.port_var.set(active_port)
            
            self.start_button.config(state=ACTIVE)
            self.stop_button.config(state=DISABLED)
            self.start_recording_button.config(state=DISABLED)
            self.stop_recording_button.config(state=DISABLED)



            # self.start_animation()
            # self.start_recording_button.config(state=tk.NORMAL)
            # Optionally, disable self.port_menu and self.refresh_ports_button
            
        else:
            self.port_var.set(active_port)
            self.start_button.config(state=DISABLED)
            self.stop_button.config(state=DISABLED)
            self.start_recording_button.config(state=DISABLED)
            self.stop_recording_button.config(state=DISABLED)

        time.sleep(0) 

    def setup_serial(self):
        self.ser = None

    def start_data_acquisition(self):
        self.data = np.zeros(6000)
        self.data2 = np.zeros(6000)
        self.data3 = np.zeros(6000)

        self.data_lock = threading.Lock()

    def acquire_data(self):
        while self.is_running.is_set():
            try:
                line = self.ser.readline().decode().strip()
                value1, value2, timestamp = map(float, line.split(','))

                with self.data_lock:
                    self.data = np.append(self.data, value1)
                    self.data = self.data[-6000:]

                    self.data2 = np.append(self.data2,value2)
                    self.data2 = self.data2[-6000:]

                    self.data3 = np.append(self.data3,timestamp)
                    self.data3 = self.data2[-6000:]


                    if self.is_recording:
                        self.recording_data.append((value1, value2, timestamp))

            except (serial.SerialException, ValueError, IndexError):
                # self.show_error_message("Serial port disconnected or invalid data received.")
                pass
                
                
                # self.show_error_message("Serial port disconnected or invalid data received.")
                # self.stop_animation()
                # break
                    

        # self.acquire_data = acquire_data  # This line should be inside the method

    def animate(self):
        self.lines, = self.ax.plot(self.data, label='Live Data', color='#464DB6', linewidth=1.0)
        self.lines2, = self.ax2.plot(self.data2, label='Live Data', color='#464DB6', linewidth=1.0)

        def update_plot(frame):
            with self.data_lock:
                self.lines.set_ydata(self.data)
                self.ax.relim()
                self.ax.autoscale_view(True, True, True)

                self.lines2.set_ydata(self.data2)
                self.ax2.relim()
                self.ax2.autoscale_view(True, True, True)

        animation = FuncAnimation(self.fig, update_plot, interval=self.update_interval, cache_frame_data=False)

        self.ax.set_xticks(np.arange(0, 6001, 1200))
        self.ax.set_xticklabels(['0','1', '2', '3', '4', '5'])

        self.ax2.set_xticks(np.arange(0, 6001, 1200))
        self.ax2.set_xticklabels(['0','1', '2', '3', '4', '5'])


        # Add labels to the axes
        self.ax.set_xlabel('Time (s)', color='#2B318A', fontsize=10)
        self.ax.set_ylabel('Amplitude', color='#2B318A', fontsize=10)

        self.ax2.set_xlabel('Time (s)', color='#2B318A', fontsize=10)
        self.ax2.set_ylabel('Amplitude', color='#2B318A', fontsize=10)

        self.canvas.draw()
        self.root.mainloop()

    def start_animation(self):
        # self.play_sound(get_embedded_image_data("sounds\\beep-02.mp3"))
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        with self.data_lock:
            self.data = np.zeros(6000)
            self.lines.set_ydata(self.data)
            self.ax.relim()
            self.ax.autoscale_view(True, True, True)


            self.data2 = np.zeros(6000)
            self.lines2.set_ydata(self.data2)
            self.ax2.relim()
            self.ax2.autoscale_view(True, True, True)

        selected_port = self.port_var.get()
        # selected_baud = int(self.baud_var.get())  # Get selected baud rate as an integer
        selected_baud = 115200


        if selected_port != "Select Port":
            try:
                self.ser = serial.Serial(selected_port, selected_baud, timeout=1)
                self.start_animation_thread()
              

                # Start color determination thread
                self.start_color_thread()

            except serial.SerialException as e:
                self.show_error_message(f"Error opening serial port: {e}")
                self.stop_animation()
                
    def start_animation_thread(self):
        self.is_running.set()
        self.data_thread = threading.Thread(target=self.acquire_data, daemon=True)
        self.data_thread.start()

    def start_color_thread(self):
        self.color_thread = threading.Thread(target=self.monitor_data_array, daemon=True)
        self.color_thread.start()

    def monitor_data_array(self):
        while self.is_running.is_set():
           
            def butter_lowpass_filter(data, cutoff_freq, sampling_rate, order=4):
                nyquist = 0.5 * sampling_rate
                normal_cutoff = cutoff_freq / nyquist
                b, a = butter(order, normal_cutoff, btype='low', analog=False)
                filtered_data = filtfilt(b, a, data)
                return filtered_data

            def find_peaks_between_troughs(data):
                # Find troughs using the filtered data
                troughs, _ = find_peaks(-data, distance=500, prominence=1.0)

                # Find the index of the maximum point between two troughs
                peaks = [np.argmax(data[troughs[i]:troughs[i+1]]) + troughs[i] for i in range(len(troughs)-1)]

                return np.array(peaks), troughs  # Return both peaks and troughs


            def process_pulse_wave_for_file(datahere,timestamphere,cutoff_frequency=20, slope_threshold=300):
                # Apply Butterworth low-pass filter to 'Signal-1' data
                filtered_data = butter_lowpass_filter(datahere, cutoff_frequency, 1100)

                # Find peaks and troughs using the filtered data
                peaks, troughs = find_peaks_between_troughs(filtered_data)
                # Counter for good pulses
                good_pulse_count = 0

                # Process the pulse wave for each 2-second window
                for i in range(len(troughs) - 1):
                    pulse_start, pulse_end = troughs[i], troughs[i + 1]
                    slope_at_trough = (datahere[pulse_end] - datahere[pulse_start])

                    if i < len(peaks) - 1:
                        peak_index = peaks[i]
                        next_peak_index = peaks[i + 1]
                        slope_at_peak = (datahere[next_peak_index] - datahere[peak_index])

                        vertical_difference = datahere[peaks[i]] - datahere[pulse_start]
                        horizontal_difference = timestamphere[pulse_end] - timestamphere[pulse_start]
                        rising_time = timestamphere[peaks[i]] - timestamphere[pulse_start]


                        if (
                            i < len(peaks) - 1 and
                            slope_threshold >= abs(slope_at_trough) and
                            10 <= vertical_difference <= 700 and
                            400 <= horizontal_difference <= 1500 and
                            slope_threshold >= abs(slope_at_peak) and
                            60 <= rising_time <= 400
                        ):
                            good_pulse_count += 1

                # Determine color based on the presence of good pulses
                graph_color = 'green' if good_pulse_count > 3 else 'red'

                return graph_color


            self.graphcolor = process_pulse_wave_for_file(self.data,self.data3)

            self.lines.set_color(self.graphcolor)
            self.lines2.set_color(process_pulse_wave_for_file(self.data2,self.data3))
            # Redraw canvas
            # self.canvas.draw()
            # Sleep for a short interval before checking again
            time.sleep(0.1)

    def stop_animation(self):
        # self.play_sound(get_embedded_image_data("sounds\\beep-02.mp3"))
        # self.stop_button.config(state=tk.DISABLED)
        # self.start_button.config(state=tk.NORMAL)

        # self.is_running.clear()
        # if self.data_thread and self.data_thread.is_alive():
        #     self.data_thread.join()

        # if self.ser:
        #     self.ser.close()



        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        self.is_running.clear()
        if self.data_thread and self.data_thread != threading.current_thread():
            if self.data_thread.is_alive():
                self.data_thread.join()

        if self.ser:
            self.ser.close()

    def start_recording(self):

        sound_data = get_embedded_image_data("sounds\\beep-06.mp3")
        self.play_sound(sound_data)
        self.start_recording_button.config(state=tk.DISABLED)
        self.stop_recording_button.config(state=tk.NORMAL)
        self.is_recording = True
        self.recording_data = []
        self.timer_running = True
        self.start_timer()

    def play_sound(self, sound_file):
        try:


            sound_file2 = io.BytesIO(sound_file)
            pygame.mixer.music.load(sound_file2)
            pygame.mixer.music.play()



            # pygame.mixer.music.load(sound_file)
            # pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Error playing sound: {e}")

    def stop_recording(self):
        sound_data = get_embedded_image_data("sounds\\beep-06.mp3")
        self.play_sound(sound_data)

        self.stop_recording_button.config(state=tk.DISABLED)
        self.start_recording_button.config(state=tk.NORMAL)
        self.is_recording = False
        self.timer_running = False
        self.stop_timer()
        if self.recording_data:
            self.save_data()

    def save_data(self):
      

        try:
            file_name = "graphData.apa"
            self.today_timestamp = int(datetime.now().timestamp())
            self.today_milliseconds = int(datetime.now().timestamp() * 1000)
            self.final_file_path = f"{self.patient}_{self.today_timestamp}_${self.today_milliseconds}$_{file_name}"
            
            # Create a temporary directory to extract the embedded readings directory
            temp_dir = tempfile.mkdtemp()

            # Extract the readings directory from the embedded resources
            for filename in pkg_resources.resource_listdir(__name__, 'readings'):
                file_content = pkg_resources.resource_string(__name__, os.path.join('readings', filename))
                with open(os.path.join(temp_dir, filename), 'wb') as file:
                    file.write(file_content)

            # Create the file path within the extracted readings directory
            self.file_path = os.path.join(temp_dir, self.final_file_path)

            # Write data to the file
            json_data = {"Signal-1": [], "Signal-2": [], "Signal-3": []}
            for data_point in self.recording_data:
                json_data["Signal-1"].append(data_point[0])
                json_data["Signal-2"].append(data_point[1])
                json_data["Signal-3"].append(data_point[2])

            with open(self.file_path, 'w') as file:
                json.dump(json_data, file, indent=2)

            # Optionally, clean up the temporary directory after use
            # shutil.rmtree(temp_dir)

            messagebox.showinfo("Success", "Data saved successfully.")
            self.generate_report_button.config(state=tk.NORMAL)

        except Exception as e:
            self.show_error_message(f"Error saving data: {e}")




        # try:
        #     json_data = {"Signal-1": [], "Signal-2": [], "Signal-3": []}

        #     for data_point in self.recording_data:
        #         json_data["Signal-1"].append(data_point[0])  # Add values to Signal-1 array
        #         json_data["Signal-2"].append(0)  # Add zeros to Signal-2 array
        #         json_data["Signal-3"].append(data_point[1])  # Add timestamp values to Signal-3 array

        #     with open(self.file_path, 'w') as file:
        #         json.dump(json_data, file, indent=2)

        #     messagebox.showinfo("Success", "Data saved successfully.")
        #     self.generate_report_button.config(state=tk.NORMAL)

            
        # except Exception as e:
        #     self.show_error_message(f"Error saving data: {e}")

    def update_ports_list(self):
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        menu = self.port_menu["menu"]
        menu.delete(0, "end")
        for port in available_ports:
            menu.add_command(label=port, command=lambda p=port: self.port_var.set(p))

    def show_error_message(self, message):
        messagebox.showerror("Error", message)



# ===========================================================single sensor logic here==========================================================

class SingleSensorLogic:
    def __init__(self, root,patientName,noofsensor,dob,hospitalName,gender,height,weight,d_notch_ank, d_notch_rad,uid):  
    
        self.patient = patientName
        self.noofsensor = noofsensor
        self.dob = dob
        self.hospitalName = hospitalName
        self.gender = gender
        self.weight = weight
        self.rad_value = d_notch_rad
        self.ank_value = d_notch_ank
        self.height= height
        self.uid = uid              

        self.graphcolor = "red"
        self.color_thread = None  # Initialize color determination thread
        
        # self.weight = weight
        # self.age = age
        # self.gender = gender

        print(self.patient)
        self.root = root
  
     # Create a lock for shared resources
        self.is_running = threading.Event()
        self.recording_data = []
        self.is_recording = False
        self.update_interval = int(0)  # Set default update interval

        self.start_time = None
        self.timer_running = False

        # Initialize Pygame mixer
        pygame.mixer.init()

        self.create_widgets()
        # self.start_animation()
        self.setup_serial()
        self.start_data_acquisition()
        self.animate()
        

        self.data_thread = None

    def disconnect_and_go_home(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            

        except Exception as e:
            pass
            # Handle any exceptions that may occur
            # messagebox.showerror("Error", f"An error occurred while disconnecting and going back: {str(e)}")

        # Destroy frames
        self.top_frame.destroy()
        self.footer_label.destroy()
        self.main_frame.destroy()
        
        # Call the function to go back
        Modules()

    def disconnect_and_go_helpsupport(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            

        except Exception as e:
            pass
            # Handle any exceptions that may occur
            # messagebox.showerror("Error", f"An error occurred while disconnecting and going back: {str(e)}")

        # Destroy frames
        self.top_frame.destroy()
        self.footer_label.destroy()
        self.main_frame.destroy()
        
        # Call the function to go back
        help_support(self.patient,self.noofsensor,self.dob,self.hospitalName,self.gender,self.weight,self.rad_value,self.ank_value,self.height,self.uid)

    def disconnect_and_go_back(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            

        except Exception as e:
            pass
            # Handle any exceptions that may occur
            # messagebox.showerror("Error", f"An error occurred while disconnecting and going back: {str(e)}")

        # Destroy frames
        self.top_frame.destroy()
        self.footer_label.destroy()
        self.main_frame.destroy()
        
        # Call the function to go back
        recordNewTestSelected()

    def on_frame_configure(self, event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)

        self.label_precog.config(font=("helvetica",font_size+14))
        self.home_btn.config(font=("helvetica",font_size))
        self.back_btn.config(font=("helvetica",font_size))
        self.help_btn.config(font=("helvetica",font_size))


        # label_add_patient.config(font=("helvetica",font_size+14))
        # entry_name.config(font=("helvetica",font_size))
       
    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            time_string = f"{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_string)
            self.timer_label.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def go_to_generate_report(self):
        try:
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
        except Exception as e:
            pass

        generate_report(self.file_path,self.patient, self.noofsensor,self.dob,self.hospitalName,self.gender,self.weight,self.rad_value,self.ank_value,self.height,self.uid)

    def create_widgets(self):
       

        self.top_frame = Frame(frame1,bg="white")
        self.top_frame.pack(side=LEFT,expand=1,fill=BOTH)
            
        frame1_1 = Frame(self.top_frame, bg="white")
        frame1_1.pack(expand=1, fill="both", side="left")

        frame1_2 = Frame(self.top_frame, bg="white")
        frame1_2.pack(expand=1, fill="both", side="right")
        #content 
        self.label_precog = Label(frame1_1,text="PRECOG",bg="white",fg="#464DB6")
        self.label_precog.pack(anchor=W,padx=5)

        self.home_btn = Button(frame1_2,text="Home",bg="white",border=0,highlightthickness=0,fg="#464DB6",command=lambda:(self.disconnect_and_go_home()))
        self.home_btn.pack(side=RIGHT,anchor=E,padx=5)

        self.help_btn = Button(frame1_2,text="Help & support",bg="white",border=0,highlightthickness=0,fg="#464DB6",command=lambda:( self.top_frame.destroy(),self.footer_label.destroy(),self.main_frame.destroy(),self.disconnect_and_go_helpsupport()))
        self.help_btn.pack(side=RIGHT,anchor=E,padx=5)


        self.back_btn = Button(frame1_1,image=backbtnimageblue2,border=0,highlightthickness=0,bg="white",command=lambda:(self.disconnect_and_go_back()))
        self.back_btn.pack(anchor=W,padx=5,pady=(5,0))

        self.top_frame.bind("<Configure>", self.on_frame_configure)

        self.main_frame = Frame(frame2, bg='white')
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.fig = Figure(figsize=(4, 1), facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('white')
        self.ax.grid(True, color='#DCE6FE', linestyle='--', linewidth=0.5)
        self.ax.tick_params(axis='x', colors='#2B318A')
        self.ax.tick_params(axis='y', colors='#2B318A')

        self.ax.spines['top'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')


        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        control_frame = Frame(self.main_frame, bg='white')
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=10, expand=0)

        serial_frame = Frame(control_frame, bg='white', highlightthickness=1, highlightbackground='#2B318A')
        serial_frame.pack(padx=2, pady=10, expand=0)

        recording_frame = Frame(control_frame, bg='white', highlightthickness=1, highlightbackground='#2B318A')
        recording_frame.pack(padx=2, pady=10, expand=0)

        self.serialLabel = Label(serial_frame, text="Serial Port", bg='white', fg='#464DB6', font=("helvetica", 10))
        self.serialLabel.pack(side=tk.TOP, pady=5, padx=5)

        self.port_var = StringVar()
        self.port_var.set("Select Port")

        self.port_menu = OptionMenu(serial_frame, self.port_var, *["Select Port"])
        self.port_menu.config(bg='white', fg='#464DB6', width=11, font=("helvetica", 12), highlightthickness=2, highlightbackground="grey")
        self.port_menu.pack(side=tk.TOP, pady=0, padx=5)


        running_port = self.detect_active_port()
        self.port_var.set(running_port)

        self.port_checker_thread = threading.Thread(target=self.check_for_new_ports)
        self.port_checker_thread.start()




        # self.baud_var = StringVar(self.root)
        # self.baud_var.set("9600")  # Set default baud rate
        # baud_rates = ["9600", "19200", "38400", "57600", "115200"]

        # self.baud_menu = OptionMenu(control_frame, self.baud_var, *baud_rates)
        # self.baud_menu.config(bg='#000000', fg='white', width=10, font=("Lucida Sans", 10), highlightthickness=2, highlightbackground="grey")
        # self.baud_menu.pack(side=tk.TOP, pady=5, padx=5)

        self.refresh_ports_button = Button(serial_frame, image=refreshportbtn3, highlightthickness=0,border=0, command=self.check_for_new_ports)
        self.refresh_ports_button.pack(side=tk.TOP, pady=5, padx=5)

        self.update_ports_list()

        self.start_button = Button(serial_frame, image=connectbtn3,border=0,highlightthickness=0, command=lambda:(self.start_animation(),self.start_recording_button.config(state=tk.NORMAL)))
        self.start_button.pack(side=tk.TOP)

        self.stop_button = Button(serial_frame, image=disconnectbtn3, border=0,highlightthickness=0,command=lambda:(self.stop_animation(),self.start_recording_button.config(state=tk.DISABLED)), state=tk.DISABLED)
        self.stop_button.pack(side=tk.TOP)

        self.baud_label = Label(recording_frame, text="Record Option",bg="white",fg="#464DB6", font=("helvetica", 10))
        self.baud_label.pack(side=tk.TOP,padx=10,pady=5)

        self.start_recording_button = Button(recording_frame, image=startrecordingbtn3, border=0,highlightthickness=0,state=tk.DISABLED,command=self.start_recording)
        self.start_recording_button.pack(side=tk.TOP,padx=5)

        self.stop_recording_button = Button(recording_frame, image=stoprecordingbtn3,border=0,highlightthickness=0, command=self.stop_recording, state=tk.DISABLED)
        self.stop_recording_button.pack(side=tk.TOP)

        self.generate_report_button = Button(recording_frame,image=generatereportbtn3 ,border=0,highlightthickness=0, command=lambda:(self.main_frame.destroy(),self.top_frame.destroy(),self.footer_label.destroy(),self.go_to_generate_report()), state=tk.DISABLED)
        self.generate_report_button.pack(side=tk.TOP)

        self.patientName_Label = Label(control_frame, bg="white",fg="#464DB6",text=f"Patient Name: {self.patient}",font=("Lucida Sans", 12))
        self.patientName_Label.pack(side=tk.TOP)


        self.timer_label  = Label(control_frame, text="00:00",bg="white",fg="#464DB6", font=("Lucida Sans", 12))
        self.timer_label.pack(side=tk.BOTTOM)
        self.timer_label2  = Label(control_frame, text="Timer",bg="white",fg="#464DB6", font=("helvetica", 12))
        self.timer_label2.pack(side=tk.BOTTOM)

        self.footer_label= Label(frame3,bg="white",text="Copyright © 2024 Acuradyne Systems")
        self.footer_label.pack(expand=1,fill=BOTH,pady=0)

    def detect_active_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                ser = serial.Serial(port.device, timeout=1)
                if ser.is_open:
                    ser.close()
                    return port.device
                    
            except (OSError, serial.SerialException):
                pass
        return None

    def check_for_new_ports(self):
        try:
            # Call the function to disconnect
            self.is_running.clear()
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join()

            if self.ser:
                self.ser.close()
          
            with self.data_lock:
                self.data = np.zeros(6000)
                self.lines.set_ydata(self.data)
                self.ax.relim()
                self.ax.autoscale_view(True, True, True)
            
        except Exception as e:
            pass

        self.update_ports_list()
            # self.start_button.config(state=state)
        # while True:
        # if self.main_frame.winfo_exists():
        active_port = self.detect_active_port()
        if active_port:
            self.port_var.set(active_port)
            
            self.start_button.config(state=ACTIVE)
            self.stop_button.config(state=DISABLED)
            self.start_recording_button.config(state=DISABLED)
            self.stop_recording_button.config(state=DISABLED)



            # self.start_animation()
            # self.start_recording_button.config(state=tk.NORMAL)
            # Optionally, disable self.port_menu and self.refresh_ports_button
            
        else:
            self.port_var.set(active_port)
            self.start_button.config(state=DISABLED)
            self.stop_button.config(state=DISABLED)
            self.start_recording_button.config(state=DISABLED)
            self.stop_recording_button.config(state=DISABLED)

        time.sleep(0) 

    def setup_serial(self):
        self.ser = None

    def start_data_acquisition(self):
        self.data = np.zeros(6000)
        self.data2 = np.zeros(6000)

        self.data_lock = threading.Lock()

    def acquire_data(self):
        while self.is_running.is_set():
            try:
                line = self.ser.readline().decode().strip()
                value, timestamp = map(float, line.split(','))

                with self.data_lock:
                    self.data = np.append(self.data, value)
                    self.data = self.data[-6000:]

                    self.data2 = np.append(self.data2,timestamp)
                    self.data2 = self.data2[-6000:]


                    if self.is_recording:
                        self.recording_data.append((value, timestamp))

            except (serial.SerialException, ValueError, IndexError):
                # self.show_error_message("Serial port disconnected or invalid data received.")
                pass
                
                
                # self.show_error_message("Serial port disconnected or invalid data received.")
                # self.stop_animation()
                # break
                    

        # self.acquire_data = acquire_data  # This line should be inside the method

    def animate(self):
        self.lines, = self.ax.plot(self.data, label='Live Data', color='#464DB6', linewidth=1.0)

        def update_plot(frame):
            with self.data_lock:
                self.lines.set_ydata(self.data)
                self.ax.relim()
                self.ax.autoscale_view(True, True, True)

        animation = FuncAnimation(self.fig, update_plot, interval=self.update_interval, cache_frame_data=False)

        self.ax.set_xticks(np.arange(0, 6001, 1200))
        self.ax.set_xticklabels(['0','1', '2', '3', '4', '5'])


        # Add labels to the axes
        self.ax.set_xlabel('Time (s)', color='#2B318A', fontsize=10)
        self.ax.set_ylabel('Amplitude', color='#2B318A', fontsize=10)

        self.canvas.draw()
        self.root.mainloop()

    def start_animation(self):
        # self.play_sound(get_embedded_image_data("sounds\\beep-02.mp3"))
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        with self.data_lock:
            self.data = np.zeros(6000)
            self.lines.set_ydata(self.data)
            self.ax.relim()
            self.ax.autoscale_view(True, True, True)

        selected_port = self.port_var.get()
        # selected_baud = int(self.baud_var.get())  # Get selected baud rate as an integer
        selected_baud = 115200


        if selected_port != "Select Port":
            try:
                self.ser = serial.Serial(selected_port, selected_baud, timeout=1)
                self.start_animation_thread()
              

                # Start color determination thread
                self.start_color_thread()

            except serial.SerialException as e:
                self.show_error_message(f"Error opening serial port: {e}")
                self.stop_animation()
                
    def start_animation_thread(self):
        self.is_running.set()
        self.data_thread = threading.Thread(target=self.acquire_data, daemon=True)
        self.data_thread.start()

    def start_color_thread(self):
        self.color_thread = threading.Thread(target=self.monitor_data_array, daemon=True)
        self.color_thread.start()

    def monitor_data_array(self):
        while self.is_running.is_set():
           
            def butter_lowpass_filter(data, cutoff_freq, sampling_rate, order=4):
                nyquist = 0.5 * sampling_rate
                normal_cutoff = cutoff_freq / nyquist
                b, a = butter(order, normal_cutoff, btype='low', analog=False)
                filtered_data = filtfilt(b, a, data)
                return filtered_data

            def find_peaks_between_troughs(data):
                # Find troughs using the filtered data
                troughs, _ = find_peaks(-data, distance=500, prominence=1.0)

                # Find the index of the maximum point between two troughs
                peaks = [np.argmax(data[troughs[i]:troughs[i+1]]) + troughs[i] for i in range(len(troughs)-1)]

                return np.array(peaks), troughs  # Return both peaks and troughs


            def process_pulse_wave_for_file(cutoff_frequency=20, slope_threshold=300):
                # Apply Butterworth low-pass filter to 'Signal-1' data
                filtered_data = butter_lowpass_filter(self.data, cutoff_frequency, 1100)

                # Find peaks and troughs using the filtered data
                peaks, troughs = find_peaks_between_troughs(filtered_data)
                # Counter for good pulses
                good_pulse_count = 0

                # Process the pulse wave for each 2-second window
                for i in range(len(troughs) - 1):
                    pulse_start, pulse_end = troughs[i], troughs[i + 1]
                    slope_at_trough = (self.data[pulse_end] - self.data[pulse_start])

                    if i < len(peaks) - 1:
                        peak_index = peaks[i]
                        next_peak_index = peaks[i + 1]
                        slope_at_peak = (self.data[next_peak_index] - self.data[peak_index])

                        vertical_difference = self.data[peaks[i]] - self.data[pulse_start]
                        horizontal_difference = self.data2[pulse_end] - self.data2[pulse_start]
                        rising_time = self.data2[peaks[i]] - self.data2[pulse_start]


                        if (
                            i < len(peaks) - 1 and
                            slope_threshold >= abs(slope_at_trough) and
                            10 <= vertical_difference <= 700 and
                            400 <= horizontal_difference <= 1500 and
                            slope_threshold >= abs(slope_at_peak) and
                            60 <= rising_time <= 400
                        ):
                            good_pulse_count += 1

                # Determine color based on the presence of good pulses
                graph_color = 'green' if good_pulse_count > 3 else 'red'

                return graph_color

        
            self.graphcolor = process_pulse_wave_for_file()

            self.lines.set_color(self.graphcolor)
            # Redraw canvas
            # self.canvas.draw()
            # Sleep for a short interval before checking again
            time.sleep(0.1)

    def stop_animation(self):
        # self.play_sound(get_embedded_image_data("sounds\\beep-02.mp3"))
        # self.stop_button.config(state=tk.DISABLED)
        # self.start_button.config(state=tk.NORMAL)

        # self.is_running.clear()
        # if self.data_thread and self.data_thread.is_alive():
        #     self.data_thread.join()

        # if self.ser:
        #     self.ser.close()



        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        self.is_running.clear()
        if self.data_thread and self.data_thread != threading.current_thread():
            if self.data_thread.is_alive():
                self.data_thread.join()

        if self.ser:
            self.ser.close()

    def start_recording(self):

        sound_data = get_embedded_image_data("sounds\\beep-06.mp3")
        self.play_sound(sound_data)
        self.start_recording_button.config(state=tk.DISABLED)
        self.stop_recording_button.config(state=tk.NORMAL)
        self.is_recording = True
        self.recording_data = []
        self.timer_running = True
        self.start_timer()

    def play_sound(self, sound_file):
        try:


            sound_file2 = io.BytesIO(sound_file)
            pygame.mixer.music.load(sound_file2)
            pygame.mixer.music.play()



            # pygame.mixer.music.load(sound_file)
            # pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Error playing sound: {e}")

    def stop_recording(self):
        sound_data = get_embedded_image_data("sounds\\beep-06.mp3")
        self.play_sound(sound_data)

        self.stop_recording_button.config(state=tk.DISABLED)
        self.start_recording_button.config(state=tk.NORMAL)
        self.is_recording = False
        self.timer_running = False
        self.stop_timer()
        if self.recording_data:
            self.save_data()

    def save_data(self):
      

        try:
            file_name = "graphData.apa"
            self.today_timestamp = int(datetime.now().timestamp())
            self.today_milliseconds = int(datetime.now().timestamp() * 1000)
            self.final_file_path = f"{self.patient}_{self.today_timestamp}_${self.today_milliseconds}$_{file_name}"
            
            # Create a temporary directory to extract the embedded readings directory
            temp_dir = tempfile.mkdtemp()

            # Extract the readings directory from the embedded resources
            for filename in pkg_resources.resource_listdir(__name__, 'readings'):
                file_content = pkg_resources.resource_string(__name__, os.path.join('readings', filename))
                with open(os.path.join(temp_dir, filename), 'wb') as file:
                    file.write(file_content)

            # Create the file path within the extracted readings directory
            self.file_path = os.path.join(temp_dir, self.final_file_path)

            # Write data to the file
            json_data = {"Signal-1": [], "Signal-2": [], "Signal-3": []}
            for data_point in self.recording_data:
                json_data["Signal-1"].append(data_point[0])
                json_data["Signal-2"].append(0)
                json_data["Signal-3"].append(data_point[1])

            with open(self.file_path, 'w') as file:
                json.dump(json_data, file, indent=2)

            # Optionally, clean up the temporary directory after use
            # shutil.rmtree(temp_dir)

            messagebox.showinfo("Success", "Data saved successfully.")
            self.generate_report_button.config(state=tk.NORMAL)

        except Exception as e:
            self.show_error_message(f"Error saving data: {e}")




        try:
            json_data = {"Signal-1": [], "Signal-2": [], "Signal-3": []}

            for data_point in self.recording_data:
                json_data["Signal-1"].append(data_point[0])  # Add values to Signal-1 array
                json_data["Signal-2"].append(0)  # Add zeros to Signal-2 array
                json_data["Signal-3"].append(data_point[1])  # Add timestamp values to Signal-3 array

            with open(self.file_path, 'w') as file:
                json.dump(json_data, file, indent=2)

            messagebox.showinfo("Success", "Data saved successfully.")
            self.generate_report_button.config(state=tk.NORMAL)

            
        except Exception as e:
            self.show_error_message(f"Error saving data: {e}")

    def update_ports_list(self):
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        menu = self.port_menu["menu"]
        menu.delete(0, "end")
        for port in available_ports:
            menu.add_command(label=port, command=lambda p=port: self.port_var.set(p))

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

# ==========================================================  class ends here ==========================================================================

# =====================================================================# basic functions for validations  ========================================================================

# basic functions for validations
def show_error_message(message):
    messagebox.showerror("Error", message)


def validate_name(name):
    # Allow letters and spaces in the name
    return bool(re.match("^[a-zA-Z\s]+$", name))


def validate_phone(phone):
    # Use regular expression to match 10 digit numbers
    pattern = r'^\d{10}$'
    return bool(re.match(pattern, phone))

def validate_email(email):
    # Use a simple regex for basic email validation
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

def validate_city(city):
    # Allow only letters in the city
    return bool(re.match("^[a-zA-Z\s]+$", city))

def is_valid_number(no):
    try:
        int(no)
        return True
    except ValueError:
        return False

# this function is to calculate age from dob

def calculate_age(dob):
    try:
        # Parse the date of birth
        dob_date = datetime.strptime(dob, '%d/%m/%Y')
    except ValueError:
        # Handle invalid date format
        return "Invalid Date"

    # Get the current date
    current_date = datetime.now()

    # Check if the birthday for the current year has passed
    if (current_date.month, current_date.day) < (dob_date.month, dob_date.day):
        age = current_date.year - dob_date.year - 1
    else:
        age = current_date.year - dob_date.year

    return age

# it will convert any data in epoch format
def date_to_epoch(date_str, date_format='%Y/%m/%d'):
    date_object = datetime.strptime(date_str, date_format)
    epoch_time = int(date_object.timestamp())
    return epoch_time

def calculate_font_size1(screen_width):
    # Calculate font size based on screen width 
    font_size = int(screen_width / 24)
    return font_size

def date_to_epoch(date_str, date_format='%Y/%m/%d'):
    date_object = datetime.strptime(date_str, date_format)
    epoch_time = int(date_object.timestamp())
    return epoch_time

# ======================================================================   help and support ======================================================================
def help_support(patientName,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid):

    frame1_1 = Frame(frame1, bg="white")
    frame1_1.pack( side="left",pady=5)

    frame1_2 = Frame(frame1, bg="white")
    frame1_2.pack( side="right",pady=5)

    frame2_1 = Frame(frame2, bg="white")
    frame2_1.pack(expand=1, fill=X)

    frame2_2 = Frame(frame2, bg="white")
    frame2_2.pack(expand=1, fill=BOTH)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=0,pady=5,fill=X)


    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)

        label_precog.config(font=("helvetica",font_size+14))
        # label_heading.config(font=("helvetica",font_size+16))
        home_btn.config(font=("helvetica",font_size))
        # label_parameters.config(font=("helvetica",font_size+8),fg="#464DB6")
        # label_unit.config(font=("helvetica",font_size+8),fg="#464DB6")
        # label_normal_value.config(font=("helvetica",font_size+8),fg="#464DB6")
        # label_observed_value.config(font=("helvetica",font_size+8),fg="#464DB6")


    label_precog = Label(frame1_1,text="PRECOG",bg="white",fg="#464DB6")
    label_precog.pack(side="left",padx=10)

    home_btn = Button(frame1_2,text="Home",bg="white",fg="#464DB6",border=0,highlightthickness=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    home_btn.pack(side=RIGHT,padx=10)

    #three vertical frames in middle
    framev1 = Frame(frame2_2,bg="white")
    framev1.pack(side=LEFT,expand=1,fill=BOTH)

    framev2 = Frame(frame2_2,bg="white")
    framev2.pack(side=LEFT,expand=1,fill=BOTH)

    framev3 = Frame(frame2_2,bg="white")
    framev3.pack(side=LEFT,expand=1,fill=BOTH)

    #three frames in every single vertical frames

    # in v1
    framev1_h1 = Frame(framev1,bg="white")
    framev1_h1.pack(expand=1,fill=BOTH)

    framev1_h2 = Frame(framev1,bg="white")
    framev1_h2.pack(expand=1,fill=BOTH)

    framev1_h3 = Frame(framev1,bg="white")
    framev1_h3.pack(expand=1,fill=BOTH)


    # in v2
    framev2_h1 = Frame(framev2,bg="white")
    framev2_h1.pack(expand=1,fill=BOTH)

    framev2_h2 = Frame(framev2,bg="white")
    framev2_h2.pack(expand=1,fill=BOTH)

    framev2_h3 = Frame(framev2,bg="white")
    framev2_h3.pack(expand=1,fill=BOTH)


    # in v3
    framev3_h1 = Frame(framev3,bg="white")
    framev3_h1.pack(expand=1,fill=BOTH)

    framev3_h2 = Frame(framev3,bg="white")
    framev3_h2.pack(expand=1,fill=BOTH)

    framev3_h3 = Frame(framev3,bg="white")
    framev3_h3.pack(expand=1,fill=BOTH)


#content here 
    def go_back_to_recording():
        singleSensorApp = SingleSensorLogic(root,patientName,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid) 
    
    back_btn = Button(frame2_1,image=backbtnimageblue2,border=0,highlightthickness=0,bg="white",command= lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),go_back_to_recording()))
    back_btn.pack(side=LEFT,expand=0)

    label_guide = Label(frame2_1,bg="white",text="Step by step guide",fg="#464DB6")
    label_guide.pack(side=LEFT)


    # content in v1
    label_img1 = Label(framev1_h1,image=support1final2,bg="white")
    label_img1.pack(expand=1,fill=BOTH)

    label_heading = Label(framev1_h2,text="Step 1",bg="white",fg="#464DB6")
    label_heading.pack(expand=1,fill=BOTH)

    label_des = Label(framev1_h3,text="Connect the device to your desktop via serial port",bg="white",fg="#464DB6")
    label_des.pack(expand=1,fill=BOTH)



    # content in v2
    label_img2 = Label(framev2_h1,image=support2final2,bg="white")
    label_img2.pack(expand=1,fill=BOTH)

    label_heading2 = Label(framev2_h2,text="Step 2",bg="white",fg="#464DB6")
    label_heading2.pack(expand=1,fill=BOTH)

    label_des2 = Label(framev2_h3,text="Adjust the strap on patient's wrist as per required",bg="white",fg="#464DB6")
    label_des2.pack(expand=1,fill=BOTH)


    # content in v2
    label_img3 = Label(framev3_h1,image=support3final2,bg="white")
    label_img3.pack(expand=1,fill=BOTH)

    label_heading3 = Label(framev3_h2,text="Step 3",bg="white",fg="#464DB6")
    label_heading3.pack(expand=1,fill=BOTH)

    label_des3 = Label(framev3_h3,text="Select proper port and click on connect button to begin process",bg="white",fg="#464DB6")
    label_des3.pack(expand=1,fill=BOTH)


    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

    frame1_1.bind("<Configure>", on_frame_configure)
    frame1_2.bind("<Configure>", on_frame_configure)
    frame2_1.bind("<Configure>", on_frame_configure)
    frame2_2.bind("<Configure>", on_frame_configure)
    frame3_1.bind("<Configure>", on_frame_configure)

# ====================================================================   show parameters in history of patient ====================================================

def show_parameters_history(parameters):  
    def save_image_from_base64(image_data, filename):
        try:
            with open(filename, "wb") as f:
                f.write(base64.b64decode(image_data))
            return True
        except Exception as e:
            print("Error saving image:", e)
            return False

    def download_parameters_pdf_history( json_data):
        if json_data:
            # Ask the user for the file path and name
            # file_path = filedialog.asksaveasfilename(defaultextension=".apa", filetypes=[("PDF files", "*.pdf")])
            # file_path = 
            # Get the user's downloads folder path
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            file_name = "Precog_Report.apa"
            today_timestamp = datetime.now().date()
            today_milliseconds = int(datetime.now().timestamp() * 1000)
            final_file_path = f"{patientName_}_{today_timestamp}_{today_milliseconds}_{file_name}"
            # # Construct the new file path by appending the desired file name to the downloads folder path
            file_path = os.path.join(downloads_folder, final_file_path)

            if not file_path:
                # User canceled the save operation
                return


            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Load logo image
            try:
                # Save the binary image data to temporary files
                desktop_icon_data = get_embedded_image_data("images\\desktopicon.png")
                desktop_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                desktop_icon_temp_file.write(desktop_icon_data)
                desktop_icon_temp_file.close()

                precog_icon_data = get_embedded_image_data("images\\Precog.png")
                precog_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                precog_icon_temp_file.write(precog_icon_data)
                precog_icon_temp_file.close()

                # Now use the paths to the temporary files in the pdf.image() function
                pdf.image(desktop_icon_temp_file.name, x=86, y=10, w=12)
                pdf.image(precog_icon_temp_file.name, x=100, y=12, w=30)

                # Don't forget to clean up the temporary files after using them
                os.unlink(desktop_icon_temp_file.name)
                os.unlink(precog_icon_temp_file.name)
            except Exception as e:
                print("Error loading image:", e)

            # Define colors
            header_color = (89, 124, 146)  # #597C92

            # Move cursor to a new line after the logo
            pdf.ln(30)

            # Add Test Details heading with font color #597C92
            pdf.set_font("Times", size=15, style='B')
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test Details", ln=True, align='L', fill=False)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Add Test Details with background color #E5F7DF
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_font("Arial", size=12)
            # Get the current date and time
            current_date = datetime.now().date()
            current_time = datetime.now().time()

            # Format current date as "date/month/year"
            formatted_date = current_date.strftime("%d/%m/%Y")

            # Format current time in 12-hour format like "2:30 pm"
            formatted_time = current_time.strftime("%I:%M %p")



            test_details = [
                f"Name : {patientName_}",
                f"Date : {formatted_date}",
                f"Age/Gender : {calculate_age(dob_)} years /{gender_} ",
                f"Time : {formatted_time}",
                f"Weight/Height : {weight_} kg /{height_} cm",
                f"Referred by :",
                f"Hospital name : {hospitalName_}",
                ""
            ]
            cell_width = pdf.w / 2
            for i in range(len(test_details)):
                linebreak=False
                if i%2!=0:
                    linebreak=True
                if i==len(test_details)-1:
                    linebreak=True
                pdf.cell(cell_width, 10, txt=test_details[i], ln=linebreak, fill=True)

            pdf.cell(0, 10, txt="", ln=True)

            # Add CARDIO VASCULAR RISK ANALYSIS text
            pdf.set_font("Times", size=15, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="CARDIO VASCULAR RISK ANALYSIS", ln=True, align='C')
            
            # Add Test report and observations text
            pdf.set_font("Arial", size=14, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test report and observations", ln=True, align='C')
            # pdf.ln(10)  # Add a line break

            # Adding table headers with colors
            pdf.set_fill_color(*header_color)
            pdf.set_text_color(255, 255, 255)  # White font color for headers
            pdf.cell(65, 10, txt="Parameter", ln=0, align='C', fill=True)
            pdf.cell(65, 10, txt="Values", ln=0, align='C', fill=True)
            pdf.cell(65, 10, txt="Unit", ln=1, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Adding table data with colors
            parameters = [
                ["Pulse Rate", str(json_data.get("pulse_rate", {}).get("mean", "-")), "bpm"],
                ["Pulse Rate Variance", str(json_data.get("pulse_rate", {}).get("var", "-")), "-"],
                ["Stiffness Index", str(json_data.get("si_mean", "-")), "-"],
                ["Augmentation Index", str(json_data.get("ai_mean", "-")), "%"],
                ["Pulse Wave Velocity", str(json_data.get("pulse_wave", {}).get("velocity", "-")), "m/s"],
                ["Ejection Duration", str(json_data.get("eject_duration", "-")), "ms"],
                ["Relative Crest Time Ratio", str(json_data.get("rel_crest_time", "-")), "s"],
                ["Average Pulse Height", str(json_data.get("pulse", {}).get("height", "-")), "mV"],
                ["Average Pulse Width Duration", str(json_data.get("pulse", {}).get("width", "-")), "ms"],
                ["Dichrotic Wave Time", str(json_data.get("dicr_wave_time", "-")), "ms"],
                ["Average Dicrotic Wave Height", str(json_data.get("pulse_wave", {}).get("transit_time", "-")), "mV"],
                ["Delay Time", str(json_data.get("delay_time", "-")), "ms"]
            ]

            for i, parameter in enumerate(parameters):
                for j, val in enumerate(parameter):
                    if j == 0:  # First column background color
                        pdf.set_fill_color(207, 236, 237)  # #CFECED
                        pdf.set_font("Arial", size=12)  # Set font size to 12 for content
                        pdf.cell(65, 10, txt=val, ln=0, align='L', fill=True)
                    elif j in (1, 2):  # Second and third column background color
                        pdf.set_fill_color(229, 247, 223)  # #E5F7DF
                        pdf.set_font("Arial", size=12)  # Set font size to 12 for content
                        pdf.cell(65, 10, txt=val, ln=0, align='C', fill=True)
                    else:
                        pdf.set_font("Arial", size=14)  # Reset font size to 14 for headers
                        pdf.cell(65, 10, txt=val, ln=0, align='C', fill=True)
                pdf.cell(0, 10, txt="", ln=True)  # Adding a new line after each row


            # Add a new page
            pdf.add_page()

      

   # Load logo image
            try:
                # Save the binary image data to temporary files
                desktop_icon_data = get_embedded_image_data("images\\desktopicon.png")
                desktop_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                desktop_icon_temp_file.write(desktop_icon_data)
                desktop_icon_temp_file.close()

                precog_icon_data = get_embedded_image_data("images\\Precog.png")
                precog_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                precog_icon_temp_file.write(precog_icon_data)
                precog_icon_temp_file.close()

                # Now use the paths to the temporary files in the pdf.image() function
                pdf.image(desktop_icon_temp_file.name, x=86, y=10, w=12)
                pdf.image(precog_icon_temp_file.name, x=100, y=12, w=30)

                # Don't forget to clean up the temporary files after using them
                os.unlink(desktop_icon_temp_file.name)
                os.unlink(precog_icon_temp_file.name)
            except Exception as e:
                print("Error loading image:", e)




            # Define colors
            header_color = (89, 124, 146)  # #597C92

            # Move cursor to a new line after the logo
            pdf.ln(30)

            # Add Test Details heading with font color #597C92
            pdf.set_font("Times", size=15, style='B')
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test Details", ln=True, align='L', fill=False)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Add Test Details with background color #E5F7DF
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_font("Arial", size=12)
            test_details = [
                f"Name : {patientName_}",
                f"Date : {formatted_date}",
                f"Age/Gender : {calculate_age(dob_)} years /{gender_} ",
                f"Time : {formatted_time}",
                f"Weight/Height : {weight_} kg /{height_} cm",
                f"Referred by :",
                f"Hospital name : {hospitalName_}",
                ""
            ]

            cell_width = pdf.w / 2
            for i in range(len(test_details)):
                linebreak=False
                if i%2!=0:
                    linebreak=True
                if i==len(test_details)-1:
                    linebreak=True
                pdf.cell(cell_width, 10, txt=test_details[i], ln=linebreak, fill=True)

            pdf.cell(0, 10, txt="", ln=True)

            # Add CARDIO VASCULAR RISK ANALYSIS text
            pdf.set_font("Times", size=15, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="CARDIO VASCULAR RISK ANALYSIS", ln=True, align='C')
            
            # Add Test report and observations text
            pdf.set_font("Arial", size=14, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test report and observations", ln=True, align='C')
            # pdf.ln(10)  # Add a line break
            
            pdf.ln()
            # Add Radial Arterial Pulse Waveform heading with font color #597C92
            pdf.set_font("Times", size=14, style='B')
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Radial Arterial Pulse Waveform", ln=True, align='L', fill=False)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black
            # Add images to the second page
            try:
                # pdf.image("logo.png", x=86, y=10, w=12)
                # pdf.image("Precog.png", x=100, y=12, w=30)
                pdf.ln(30)
                pdf.set_font("Arial", size=12)
                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.set_text_color(89, 124, 146)  # Font color: #597C92
                # pdf.cell(0, 10, txt="Graphs", ln=True, align='L', fill=False)
                pdf.set_text_color(0, 0, 0)  # Reset font color to black

                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.cell(0, 10, txt="", ln=True)

                # Decode and save the first image
                save_image_from_base64(json_data["plots"]["radial_signal"], "graph1.png")
                pdf.image("graph1.png", x=10, y=150, w=200)
                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.cell(0, 10, txt="", ln=True)

                pdf.ln()
                # AddRadial Pressure Waveform heading with font color #597C92
                pdf.set_font("Times", size=14, style='B')
                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.set_text_color(89, 124, 146)  # Font color: #597C92
                pdf.cell(0, 10, txt="Radial Pressure Waveform", ln=True, align='L', fill=False)
                pdf.set_text_color(0, 0, 0)  # Reset font color to black

                # Decode and save the second image
                save_image_from_base64(json_data["plots"]["overlap_radial_signal"], "graph3.png")
                pdf.image("graph3.png", x=10, y=pdf.get_y() , w=100)



                pdf.output(file_path)
                print(f"PDF report generated successfully: {file_path}")
                label_download_status.config(text="Done! Check downloads folder")
            except Exception as e:
                print("Error adding images to the second page:", e)




            
            # messagebox.showinfo("Downloaded successfull",f"Please check your downloads folders: {file_path}")
        else:
            print("No JSON data received")

# ==============

    # Main frames
    frame1_1 = Frame(frame1, bg="white")
    frame1_1.pack( side="left",pady=5)

    frame1_2 = Frame(frame1, bg="white")
    frame1_2.pack( side="right",pady=5)

    frame2_1 = Frame(frame2, bg="white")
    frame2_1.pack(expand=1, fill=BOTH)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=0,pady=5,fill=X)


    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)

        label_precog.config(font=("helvetica",font_size+14))
        label_heading.config(font=("helvetica",font_size+16))
        home_btn.config(font=("helvetica",font_size))
        label_parameters.config(font=("helvetica",font_size+8),fg="#464DB6")
        label_unit.config(font=("helvetica",font_size+8),fg="#464DB6")
        label_normal_value.config(font=("helvetica",font_size+8),fg="#464DB6")
        label_observed_value.config(font=("helvetica",font_size+8),fg="#464DB6")

        # label_parameter.config(font=("helvetica",font_size+12),padx=(160))
        # label_value.config(font=("helvetica",font_size+12),padx=(160))
        # label_pulserate.config(font=("helvetica",font_size),padx=(160))
        # value_pulserate.config(font=("helvetica",font_size),padx=(160))
        # label_pulseratevariance.config(font=("helvetica",font_size),padx=(160))
        # value_pulseratevar.config(font=("helvetica",font_size),padx=(160))
        # label_pulseratevarper.config(font=("helvetica",font_size),padx=(160))
        # value_pulseratevarper.config(font=("helvetica",font_size),padx=(160))
        # label_pulsewavevel.config(font=("helvetica",font_size),padx=(160))
        # value_pulsewavevel.config(font=("helvetica",font_size),padx=(160))
        # label_ejectiondur.config(font=("helvetica",font_size),padx=(160))
        # value_ejectiondur.config(font=("helvetica",font_size),padx=(160))
        # label_relcresttime.config(font=("helvetica",font_size),padx=(160))
        # value_relcresttime.config(font=("helvetica",font_size),padx=(160))
        # label_avgpulseheight.config(font=("helvetica",font_size),padx=(160))
        # value_avgpulseheight.config(font=("helvetica",font_size),padx=(160))
        # label_avgpulsewidth.config(font=("helvetica",font_size),padx=(160))
        # value_avgpulsewidth.config(font=("helvetica",font_size),padx=(160))
        # label_dicroticwavetime.config(font=("helvetica",font_size),padx=(160))
        # value_dicroticwavetime.config(font=("helvetica",font_size),padx=(160))
        # label_dicroticwaveheight.config(font=("helvetica",font_size),padx=(160))
        # value_dicroticwaveheight.config(font=("helvetica",font_size),padx=(160))
        # label_footer.config(font=("helvetica",font_size))

        # screen_width = top_level.winfo_width()
        # font_size = int(screen_width / 80)
        # top_level.config(font=("helvetica",font_size))
    
    frame_main = Frame(frame2_1,bg="white")
    frame_main.pack(expand=1,fill="both",padx=10)

    # frame1_inner = Frame(frame_main,bg="white")
    # frame1_inner.pack(expand=1,fill="both",side="top")

    frame2_inner = Frame(frame_main,bg="white")
    frame2_inner.pack(expand=0,fill="both") 


    # preview table frame structure starts here 
   
    frame_v = Frame(frame_main,bg="white")
    frame_v.pack(expand=1,fill=BOTH)

    # first 4 vertical frames for preview table

    frame_v_1 = Frame(frame_v,bg="white")
    frame_v_1.pack(side=LEFT,expand=1,fill=BOTH,anchor=W)

    frame_v_2 = Frame(frame_v,bg="white")
    frame_v_2.pack(side=LEFT,expand=1,fill=Y)

    frame_v_3 = Frame(frame_v,bg="white")
    frame_v_3.pack(side=LEFT,expand=1,fill=BOTH)

    frame_v_4 = Frame(frame_v,bg="white")
    frame_v_4.pack(side=LEFT,expand=1,fill=BOTH)


    # #content 
    label_precog = Label(frame1_1,text="PRECOG",bg="white",fg="#464DB6")
    label_precog.pack(side="left",padx=10)

    home_btn = Button(frame1_2,text="Home",bg="white",fg="#464DB6",border=0,highlightthickness=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame3_1.destroy(),Modules()))
    home_btn.pack(side=RIGHT,padx=10)

    def goBack():
      
        frame1_1.destroy()
        frame1_2.destroy()
        frame2_1.destroy()
        frame3_1.destroy()
        patientsSelected()
        

    back_btn = Button(frame2_inner,image=backbtnimageblue2,border=0,highlightthickness=0,bg="white",command=lambda:(goBack()))
    back_btn.pack(side=LEFT)

    label_heading = Label(frame2_inner,text="Preview: Cardio Vascular Risk Analysis",fg="#464DB6",bg="white")
    label_heading.pack(side=LEFT)

    label_download_status = Label(frame2_inner,bg="white",fg="#464DB6")
    label_download_status.pack(side=RIGHT)

    download_button = Button(frame2_inner,image=downloadbutton2,border=0,highlightthickness=0,command=lambda:(download_parameters_pdf_history(parameters)))
    download_button.pack(side="right")


# content inside preview table 
    # content in v1
    label_parameters = Label(frame_v_1,bg="white",text="Parameter")
    label_parameters.pack(expand=1,fill=BOTH)

    label_pulserate = Label(frame_v_1,bg="white",text="Pulse Rate")
    label_pulserate.pack(expand=1,fill=BOTH)

    label_pulseratevar = Label(frame_v_1,bg="white",text="Pulse Rate Variance")
    label_pulseratevar.pack(expand=1,fill=BOTH)

    label_pulseratevarper = Label(frame_v_1,bg="white",text="% Pulse Rate Variance")
    label_pulseratevarper.pack(expand=1,fill=BOTH)

    label_si = Label(frame_v_1,bg="white",text="Stiffness Index")
    label_si.pack(expand=1,fill=BOTH)

    label_ai = Label(frame_v_1,bg="white",text="Augmentation Index")
    label_ai.pack(expand=1,fill=BOTH)

    label_pulsewavevel = Label(frame_v_1,bg="white",text="Pulse Wave Velocity")
    label_pulsewavevel.pack(expand=1,fill=BOTH)

    label_ejecdur = Label(frame_v_1,bg="white",text="Ejection Duration")
    label_ejecdur.pack(expand=1,fill=BOTH)

    label_relcresttime = Label(frame_v_1,bg="white",text="Relative Crest Time Ratio")
    label_relcresttime.pack(expand=1,fill=BOTH)

    label_avg_pulse_height = Label(frame_v_1,bg="white",text="Average Pulse Height")
    label_avg_pulse_height.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur = Label(frame_v_1,bg="white",text="Average Pulse Width Duration")
    label_avg_pulse_width_dur.pack(expand=1,fill=BOTH)

    label_dic_wave_time = Label(frame_v_1,bg="white",text="Dichrotic Wave Time")
    label_dic_wave_time.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height = Label(frame_v_1,bg="white",text="Average Dicrotic Wave Height")
    label_avg_dic_wave_height.pack(expand=1,fill=BOTH)

    label_delay_time = Label(frame_v_1,bg="white",text="Delay Time")
    label_delay_time.pack(expand=1,fill=BOTH)





    # content in v2 
    label_unit = Label(frame_v_2,bg="white",text="Unit")
    label_unit.pack(expand=1,fill=BOTH)

    label_pulserate_unit = Label(frame_v_2,bg="white",text="bpm")
    label_pulserate_unit.pack(expand=1,fill=BOTH)

    label_pulseratevar_unit = Label(frame_v_2,bg="white",text="-")
    label_pulseratevar_unit.pack(expand=1,fill=BOTH)

    label_pulseratevarper_unit = Label(frame_v_2,bg="white",text="%")
    label_pulseratevarper_unit.pack(expand=1,fill=BOTH)

    label_si_unit = Label(frame_v_2,bg="white",text="-")
    label_si_unit.pack(expand=1,fill=BOTH)

    label_ai_unit = Label(frame_v_2,bg="white",text="%")
    label_ai_unit.pack(expand=1,fill=BOTH)

    label_pulsewavevel_unit = Label(frame_v_2,bg="white",text="m/s")
    label_pulsewavevel_unit.pack(expand=1,fill=BOTH)

    label_ejecdur_unit = Label(frame_v_2,bg="white",text="ms")
    label_ejecdur_unit.pack(expand=1,fill=BOTH)

    label_relcresttime_unit = Label(frame_v_2,bg="white",text="s")
    label_relcresttime_unit.pack(expand=1,fill=BOTH)

    label_avg_pulse_height_unit = Label(frame_v_2,bg="white",text="mV")
    label_avg_pulse_height_unit.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur_unit = Label(frame_v_2,bg="white",text="ms")
    label_avg_pulse_width_dur_unit.pack(expand=1,fill=BOTH)

    label_dic_wave_time_unit = Label(frame_v_2,bg="white",text="ms")
    label_dic_wave_time_unit.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height_unit = Label(frame_v_2,bg="white",text="mV")
    label_avg_dic_wave_height_unit.pack(expand=1,fill=BOTH)

    label_delay_time_unit = Label(frame_v_2,bg="white",text="ms")
    label_delay_time_unit.pack(expand=1,fill=BOTH)



    # content in v3
    label_normal_value = Label(frame_v_3,bg="white",text="Normal value")  
    label_normal_value.pack(expand=1,fill=BOTH)

    label_pulserate_nv = Label(frame_v_3,bg="white",text="")
    label_pulserate_nv.pack(expand=1,fill=BOTH)

    label_pulseratevar_nv = Label(frame_v_3,bg="white",text=f"")
    label_pulseratevar_nv.pack(expand=1,fill=BOTH)

    label_pulseratevarper_nv = Label(frame_v_3,bg="white",text=f"")
    label_pulseratevarper_nv.pack(expand=1,fill=BOTH)

    label_si_nv = Label(frame_v_3,bg="white",text=f"")
    label_si_nv.pack(expand=1,fill=BOTH)

    label_ai_nv = Label(frame_v_3,bg="white",text=f"")
    label_ai_nv.pack(expand=1,fill=BOTH)

    label_pulsewavevel_nv = Label(frame_v_3,bg="white",text=f"")
    label_pulsewavevel_nv.pack(expand=1,fill=BOTH)

    label_ejecdur_nv = Label(frame_v_3,bg="white",text=f"")
    label_ejecdur_nv.pack(expand=1,fill=BOTH)

    label_relcresttime_nv = Label(frame_v_3,bg="white",text=f"")
    label_relcresttime_nv.pack(expand=1,fill=BOTH)

    label_avg_pulse_height_nv = Label(frame_v_3,bg="white",text=f"")
    label_avg_pulse_height_nv.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur_nv = Label(frame_v_3,bg="white",text=f"")
    label_avg_pulse_width_dur_nv.pack(expand=1,fill=BOTH)

    label_dic_wave_time_nv = Label(frame_v_3,bg="white",text=f"")
    label_dic_wave_time_nv.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height_nv = Label(frame_v_3,bg="white",text=f"")
    label_avg_dic_wave_height_nv.pack(expand=1,fill=BOTH)

    label_delay_time_nv = Label(frame_v_3,bg="white",text=f"")
    label_delay_time_nv.pack(expand=1,fill=BOTH)





    # content in v4
    label_observed_value = Label(frame_v_4,bg="white",text="Observed value")  
    label_observed_value.pack(expand=1,fill=BOTH)

    label_pulserate_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_rate']['mean']}")
    label_pulserate_ov.pack(expand=1,fill=BOTH)

    label_pulseratevar_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_rate']['var']}")
    label_pulseratevar_ov.pack(expand=1,fill=BOTH)

    label_pulseratevarper_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_rate']['var_percent']}")
    label_pulseratevarper_ov.pack(expand=1,fill=BOTH)

    label_si_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('si_mean')}")
    label_si_ov.pack(expand=1,fill=BOTH)

    label_ai_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('ai_mean')}")
    label_ai_ov.pack(expand=1,fill=BOTH)

    label_pulsewavevel_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_wave']['velocity']}")
    label_pulsewavevel_ov.pack(expand=1,fill=BOTH)

    label_ejecdur_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('eject_duration')}")
    label_ejecdur_ov.pack(expand=1,fill=BOTH)

    label_relcresttime_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('rel_crest_time')}")
    label_relcresttime_ov.pack(expand=1,fill=BOTH)

    label_avg_pulse_height_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse']['height']}")
    label_avg_pulse_height_ov.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse']['width']}")
    label_avg_pulse_width_dur_ov.pack(expand=1,fill=BOTH)

    label_dic_wave_time_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('dicr_wave_time')}")
    label_dic_wave_time_ov.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('dicr_height_mean')}")
    label_avg_dic_wave_height_ov.pack(expand=1,fill=BOTH)

    label_delay_time_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('delay_time')}")
    label_delay_time_ov.pack(expand=1,fill=BOTH)


    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack()

    frame_main.bind("<Configure>", on_frame_configure)

# ====================================================================   show parameters ============================================================================

def show_parameters(parameters, patientName,filepath ,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid):
    def save_image_from_base64(image_data, filename):
        try:
            with open(filename, "wb") as f:
                f.write(base64.b64decode(image_data))
            return True
        except Exception as e:
            print("Error saving image:", e)
            return False

    def download_parameters_pdf( json_data,patientName,filepath ,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid):
        if json_data:
            # Ask the user for the file path and name
            # file_path = filedialog.asksaveasfilename(defaultextension=".apa", filetypes=[("PDF files", "*.pdf")])
            # file_path = 
            # Get the user's downloads folder path
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            file_name = "Precog_Report.apa"
            today_timestamp = datetime.now().date()
            today_milliseconds = int(datetime.now().timestamp() * 1000)
            final_file_path = f"{patientName}_{today_timestamp}_{today_milliseconds}_{file_name}"
            # Construct the new file path by appending the desired file name to the downloads folder path
            file_path = os.path.join(downloads_folder, final_file_path)

            if not file_path:
                # User canceled the save operation
                return


            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Load logo image
            try:
                # Save the binary image data to temporary files
                desktop_icon_data = get_embedded_image_data("images\\desktopicon.png")
                desktop_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                desktop_icon_temp_file.write(desktop_icon_data)
                desktop_icon_temp_file.close()

                precog_icon_data = get_embedded_image_data("images\\Precog.png")
                precog_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                precog_icon_temp_file.write(precog_icon_data)
                precog_icon_temp_file.close()

                # Now use the paths to the temporary files in the pdf.image() function
                pdf.image(desktop_icon_temp_file.name, x=86, y=10, w=12)
                pdf.image(precog_icon_temp_file.name, x=100, y=12, w=30)

                # Don't forget to clean up the temporary files after using them
                os.unlink(desktop_icon_temp_file.name)
                os.unlink(precog_icon_temp_file.name)
            except Exception as e:
                print("Error loading image:", e)

            # Define colors
            header_color = (89, 124, 146)  # #597C92

            # Move cursor to a new line after the logo
            pdf.ln(30)

            # Add Test Details heading with font color #597C92
            pdf.set_font("Times", size=15, style='B')
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test Details", ln=True, align='L', fill=False)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Add Test Details with background color #E5F7DF
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_font("Arial", size=12)
            # Get the current date and time
            # Get the current date and time
            current_date = datetime.now().date()
            current_time = datetime.now().time()

            # Format current date as "date/month/year"
            formatted_date = current_date.strftime("%d/%m/%Y")

            # Format current time in 12-hour format like "2:30 pm"
            formatted_time = current_time.strftime("%I:%M %p")


            test_details = [
                f"Name : {patientName}",
                f"Date : {formatted_date}",
                f"Age/Gender : {calculate_age(dob)} years /{gender}",
                f"Time : {formatted_time}",
                f"Weight/Height : {weight} kg /{height} cm",
                f"Referred by :",
                f"Hospital name : {hospitalName}",
                ""

            ]
            cell_width = pdf.w / 2
            for i in range(len(test_details)):
                linebreak=False
                if i%2!=0:
                    linebreak=True
                if i==len(test_details)-1:
                    linebreak=True
                pdf.cell(cell_width, 10, txt=test_details[i], ln=linebreak, fill=True)

            pdf.cell(0, 10, txt="", ln=True)

            # Add CARDIO VASCULAR RISK ANALYSIS text
            pdf.set_font("Times", size=15, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="CARDIO VASCULAR RISK ANALYSIS", ln=True, align='C')
            
            # Add Test report and observations text
            pdf.set_font("Arial", size=14, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test report and observations", ln=True, align='C')
            # pdf.ln(10)  # Add a line break

            # Adding table headers with colors
            pdf.set_fill_color(*header_color)
            pdf.set_text_color(255, 255, 255)  # White font color for headers
            pdf.cell(65, 10, txt="Parameter", ln=0, align='C', fill=True)
            pdf.cell(65, 10, txt="Values", ln=0, align='C', fill=True)
            pdf.cell(65, 10, txt="Unit", ln=1, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Adding table data with colors
            parameters = [
                ["Pulse Rate", str(json_data.get("pulse_rate", {}).get("mean", "-")), "bpm"],
                ["Pulse Rate Variance", str(json_data.get("pulse_rate", {}).get("var", "-")), "-"],
                ["Stiffness Index", str(json_data.get("si_mean", "-")), "-"],
                ["Augmentation Index", str(json_data.get("ai_mean", "-")), "%"],
                ["Pulse Wave Velocity", str(json_data.get("pulse_wave", {}).get("velocity", "-")), "m/s"],
                ["Ejection Duration", str(json_data.get("eject_duration", "-")), "ms"],
                ["Relative Crest Time Ratio", str(json_data.get("rel_crest_time", "-")), "s"],
                ["Average Pulse Height", str(json_data.get("pulse", {}).get("height", "-")), "mV"],
                ["Average Pulse Width Duration", str(json_data.get("pulse", {}).get("width", "-")), "ms"],
                ["Dichrotic Wave Time", str(json_data.get("dicr_wave_time", "-")), "ms"],
                ["Average Dicrotic Wave Height", str(json_data.get("pulse_wave", {}).get("transit_time", "-")), "mV"],
                ["Delay Time", str(json_data.get("delay_time", "-")), "ms"]
            ]

            for i, parameter in enumerate(parameters):
                for j, val in enumerate(parameter):
                    if j == 0:  # First column background color
                        pdf.set_fill_color(207, 236, 237)  # #CFECED
                        pdf.set_font("Arial", size=12)  # Set font size to 12 for content
                        pdf.cell(65, 10, txt=val, ln=0, align='L', fill=True)
                    elif j in (1, 2):  # Second and third column background color
                        pdf.set_fill_color(229, 247, 223)  # #E5F7DF
                        pdf.set_font("Arial", size=12)  # Set font size to 12 for content
                        pdf.cell(65, 10, txt=val, ln=0, align='C', fill=True)
                    else:
                        pdf.set_font("Arial", size=14)  # Reset font size to 14 for headers
                        pdf.cell(65, 10, txt=val, ln=0, align='C', fill=True)
                pdf.cell(0, 10, txt="", ln=True)  # Adding a new line after each row


            # Add a new page
            pdf.add_page()

            # You can add content to the new page here
            # Load logo image
            try:
                # Save the binary image data to temporary files
                desktop_icon_data = get_embedded_image_data("images\\desktopicon.png")
                desktop_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                desktop_icon_temp_file.write(desktop_icon_data)
                desktop_icon_temp_file.close()

                precog_icon_data = get_embedded_image_data("images\\Precog.png")
                precog_icon_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                precog_icon_temp_file.write(precog_icon_data)
                precog_icon_temp_file.close()

                # Now use the paths to the temporary files in the pdf.image() function
                pdf.image(desktop_icon_temp_file.name, x=86, y=10, w=12)
                pdf.image(precog_icon_temp_file.name, x=100, y=12, w=30)

                # Don't forget to clean up the temporary files after using them
                os.unlink(desktop_icon_temp_file.name)
                os.unlink(precog_icon_temp_file.name)
            except Exception as e:
                print("Error loading image:", e)

            # Define colors
            header_color = (89, 124, 146)  # #597C92

            # Move cursor to a new line after the logo
            pdf.ln(30)

            # Add Test Details heading with font color #597C92
            pdf.set_font("Times", size=15, style='B')
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test Details", ln=True, align='L', fill=False)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Add Test Details with background color #E5F7DF
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_font("Arial", size=12)
            test_details = [
                f"Name : {patientName}",
                f"Date : {formatted_date}",
                f"Age/Gender : {calculate_age(dob)} years /{gender}",
                f"Time : {formatted_time}",
                f"Weight/Height : {weight} kg /{height} cm",
                f"Referred by :",
                f"Hospital name : {hospitalName}",
                ""

            ]
            cell_width = pdf.w / 2
            for i in range(len(test_details)):
                linebreak=False
                if i%2!=0:
                    linebreak=True
                if i==len(test_details)-1:
                    linebreak=True
                pdf.cell(cell_width, 10, txt=test_details[i], ln=linebreak, fill=True)

            pdf.cell(0, 10, txt="", ln=True)

            # Add CARDIO VASCULAR RISK ANALYSIS text
            pdf.set_font("Times", size=15, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="CARDIO VASCULAR RISK ANALYSIS", ln=True, align='C')
            
            # Add Test report and observations text
            pdf.set_font("Arial", size=14, style='B')
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Test report and observations", ln=True, align='C')
            # pdf.ln(10)  # Add a line break
            
            pdf.ln()
            # Add Radial Arterial Pulse Waveform heading with font color #597C92
            pdf.set_font("Times", size=14, style='B')
            pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
            pdf.set_text_color(89, 124, 146)  # Font color: #597C92
            pdf.cell(0, 10, txt="Radial Arterial Pulse Waveform", ln=True, align='L', fill=False)
            pdf.set_text_color(0, 0, 0)  # Reset font color to black

            # Add images to the second page
            try:
                # pdf.image("logo.png", x=86, y=10, w=12)
                # pdf.image("Precog.png", x=100, y=12, w=30)
                pdf.ln(30)
                pdf.set_font("Arial", size=12)
                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.set_text_color(89, 124, 146)  # Font color: #597C92
                # pdf.cell(0, 10, txt="Graphs", ln=True, align='L', fill=False)
                pdf.set_text_color(0, 0, 0)  # Reset font color to black

                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.cell(0, 10, txt="", ln=True)

                # Decode and save the first image
                save_image_from_base64(json_data["plots"]["radial_signal"], "graph1.png")
                pdf.image("graph1.png", x=10, y=150, w=200)
                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.cell(0, 10, txt="", ln=True)

                pdf.ln()
                # AddRadial Pressure Waveform heading with font color #597C92
                pdf.set_font("Times", size=14, style='B')
                pdf.set_fill_color(229, 247, 223)  # Background color: #E5F7DF
                pdf.set_text_color(89, 124, 146)  # Font color: #597C92
                pdf.cell(0, 10, txt="Radial Pressure Waveform", ln=True, align='L', fill=False)
                pdf.set_text_color(0, 0, 0)  # Reset font color to black

                # Decode and save the second image
                save_image_from_base64(json_data["plots"]["overlap_radial_signal"], "graph3.png")
                pdf.image("graph3.png", x=10, y=pdf.get_y() , w=100)

                pdf.output(file_path)
                print(f"PDF report generated successfully: {file_path}")
                label_download_status.config(text="Done! Check downloads folder")
                        # print(f"PDF report generated successfully: {file_name}")
            except Exception as e:
                print("Error adding images to the second page:", e)

            
            # messagebox.showinfo("Downloaded successfull",f"Please check your downloads folders: {file_path}")

            
        else:
            print("No JSON data received")

# =============================================== new content ============================================================
            

    # Main frames
    frame1_1 = Frame(frame1, bg="white")
    frame1_1.pack( side="left",pady=5)

    frame1_2 = Frame(frame1, bg="white")
    frame1_2.pack( side="right",pady=5)

    frame2_1 = Frame(frame2, bg="white")
    frame2_1.pack(expand=1, fill=BOTH)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=0,pady=5,fill=X)


    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)

        label_precog.config(font=("helvetica",font_size+14))
        label_heading.config(font=("helvetica",font_size+16))
        home_btn.config(font=("helvetica",font_size))
        label_parameters.config(font=("helvetica",font_size+8),fg="#464DB6")
        label_unit.config(font=("helvetica",font_size+8),fg="#464DB6")
        label_normal_value.config(font=("helvetica",font_size+8),fg="#464DB6")
        label_observed_value.config(font=("helvetica",font_size+8),fg="#464DB6")

        # label_parameter.config(font=("helvetica",font_size+12),padx=(160))
        # label_value.config(font=("helvetica",font_size+12),padx=(160))
        # label_pulserate.config(font=("helvetica",font_size),padx=(160))
        # value_pulserate.config(font=("helvetica",font_size),padx=(160))
        # label_pulseratevariance.config(font=("helvetica",font_size),padx=(160))
        # value_pulseratevar.config(font=("helvetica",font_size),padx=(160))
        # label_pulseratevarper.config(font=("helvetica",font_size),padx=(160))
        # value_pulseratevarper.config(font=("helvetica",font_size),padx=(160))
        # label_pulsewavevel.config(font=("helvetica",font_size),padx=(160))
        # value_pulsewavevel.config(font=("helvetica",font_size),padx=(160))
        # label_ejectiondur.config(font=("helvetica",font_size),padx=(160))
        # value_ejectiondur.config(font=("helvetica",font_size),padx=(160))
        # label_relcresttime.config(font=("helvetica",font_size),padx=(160))
        # value_relcresttime.config(font=("helvetica",font_size),padx=(160))
        # label_avgpulseheight.config(font=("helvetica",font_size),padx=(160))
        # value_avgpulseheight.config(font=("helvetica",font_size),padx=(160))
        # label_avgpulsewidth.config(font=("helvetica",font_size),padx=(160))
        # value_avgpulsewidth.config(font=("helvetica",font_size),padx=(160))
        # label_dicroticwavetime.config(font=("helvetica",font_size),padx=(160))
        # value_dicroticwavetime.config(font=("helvetica",font_size),padx=(160))
        # label_dicroticwaveheight.config(font=("helvetica",font_size),padx=(160))
        # value_dicroticwaveheight.config(font=("helvetica",font_size),padx=(160))
        # label_footer.config(font=("helvetica",font_size))

        # screen_width = top_level.winfo_width()
        # font_size = int(screen_width / 80)
        # top_level.config(font=("helvetica",font_size))
    
    frame_main = Frame(frame2_1,bg="white")
    frame_main.pack(expand=1,fill="both",padx=10)

    # frame1_inner = Frame(frame_main,bg="white")
    # frame1_inner.pack(expand=1,fill="both",side="top")

    frame2_inner = Frame(frame_main,bg="white")
    frame2_inner.pack(expand=0,fill="both") 


    # preview table frame structure starts here 
   
    frame_v = Frame(frame_main,bg="white")
    frame_v.pack(expand=1,fill=BOTH)

    # first 4 vertical frames for preview table

    frame_v_1 = Frame(frame_v,bg="white")
    frame_v_1.pack(side=LEFT,expand=1,fill=BOTH,anchor=W)

    frame_v_2 = Frame(frame_v,bg="white")
    frame_v_2.pack(side=LEFT,expand=1,fill=Y)

    frame_v_3 = Frame(frame_v,bg="white")
    frame_v_3.pack(side=LEFT,expand=1,fill=BOTH)

    frame_v_4 = Frame(frame_v,bg="white")
    frame_v_4.pack(side=LEFT,expand=1,fill=BOTH)


    # #content 
    label_precog = Label(frame1_1,text="PRECOG",bg="white",fg="#464DB6")
    label_precog.pack(side="left",padx=10)

    home_btn = Button(frame1_2,text="Home",bg="white",fg="#464DB6",border=0,highlightthickness=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame3_1.destroy(),Modules()))
    home_btn.pack(side=RIGHT,padx=10)

    def goBack():
        frame1_1.destroy()
        frame1_2.destroy()
        frame2_1.destroy()
        frame3_1.destroy()
        singleSensorApp = SingleSensorLogic(root,patientName,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid) 
        

    back_btn = Button(frame2_inner,image=backbtnimageblue2,border=0,highlightthickness=0,bg="white",command=lambda:(goBack()))
    back_btn.pack(side=LEFT)

    label_heading = Label(frame2_inner,text="Preview: Cardio Vascular Risk Analysis",fg="#464DB6",bg="white")
    label_heading.pack(side=LEFT)

    label_download_status = Label(frame2_inner,bg="white",fg="#464DB6")
    label_download_status.pack(side=RIGHT)

    download_button = Button(frame2_inner,image=downloadbutton2,border=0,highlightthickness=0,command=lambda:(download_parameters_pdf(parameters,patientName,filepath ,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid)))
    download_button.pack(side="right")

# content inside preview table 
    # content in v1
    label_parameters = Label(frame_v_1,bg="white",text="Parameter")
    label_parameters.pack(expand=1,fill=BOTH)

    label_pulserate = Label(frame_v_1,bg="white",text="Pulse Rate")
    label_pulserate.pack(expand=1,fill=BOTH)

    label_pulseratevar = Label(frame_v_1,bg="white",text="Pulse Rate Variance")
    label_pulseratevar.pack(expand=1,fill=BOTH)

    label_pulseratevarper = Label(frame_v_1,bg="white",text="% Pulse Rate Variance")
    label_pulseratevarper.pack(expand=1,fill=BOTH)

    label_si = Label(frame_v_1,bg="white",text="Stiffness Index")
    label_si.pack(expand=1,fill=BOTH)

    label_ai = Label(frame_v_1,bg="white",text="Augmentation Index")
    label_ai.pack(expand=1,fill=BOTH)

    label_pulsewavevel = Label(frame_v_1,bg="white",text="Pulse Wave Velocity")
    label_pulsewavevel.pack(expand=1,fill=BOTH)

    label_ejecdur = Label(frame_v_1,bg="white",text="Ejection Duration")
    label_ejecdur.pack(expand=1,fill=BOTH)

    label_relcresttime = Label(frame_v_1,bg="white",text="Relative Crest Time Ratio")
    label_relcresttime.pack(expand=1,fill=BOTH)

    label_avg_pulse_height = Label(frame_v_1,bg="white",text="Average Pulse Height")
    label_avg_pulse_height.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur = Label(frame_v_1,bg="white",text="Average Pulse Width Duration")
    label_avg_pulse_width_dur.pack(expand=1,fill=BOTH)

    label_dic_wave_time = Label(frame_v_1,bg="white",text="Dichrotic Wave Time")
    label_dic_wave_time.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height = Label(frame_v_1,bg="white",text="Average Dicrotic Wave Height")
    label_avg_dic_wave_height.pack(expand=1,fill=BOTH)

    label_delay_time = Label(frame_v_1,bg="white",text="Delay Time")
    label_delay_time.pack(expand=1,fill=BOTH)





    # content in v2 
    label_unit = Label(frame_v_2,bg="white",text="Unit")
    label_unit.pack(expand=1,fill=BOTH)

    label_pulserate_unit = Label(frame_v_2,bg="white",text="bpm")
    label_pulserate_unit.pack(expand=1,fill=BOTH)

    label_pulseratevar_unit = Label(frame_v_2,bg="white",text="-")
    label_pulseratevar_unit.pack(expand=1,fill=BOTH)

    label_pulseratevarper_unit = Label(frame_v_2,bg="white",text="%")
    label_pulseratevarper_unit.pack(expand=1,fill=BOTH)

    label_si_unit = Label(frame_v_2,bg="white",text="-")
    label_si_unit.pack(expand=1,fill=BOTH)

    label_ai_unit = Label(frame_v_2,bg="white",text="%")
    label_ai_unit.pack(expand=1,fill=BOTH)

    label_pulsewavevel_unit = Label(frame_v_2,bg="white",text="m/s")
    label_pulsewavevel_unit.pack(expand=1,fill=BOTH)

    label_ejecdur_unit = Label(frame_v_2,bg="white",text="ms")
    label_ejecdur_unit.pack(expand=1,fill=BOTH)

    label_relcresttime_unit = Label(frame_v_2,bg="white",text="s")
    label_relcresttime_unit.pack(expand=1,fill=BOTH)

    label_avg_pulse_height_unit = Label(frame_v_2,bg="white",text="mV")
    label_avg_pulse_height_unit.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur_unit = Label(frame_v_2,bg="white",text="ms")
    label_avg_pulse_width_dur_unit.pack(expand=1,fill=BOTH)

    label_dic_wave_time_unit = Label(frame_v_2,bg="white",text="ms")
    label_dic_wave_time_unit.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height_unit = Label(frame_v_2,bg="white",text="mV")
    label_avg_dic_wave_height_unit.pack(expand=1,fill=BOTH)

    label_delay_time_unit = Label(frame_v_2,bg="white",text="ms")
    label_delay_time_unit.pack(expand=1,fill=BOTH)



    # content in v3
    label_normal_value = Label(frame_v_3,bg="white",text="Normal value")  
    label_normal_value.pack(expand=1,fill=BOTH)

    label_pulserate_nv = Label(frame_v_3,bg="white",text="")
    label_pulserate_nv.pack(expand=1,fill=BOTH)

    label_pulseratevar_nv = Label(frame_v_3,bg="white",text=f"")
    label_pulseratevar_nv.pack(expand=1,fill=BOTH)

    label_pulseratevarper_nv = Label(frame_v_3,bg="white",text=f"")
    label_pulseratevarper_nv.pack(expand=1,fill=BOTH)

    label_si_nv = Label(frame_v_3,bg="white",text=f"")
    label_si_nv.pack(expand=1,fill=BOTH)

    label_ai_nv = Label(frame_v_3,bg="white",text=f"")
    label_ai_nv.pack(expand=1,fill=BOTH)

    label_pulsewavevel_nv = Label(frame_v_3,bg="white",text=f"")
    label_pulsewavevel_nv.pack(expand=1,fill=BOTH)

    label_ejecdur_nv = Label(frame_v_3,bg="white",text=f"")
    label_ejecdur_nv.pack(expand=1,fill=BOTH)

    label_relcresttime_nv = Label(frame_v_3,bg="white",text=f"")
    label_relcresttime_nv.pack(expand=1,fill=BOTH)

    label_avg_pulse_height_nv = Label(frame_v_3,bg="white",text=f"")
    label_avg_pulse_height_nv.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur_nv = Label(frame_v_3,bg="white",text=f"")
    label_avg_pulse_width_dur_nv.pack(expand=1,fill=BOTH)

    label_dic_wave_time_nv = Label(frame_v_3,bg="white",text=f"")
    label_dic_wave_time_nv.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height_nv = Label(frame_v_3,bg="white",text=f"")
    label_avg_dic_wave_height_nv.pack(expand=1,fill=BOTH)

    label_delay_time_nv = Label(frame_v_3,bg="white",text=f"")
    label_delay_time_nv.pack(expand=1,fill=BOTH)





    # content in v4
    label_observed_value = Label(frame_v_4,bg="white",text="Observed value")  
    label_observed_value.pack(expand=1,fill=BOTH)

    label_pulserate_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_rate']['mean']}")
    label_pulserate_ov.pack(expand=1,fill=BOTH)

    label_pulseratevar_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_rate']['var']}")
    label_pulseratevar_ov.pack(expand=1,fill=BOTH)

    label_pulseratevarper_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_rate']['var_percent']}")
    label_pulseratevarper_ov.pack(expand=1,fill=BOTH)

    label_si_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('si_mean')}")
    label_si_ov.pack(expand=1,fill=BOTH)

    label_ai_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('ai_mean')}")
    label_ai_ov.pack(expand=1,fill=BOTH)

    label_pulsewavevel_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse_wave']['velocity']}")
    label_pulsewavevel_ov.pack(expand=1,fill=BOTH)

    label_ejecdur_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('eject_duration')}")
    label_ejecdur_ov.pack(expand=1,fill=BOTH)

    label_relcresttime_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('rel_crest_time')}")
    label_relcresttime_ov.pack(expand=1,fill=BOTH)

    label_avg_pulse_height_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse']['height']}")
    label_avg_pulse_height_ov.pack(expand=1,fill=BOTH)

    label_avg_pulse_width_dur_ov = Label(frame_v_4,bg="white",text=f"{parameters['pulse']['width']}")
    label_avg_pulse_width_dur_ov.pack(expand=1,fill=BOTH)

    label_dic_wave_time_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('dicr_wave_time')}")
    label_dic_wave_time_ov.pack(expand=1,fill=BOTH)

    label_avg_dic_wave_height_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('dicr_height_mean')}")
    label_avg_dic_wave_height_ov.pack(expand=1,fill=BOTH)

    label_delay_time_ov = Label(frame_v_4,bg="white",text=f"{parameters.get('delay_time')}")
    label_delay_time_ov.pack(expand=1,fill=BOTH)





    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack()

    frame_main.bind("<Configure>", on_frame_configure)

# =====================================================================   generate report =============================================================================
    
def generate_report(filepath, patientName ,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid): 
    # ===============================patients module ==============
    def fetchingData():
        api_url = 'http://13.201.87.54:8000/parameter/compute'

        # Read the JSON file
        with open(filepath, 'r') as file:
            json_data = json.load(file)
            
        headers = {'Content-Type': 'application/json'}

        # Add additional fields to the JSON data
        json_data["d_notch_rad"] = int(rad)
        json_data["d_notch_ank"] = int(ank)
        json_data["patient_height"]= int(height)
        json_data["patient_uid"]= uid

        # Make the POST request with the JSON data
        response = requests.post(api_url, json=json_data, headers=headers)


        try:
            # Make the POST request with the JSON data
            response = requests.post(api_url, json=json_data, headers=headers)
            # loading_screen.destroy()

            # Check the response status
            if response.status_code == 200:
                print("POST request successful!")
                # print("Response:", response.json())

                # Display parameters in a new window
                frame1_1.destroy()
                frame1_2.destroy()
                frame2_1.destroy()
                frame3_1.destroy()
                show_parameters(response.json(), patientName, filepath, noofsensor, dob, hospitalName, gender, weight, rad, ank, height, uid)

            else:
                print("POST request failed with status code:", response.status_code)
                print("Response:", response.text)
                frame1_1.destroy()
                frame1_2.destroy()
                frame2_1.destroy()
                frame3_1.destroy()
                singleSensorApp = SingleSensorLogic(root,patientName,noofsensor,dob,hospitalName,gender,height,weight,ank,rad,uid)
                

        except Exception as e:

            # frame1_1.destroy()
            # frame1_2.destroy()
            # frame2_1.destroy()
            # frame3_1.destroy()
            # singleSensorApp = SingleSensorLogic(root,patientName,noofsensor,dob,hospitalName,gender,height,weight,ank,rad,uid)

            print(f"An error occurred: {e}")
















        # loading_screen.destroy()
        # # Check the response status
        # if response.status_code == 200:
        #     print("POST request successful!")
        #     # print("Response:", response.json())
        #     # Display parameters in a new window
        #     frame1_1.destroy()
        #     frame1_2.destroy()
        #     frame2_1.destroy()
        #     frame3_1.destroy()
        #     show_parameters(response.json(), patientName,filepath ,noofsensor,dob,hospitalName,gender,weight,rad,ank,height,uid) 
        # else:
        #     print("POST request failed with status code:", response.status_code)
        #     print("Response:", response.text)
        #     frame1_1.destroy()
        #     frame1_2.destroy()
        #     frame2_1.destroy()
        #     frame3_1.destroy()
        #     singleSensorApp = SingleSensorLogic(root,patientName,noofsensor,dob,hospitalName,gender,height,weight,ank,rad,uid)



    frame1_1 = Frame(frame1, bg="white")
    frame1_1.pack(expand=1, fill="both", side="left")

    frame1_2 = Frame(frame1, bg="white")
    frame1_2.pack(expand=1, fill="both", side="right")

    frame2_1 = Frame(frame2, bg="white")
    frame2_1.pack(expand=1, fill="both")

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=0,pady=5,fill=X) 

    img_label = tk.Label(frame1_1, image=original_img,bg="white")
    img_label.pack(side=LEFT,pady=(10),padx=10)

    label_footer= Label(frame3_1,bg="white",text="Copyright 2024 Acuradyne Systems")
    label_footer.pack(pady=5)

    gif_frames = [loadingAni1final2,loadingAni2final2,loadingAni3final2,loadingAni4final2]

    # Function to update GIF
    def update_gif(frame_number):
        gif_label.config(image=gif_frames[frame_number])
        frame_number = (frame_number + 1) % len(gif_frames)
        gif_label.after(500, update_gif, frame_number)  # Change delay (ms) as needed

    gif_label = Label(frame2_1,image="",bg="#CDDDFF")
    gif_label.pack(side=TOP ,anchor=S,expand=1,fill=BOTH)

    gif_label2 = Label(frame2_1,text="Generating your report. Please wait...",bg="#CDDDFF",fg="#2B318A")
    gif_label2.pack(side=BOTTOM,anchor=N,expand=1,fill=BOTH)
        # Start GIF animatio
    update_gif(0)


# Start other tasks in a separate thread
    thread = threading.Thread(target=fetchingData)
    thread.start()

# ==================================================================== patients modules is selected =================================================================

def patientsSelected():

    global pidToShow   
    pidToShow = ""
   

    def on_frame_configure(event):
        # configure_font_size(scrollable_frame)
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        label_precog.config(font=("helvetica", font_size+14))
        btn_home.config(font=("helvetica",font_size))
        # btn_back.config(font=("helvetica", font_size+10))
        label_listofpatients.config(font=("helvetica", font_size))
        search_patient.config(font=("helvetica", font_size))
        style.configure("Treeview.Heading", foreground="#2B318A",font=("Helvetica",font_size),borderwidth=0)
        # label_patientname.config(font=("helvetica", font_size))
        # label_phoneno.config(font=("helvetica", font_size))
        label_patient_list.config(font=("helvetica", font_size))
        # listbox.config(font=("helvetica", font_size+10))

        label_name_value.config(font=("helvetica", font_size))
        label_age_value.config(font=("helvetica", font_size))
        label_gender_value.config(font=("helvetica", font_size))
        label_weight_value.config(font=("helvetica", font_size))
        label_height_value.config(font=("helvetica", font_size))
        label_bmi_value.config(font=("helvetica", font_size))


        label_name.config(font=("helvetica", font_size))
        label_age.config(font=("helvetica", font_size))
        label_gender.config(font=("helvetica", font_size))
        label_weight.config(font=("helvetica", font_size))
        label_height.config(font=("helvetica", font_size))
        label_bmi.config(font=("helvetica", font_size))


        label_patient_detail.config(font=("helvetica", font_size+10))




    def populate_list(event=None):
        # Clear the listbox first
        tree.delete(*tree.get_children())
        
        # Get the text from the entry widget
        filter_text = search_patient.get().lower()
        
       
        sr = 1
        for item in patient_data2:
            if item.lower().startswith(filter_text):
                data_list = item.split(',')
                tree.insert("", "end", text=f"{sr}", values=(f"{data_list[0]}", f"{data_list[1]}"))
                sr= sr+1


    def on_select(event):

        global phone_number,hospital_id,email_id,height_,weight_,gender_,dob_,patientName_,hospitalName_
        selected_item = tree.selection()[0]
        
        # Get item's values
        values = tree.item(selected_item, 'values')

        
        # Search for the selected name in patient_data
        for patient in patient_data:
            if patient.startswith(f"{values[0]},{values[1]}"):             
                # Get the corresponding phone number and email
                data_list = patient.split(',')
                patientName_ = data_list[0]
                phone_number = data_list[1]
                hospital_id = data_list[2]
                email_id = data_list[3]
                height_ = int(data_list[4])
                weight_ = int(data_list[5])
                gender_ = data_list[6]
                dob_ = data_list[7]
                hospitalName_ = data_list[8]
              

                #lets calculate bmi using height and weight 
                height_bmi = int(height_)/100
                weight_bmi = int(weight_)
                bmi_ = weight_bmi/ (height_bmi ** 2)

                            # patient_data.append(f"{name}, {phone}, {hospitalid}, {email}, {height}, {weight}, {gender}")

                # Update the labels with phone number and email
                label_name_value.config(text=phone_number)
                label_age_value.config(text=f"{calculate_age(dob_)} years")
                label_gender_value.config(text=gender_)
                label_weight_value.config(text=f"{weight_} kg")
                label_height_value.config(text=f"{height_} cm")
                label_bmi_value.config(text=f"{bmi_:.2f}")


                #some database things to fetch history 
                # Define the collection reference
                collection_ref = db.collection("patients")

                # Define the criteria for name and phone
                target_name = values[0]
                target_phone = values[1]

                # Query documents in the collection
                query = collection_ref.where("name", "==", target_name).where("phone", "==", target_phone).stream()
                docId = ""
                for doc in query:
                    # Print the document ID
                    docId = doc.id
                
                    break 
                bucket = storage.bucket()

                # UID of the user
                uid = "87IWAP2aoSiYlyXvxXvI"
                epoch_list = []

                # Reference to the folder with UID
                uid_folder = bucket.blob(docId)
                global pidToShow
                pidToShow = docId

                tree2.delete(*tree2.get_children())
                blobs = bucket.list_blobs(prefix=docId)
                CountSr = 1
                for blob in blobs:
                    # Extract date and time from blob name 
                    parts = blob.name.split('/')
                    if parts[-2] in epoch_list:
                        continue

                    else:
                        epoch_list.append(parts[-2])
                        time_str = parts[-2].replace('$', '')
                        dateTime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(time_str))) 
                
                        tree2.insert("", "end", text=f"{CountSr}", values=(f'"{dateTime}"'))
                        CountSr = CountSr+1



                return  # Break out of the loop once found
            

    # Main frames
    frame1_1 = Frame(frame1, bg="white")
    frame1_1.pack(expand=1, fill="both", side="left")

    frame1_2 = Frame(frame1, bg="white")
    frame1_2.pack(expand=1, fill="both", side="right")

    frame2_1 = Frame(frame2, bg="white")
    frame2_1.pack(expand=0, fill="x")

    frame2_2 = Frame(frame2, bg="white")
    frame2_2.pack(expand=1, fill=BOTH)
    # ======================================================

    frame2_2_left = Frame(frame2_2,bg="#2B318A")
    frame2_2_left.pack(expand=1,side=LEFT,pady=20)

    frame2_2_right = Frame(frame2_2,bg="white")
    frame2_2_right.pack(expand=1,fill=BOTH,side=RIGHT,pady=20)
    # =======================================================

    # #sub frames in left frame 
    frame2_2_inner1 = Frame(frame2_2_left,bg="#CDDDFF")
    frame2_2_inner1.pack(pady=20)

    frame2_2_inner2 = Frame(frame2_2_left,bg="#CDDDFF")
    frame2_2_inner2.pack(expand=0,pady=20 )

    #two vertical sub frames in inner2 
    frame2_2_inner2_left = Frame(frame2_2_inner2,bg="#CDDDFF")
    frame2_2_inner2_left.pack(side=LEFT,expand=0,fill=X,padx=10)

    frame2_2_inner2_right = Frame(frame2_2_inner2,bg="#CDDDFF")
    frame2_2_inner2_right.pack(side=RIGHT,expand=0,fill=X,padx=10)

# ===========================================================
    #now three frames in left and right respectively 

    frame2_2_inner2_left_inner1 = Frame(frame2_2_inner2_left,bg="#CDDDFF")
    frame2_2_inner2_left_inner1.pack(expand=1,fill=BOTH)

    frame2_2_inner2_left_inner2 = Frame(frame2_2_inner2_left,bg="#CDDDFF")
    frame2_2_inner2_left_inner2.pack(expand=1,fill=BOTH)

    frame2_2_inner2_left_inner3 = Frame(frame2_2_inner2_left,bg="#CDDDFF")
    frame2_2_inner2_left_inner3.pack(expand=1,fill=BOTH)



    frame2_2_inner2_right_inner1 = Frame(frame2_2_inner2_right,bg="#CDDDFF")
    frame2_2_inner2_right_inner1.pack(expand=1,fill=BOTH)

    frame2_2_inner2_right_inner2 = Frame(frame2_2_inner2_right,bg="#CDDDFF")
    frame2_2_inner2_right_inner2.pack(expand=1,fill=BOTH)

    frame2_2_inner2_right_inner3 = Frame(frame2_2_inner2_right,bg="#CDDDFF")
    frame2_2_inner2_right_inner3.pack(expand=1,fill=BOTH)

    # ======================================================
    #adding more frames inside frame2_2_left

    frame_patient_history_label = Frame(frame2_2_left)
    frame_patient_history_label.pack()

    frame_patient_history_data = Frame(frame2_2_left)
    frame_patient_history_data.pack()

    frame3_1 = Frame(frame3, bg="white")
    frame3_1.pack(expand=1, fill="both")



# =====================================content here =========================


    # # Header content 
    label_precog = Label(frame1_1, bg="white", text="PRECOG", fg="#2B318A")
    label_precog.pack(side="left", pady=10,padx=10)

    btn_home = Button(frame1_2,bg="white",border=0,text="Home",fg="#2B318A",command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_home.pack(side=RIGHT,padx=10)

    btn_refresh = Button(frame1_2,bg="white",border=0,text="Refresh",fg="#2B318A",command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),update_users(patientsSelected)))
    btn_refresh.pack(side=RIGHT,padx=10)


    btn_back = Button(frame2_1, bg="white",image=backbtnimageblue2, border=0, highlightthickness=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_back.pack(side="left",padx=10)

    label_patient_list = Label(frame2_1, bg="white", text="List of Patients", fg="#464DB6")
    label_patient_list.pack(side="left")

    search_patient = Entry(frame2_1, bg="#F2F2F2")
    search_patient.pack(expand=1, fill=X, side="right",padx=10)

    # # Bind the update_scrollable_frame function to the KeyRelease event of the search_patient entry widget
    # # search_patient.bind("<KeyRelease>", update_scrollable_frame)
    label_listofpatients = Label(frame2_1, text="Search Patient",fg="#464DB6",bg="white")
    label_listofpatients.pack(side="right",padx=(400,0))

    # Fetch patient data from Firestore and store it in patient_data list

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Helvetica", 12),borderwidth=0)
    #treeview on right side to show list of patients 
    tree = ttk.Treeview(frame2_2_right,height=20)

    # Define columns
    tree["columns"] = ("Name", "PhoneNo")

    # Add columns
    tree.column("#0")
    tree.column("Name")
    tree.column("PhoneNo")

    # Define column headings
    tree.heading("#0", text="ID", anchor=tk.W)
    tree.heading("Name", text="Name" ,anchor=tk.W)
    tree.heading("PhoneNo", text="PhoneNo", anchor=tk.W)

    sr = 1
    for item in patient_data2:
        data_list = item.split(',')
        tree.insert("", "end", text=f"{sr}", values=(f"{data_list[0]}", f"{data_list[1]}"))
        sr= sr+1
        

    # Pack the Treeview widget
    tree.pack(expand=1,fill=Y)


    label_patient_detail = Label(frame2_2_inner1,text="PATIENT DETAILS",bg="#2B318A",fg="white")
    label_patient_detail.pack()

    label_name = Label(frame2_2_inner2_left_inner1,text="Name:",bg="#CDDDFF")
    label_name.pack(side=LEFT)

    label_name_value = Label(frame2_2_inner2_left_inner1,text="",bg="#CDDDFF")
    label_name_value.pack(side=LEFT)

    label_gender = Label(frame2_2_inner2_left_inner2,text="Gender:",bg="#CDDDFF")
    label_gender.pack(side=LEFT)

    label_gender_value = Label(frame2_2_inner2_left_inner2,text="",bg="#CDDDFF")
    label_gender_value.pack(side=LEFT)



    label_height = Label(frame2_2_inner2_left_inner3,text="Height:",bg="#CDDDFF")
    label_height.pack(side=LEFT)

    label_height_value = Label(frame2_2_inner2_left_inner3,text="",bg="#CDDDFF")
    label_height_value.pack(side=LEFT)



    label_weight = Label(frame2_2_inner2_right_inner1,text="Weight:",bg="#CDDDFF")
    label_weight.pack(side=LEFT)

    label_weight_value = Label(frame2_2_inner2_right_inner1,text="",bg="#CDDDFF")
    label_weight_value.pack(side=LEFT)


    label_age = Label(frame2_2_inner2_right_inner2,text="Age:",bg="#CDDDFF")
    label_age.pack(side=LEFT)

    label_age_value = Label(frame2_2_inner2_right_inner2,text="",bg="#CDDDFF")
    label_age_value.pack(side=LEFT)


    label_bmi = Label(frame2_2_inner2_right_inner3,text="BMI:",bg="#CDDDFF")
    label_bmi.pack(side=LEFT)

    label_bmi_value = Label(frame2_2_inner2_right_inner3,text="",bg="#CDDDFF")
    label_bmi_value.pack(side=LEFT)

# ==================================
#needs to update this function 
    

    tree2 = ttk.Treeview(frame2_2_left)

    # Define columns
    tree2["columns"] = ("DateTime")

    # Add columns
    tree2.column("#0")
    tree2.column("DateTime")
 

    # Define column headings
    tree2.heading("#0", text="Test No", anchor=tk.W)
    tree2.heading("DateTime", text="DateTime" ,anchor=tk.W)
 

    # sr2 = 1
    # for item in patient_data2:
    #     data_list = item.split(',')
    #     tree2.insert("", "end", text=f"{sr}", values=(f"{data_list[0]}", f"{data_list[1]}"))
    #     sr2= sr2+1
        

    # Pack the Treeview widget
    tree2.pack(expand=0)
    tree2.bind("<Configure>", on_frame_configure)    

# ========================================
    def see_report():
        selected_item = tree2.selection()[0]  # Get the ID of the selected item
        values = tree2.item(selected_item, "values")
        date = values[0]

        date_string = date
        import re


        # Parse the date string into a datetime object
        date_object = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S")

        # Convert the datetime object to a Unix epoch timestamp
        epoch_timestamp = int(date_object.timestamp())

        # Replace the hour part with "5"
        modified_date_string = re.sub(r'\b\d{1,2}:\d{2}:\d{2}\b', '5:30:00', date_string)

        # Parse the date string into a datetime object
        date_object2 = datetime.strptime(modified_date_string, "%a, %d %b %Y %H:%M:%S")

        # Convert the datetime object to a Unix epoch timestamp
        epoch_timestamp2 = int(date_object2.timestamp())

        print("Epoch Timestamp:", epoch_timestamp2, epoch_timestamp)

                # Reference to the file
        # Reference to the file
        blob = storage.bucket().blob(f"{pidToShow}/{epoch_timestamp2}/${epoch_timestamp}$/graphMetadata.json")     

        # Download the file
        content = blob.download_as_string()

        # Decode the content and parse JSON
        data = json.loads(content)

        # Print the content of the file
        print("Content of graphMetadata.json:")
        print(data)
        frame1_1.destroy()
        frame1_2.destroy()
        frame2_1.destroy()
        frame2_2.destroy()
        frame3_1.destroy()
        show_parameters_history(data)


# =========================================

    btn_see_report = Button(frame2_2_left,image=showReportButtonfinal,border=0,highlightthickness=0,command=lambda:(see_report()))
    btn_see_report.pack(pady=10)

    # # Bind the KeyRelease event to the populate_list function
    search_patient.bind('<KeyRelease>', populate_list)

 

    label_footer = Label(frame3_1, text="Copyright © 2024 Acuradyne Medical Systems", bg="white",fg="black")
    label_footer.pack(pady=5)

    # # frame2_3.bind("<Configure>", on_frame_configure)
    frame1_1.bind("<Configure>", on_frame_configure)
    frame1_2.bind("<Configure>", on_frame_configure)
    frame2_1.bind("<Configure>", on_frame_configure)
    frame2_2.bind("<Configure>", on_frame_configure)
    frame3_1.bind("<Configure>", on_frame_configure)

        # Bind click event to show selected item
    tree.bind("<KeyRelease>", on_select)
    tree.bind("<ButtonRelease-1>", on_select)
    tree.bind("<Configure>", on_frame_configure)

# ===========================================================going back from secondary param to primary param ============================================================
def going_back_primary_param(name,gender,dob,email,phone,state,city):

    def validate_primary_param(name, gender, dob, email, phone, state, city):
       
        frame_3_inner.config(bg="white")
        frame_6_inner.config(bg="white")
        frame_8_inner.config(bg="white")
        frame_9_inner_2_2.config(bg="white")
        frame_4_inner_2_2.config(bg="white")
        frame_4_inner_1_2.config(bg="white")
        frame_9_inner_1_2.config(bg="white")

        if(name=="Name" or not name or email=="Email" or not email or phone=="Phone number" or not phone or city=="City"  or not city or not gender or not dob or not state):
            if(name=="Name" or not name):
                # entry_name.config(fg="red")
                frame_3_inner.config(bg="red")

            if(email=="Email id" or not email):
                # entry_email.config(fg="red")
                frame_6_inner.config(bg="red")

            if(phone=="Phone number" or not phone):
                # entry_phone.config(fg="red")
                frame_8_inner.config(bg="red")

            if(city=="City" or not city):
                # entry_city.config(fg="red") 
                frame_9_inner_2_2.config(bg="red")

            if(not gender):
                # label_gender.config(fg="red")
                frame_4_inner_1_2.config(bg="red")

            if(not dob):
                # label_dob.config(fg="red")
                frame_4_inner_2_2.config(bg="red")

            if(not state):
                # label_state.config(fg="red")
                frame_9_inner_1_2.config(bg="red")

            messagebox.showerror("Empty values", "Please enter all the fields")
            # addPatientSelected()
            return


        # elif not name or not gender or not dob or not email or not phone or not state or not city:
        #     messagebox.showerror("Incomplete Details", "Please enter complete details.")
        #     return 
        

        
        elif not validate_email(email):
            frame_6_inner.config(bg="red")
            messagebox.showerror("Signup Error", "Invalid email address.")
            return
        
        elif not validate_name(name):
            frame_3_inner.config(bg="red")
            messagebox.showerror("Signup Error", "Invalid name. Only letters are allowed.")
            return

        elif not validate_phone(phone):
            frame_8_inner.config(bg="red")
            messagebox.showerror("Signup Error", "Please enter a valid 10-digit phone number using only numeric characters (0-9).")
            return

        elif not validate_city(city):
            frame_9_inner_2_2.config(bg="red")
            messagebox.showerror("Signup Error","Invalid city. Only letters are allowed.")
            return
        
        else:
            frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy()
            secondary_param(name,gender,dob,email,phone,state,city)
        


    def on_name_entry_click(event):
        if entry_name.get() == placeholder_name:
            entry_name.delete(0, tk.END)

    def on_name_focus_out(event):
        if not entry_name.get():
            entry_name.insert(0, placeholder_name)

    def on_email_entry_click(event):
        if entry_email.get() == placeholder_email:
            entry_email.delete(0, tk.END)

    def on_email_focus_out(event):
        if not entry_email.get():
            entry_email.insert(0, placeholder_email)

    def on_phone_entry_click(event):
        if entry_phone.get() == placeholder_phone:
            entry_phone.delete(0, tk.END)

    def on_phone_focus_out(event):
        if not entry_phone.get():
            entry_phone.insert(0, placeholder_phone)

    def on_city_entry_click(event):
        if entry_city.get() == placeholder_city:
            entry_city.delete(0, tk.END)

    def on_city_focus_out(event):
        if not entry_city.get():
            entry_city.insert(0, placeholder_city)

    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)

        label_precog.config(font=("helvetica",font_size+14))

        label_add_patient.config(font=("helvetica",font_size+14))
        entry_name.config(font=("helvetica",font_size))
        label_gender.config(font=("helvetica",font_size))
        gender_dropdown.config(font=("helvetica",font_size))
        label_dob.config(font=("helvetica",font_size))
        dob_entry.config(font=("helvetica",font_size))
        entry_email.config(font=("helvetica",font_size))
        entry_phone.config(font=("helvetica",font_size))
        label_state.config(font=("helvetica",font_size))
        state_dropdown.config(font=("helvetica",font_size))
        entry_city.config(font=("helvetica",font_size))
        btn_next.config(font=("helvetica",font_size))
        label_precog.config(font=("helvetica",font_size+20))
        btn_home.config(font=("helvetica",font_size))

    #main frames
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1, fill=BOTH , side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1, fill=BOTH , side=RIGHT)

    frame2_1 = Frame(frame2,bg="white")
    frame2_1.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="white")
    frame2_2.pack(expand=1, fill=BOTH, side=RIGHT)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=1, fill=BOTH)

# ===============================================
    # header content 
    label_precog = Label(frame1_1,bg="white",text="PRECOG",fg="#2B318A")
    label_precog.pack(side=LEFT,pady=10,padx=10)

    btn_home = Button(frame1_2,bg="white",border=0,text="Home",fg="#2B318A",command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_home.pack(side=RIGHT,padx=10)


#     btn_help_support = Button(frame1_2,bg="white",border=0,underline=1,text="Help & Support",fg="#2B318A")
#     btn_help_support.pack(side=RIGHT)

# # ============================
    # left frame 
    frame2_1_inner = Frame(frame2_1,bg="#2B318A")
    frame2_1_inner.pack(expand=1,fill=BOTH,pady=10,padx=30)


    #inner sub frames
    frame_0_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_0_inner.pack(expand=1,fill=BOTH,padx=30)   

    frame_1_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_1_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_2_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_2_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_3_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_3_inner.pack(fill=X,expand=0,padx=30)

    frame_4_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_4_inner.pack(expand=1,fill=BOTH,padx=30)

# # ================
    #sub frames in 4 
    frame_4_inner_1 = Frame(frame_4_inner,bg="#2B318A")
    frame_4_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))

    frame_4_inner_2 = Frame(frame_4_inner,bg="#2B318A")
    frame_4_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))

    #two sub frames in 4_1 and 4_2 respective

    frame_4_inner_1_1 = Frame(frame_4_inner_1,bg="#2B318A")
    frame_4_inner_1_1.pack(expand=1,fill=BOTH)

    frame_4_inner_1_2 = Frame(frame_4_inner_1,bg="white",height=2)
    frame_4_inner_1_2.pack(expand=0,fill=X)

    frame_4_inner_2_1 = Frame(frame_4_inner_2,bg="#2B318A")
    frame_4_inner_2_1.pack(expand=1,fill=BOTH)

    frame_4_inner_2_2 = Frame(frame_4_inner_2,bg="white",height=2)
    frame_4_inner_2_2.pack(expand=0,fill=X)

# # ================


    frame_5_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_5_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_6_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_6_inner.pack(fill=X,padx=30)
    
    frame_7_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_7_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_8_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_8_inner.pack(fill=X,padx=30)

    frame_9_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_9_inner.pack(expand=1,fill=BOTH,padx=30)

    # ================
    #sub frames in 9 
    frame_9_inner_1 = Frame(frame_9_inner,bg="#2B318A")
    frame_9_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))

    frame_9_inner_2 = Frame(frame_9_inner,bg="#2B318A")
    frame_9_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))


    #two sub frames in 9_1 and 9_2 respective

    frame_9_inner_1_1 = Frame(frame_9_inner_1,bg="#2B318A")
    frame_9_inner_1_1.pack(expand=1,fill=BOTH)

    frame_9_inner_1_2 = Frame(frame_9_inner_1,bg="white",height=2)
    frame_9_inner_1_2.pack(expand=0,fill=X)

    frame_9_inner_2_1 = Frame(frame_9_inner_2,bg="#2B318A")
    frame_9_inner_2_1.pack(expand=1,fill=BOTH)

    frame_9_inner_2_2 = Frame(frame_9_inner_2,bg="white",height=2)
    frame_9_inner_2_2.pack(expand=0,fill=X)

    # ================

    frame_10_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_10_inner.pack(expand=1,fill=BOTH,padx=30)

# # ============================
#     # fields on left frames


    btn_back = Button(frame_0_inner,bg="#2B318A",image=backbtnimagefinal,fg="white",border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_back.pack(side=LEFT)

    label_add_patient = Label(frame_1_inner,text="ADD PATIENT",bg="#2B318A",fg="white")
    label_add_patient.pack(expand=1,fill=BOTH)

    placeholder_name = "Name"
    entry_name = Entry(frame_2_inner,border=0,bg="#2B318A",fg="white")
    entry_name.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_name.insert(0, placeholder_name)
    entry_name.bind("<FocusIn>", on_name_entry_click)
    entry_name.bind("<FocusOut>", on_name_focus_out)
  
    entry_name.delete(0, tk.END)
 
    entry_name.insert(0, name)

    label_gender = Label(frame_4_inner_1_1,text="Gender",bg="#2B318A",fg="white")
    label_gender.pack(side=LEFT,anchor=S)

    gender_options = ["Male","Female","Other"]
    gender_var = tk.StringVar()
    gender_dropdown = Combobox(frame_4_inner_1_1, textvariable=gender_var, values=gender_options,state="readonly")
    gender_dropdown.pack(side=RIGHT,anchor=S)
    gender_dropdown.set(gender)

    label_dob = Label(frame_4_inner_2_1,text="DOB",bg="#2B318A",fg="white")
    label_dob.pack(side=LEFT,anchor=S)



    dob_var = tk.StringVar()
    dob_entry = DateEntry(frame_4_inner_2_1, textvariable=dob_var, date_pattern='dd/mm/yyyy', showweeknumbers=False, selectbackground="#38B18E")
    dob_entry.pack(side=RIGHT,anchor=S)
    dob_entry.delete(0, tk.END)
    dob_entry.insert(0,dob)

    entry_email= Entry(frame_5_inner,border=0,bg="#2B318A",fg="white")
    entry_email.pack(side=LEFT,anchor=S,expand=1,fill=X)
    placeholder_email= "Email id"
    entry_email.insert(0, placeholder_email)
    entry_email.bind("<FocusIn>", on_email_entry_click)
    entry_email.bind("<FocusOut>", on_email_focus_out)
    entry_email.delete(0, tk.END)
    entry_email.insert(0, email)

    entry_phone = Entry(frame_7_inner,bg="#2B318A",border=0,fg="white")
    entry_phone.pack(side=LEFT,anchor=S,expand=1,fill=X)
    placeholder_phone = "Phone number"
    entry_phone.insert(0, placeholder_phone)
    entry_phone.bind("<FocusIn>", on_phone_entry_click)
    entry_phone.bind("<FocusOut>", on_phone_focus_out)
    entry_phone.delete(0, tk.END)
    entry_phone.insert(0,phone)

    label_state = Label(frame_9_inner_1_1,text="State",bg="#2B318A",fg="white")
    label_state.pack(side=LEFT,anchor=S)

    state_options = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
        "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    state_var = tk.StringVar()
    state_dropdown = Combobox(frame_9_inner_1_1, textvariable=state_var, values=state_options,state="readonly")
    state_dropdown.pack(side=RIGHT,anchor=S)
    state_dropdown.set(state)

    entry_city = Entry(frame_9_inner_2_1,border=0,bg="#2B318A",fg="white")
    entry_city.pack(side=LEFT,anchor=S,expand=1,fill=X)
    placeholder_city = "City"
    entry_city.insert(0, placeholder_city)
    entry_city.bind("<FocusIn>", on_city_entry_click)
    entry_city.bind("<FocusOut>", on_city_focus_out)
    entry_city.delete(0, tk.END)
    entry_city.insert(0,city)

    btn_next = Button(frame_10_inner,image=nextbtnimgfinal,border=0,highlightthickness=0,command=lambda:(validate_primary_param(entry_name.get(), gender_dropdown.get(), dob_entry.get(),entry_email.get(), entry_phone.get(), state_dropdown.get(), entry_city.get())))
    btn_next.pack(side=BOTTOM,pady=20)

    frame2_1_inner.bind("<Configure>", on_frame_configure)



# # ============================

    #btns on right
    btn1= Button(frame2_2,bg="white",image=btn1final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),recordNewTestSelected()))
    btn1.pack(expand=1,fill=BOTH)

    btn2= Button(frame2_2,bg="white",image=btn2SelectedFinal,border=0,command=lambda:())
    btn2.pack(expand=1,fill=BOTH)

    btn3= Button(frame2_2,bg="white",image=btn3final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),patientsSelected()))
    btn3.pack(expand=1,fill=BOTH)


    #footer content
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

# ====================================================================== secondary param ================================================================================

def secondary_param(name,gender,dob,email,phone,state,city):

    def patient_added(name,gender,dob,email,phone,state,city,height,weight,smoke,drink,diabetes,diagnosis,symptoms,medications,dnotchrad,dnotchank):
        frame_underline.config(bg="white")
        frame_underline2.config(bg="white")
        frame_underline6.config(bg="white")
        frame_underline7.config(bg="white")
        frame_5_inner.config(bg="white")

        # def validate_primary_param(name, gender, dob, email, phone, state, city):
        if(height=="Height (cm)" or weight=="Weight (kg)"  or dnotchrad=="d_notch_rad" or dnotchank=="d_notch_ank" or not diabetes ):
            if(height=="Height (cm)" or not height.strip()):
                frame_underline.config(bg="red")

            if(weight=="Weight (kg)" or not weight.strip()):
                frame_underline2.config(bg="red")

            if(dnotchrad=="radial distance" or not dnotchrad.strip()):
                frame_underline6.config(bg="red")

            if(dnotchank=="ankle distance" or not dnotchank.strip()):
                frame_underline7.config(bg="red")

            if not diabetes:
                frame_5_inner.config(bg="red")
            messagebox.showerror("Input Error","Please enter all the fields")
            return    



            
              
        elif not is_valid_number(height):
            frame_underline.config(bg="red")
            messagebox.showerror("Input Error","Invalid height entry. Only digits are allowed.")
            return
        
        elif not is_valid_number(weight):
            frame_underline2.config(bg="red")
            messagebox.showerror("Input Error","Invalid weight entry. Only digits are allowed.")
            return
        
        elif not is_valid_number(dnotchrad):
            frame_underline6.config(bg="red")
            messagebox.showerror("Input Error","Invalid radial distance. Only digits are allowed.")
            return
        
        elif not is_valid_number(dnotchank):
            frame_underline7.config(bg="red")
            messagebox.showerror("Input Error","Invalid ankle distance. Only digits are allowed.")
            return

        #         # Check if any of the parameters are empty strings
        # if not all([height,weight,smoke,drink,diabetes,diagnosis,symptoms,medications,dnotchrad,dnotchank]):
        #     messagebox.showerror("Empty values", "Please enter all the fields")
        #     return
        
        else:
            # messagebox.showinfo("success","patient added successfuly")
            import firebase_admin
            from firebase_admin import credentials, firestore


            data = {
                'hospitalId': cur_user['localId'],
                'name': name,
                'gender': gender,
                'email': email,
                'phone': phone,
                'dob': dob,
                'state': state,
                'city': city,
                'height': height,
                'weight': weight,
                'smoke':smoke,
                'alcohol': drink,
                'diabetes': diabetes,
                'medications': medications,
                'diagnosis': diagnosis,
                'symptoms': symptoms,
                'd_notch_rad': dnotchrad,
                'd_notch_ank': dnotchank
                }

            doc_ref = db.collection('patients').document()
            doc_ref.set(data)
            messagebox.showinfo("success","patient added successfuly")
            frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()


    def on_frame_configure(event):
        screen_height = root.winfo_height()
        screen_width = root.winfo_width()

        font_size = int(screen_width/ 120)
        font_size2 = int(screen_height/60)

        label_precog.config(font=("helvetica",font_size+16))
        btn_home.config(font=("helvetica",font_size2))
        label_add_patient.config(font=("helvetica",font_size+10))
        entry_height.config(font=("helvetica",font_size))
        entry_weight.config(font=("helvetica",font_size))
        label_smoke.config(font=("helvetica",font_size))
        # label_dob.config(font=("helvetica",font_size))
        smoke_dropdown.config(font=("helvetica",font_size))
        label_drink.config(font=("helvetica",font_size))
        drink_dropdown.config(font=("helvetica",font_size))
        label_diabetes.config(font=("helvetica",font_size))
        diabetes_dropdown.config(font=("helvetica",font_size))
        entry_diagnosis.config(font=("helvetica",font_size))
        entry_symptoms.config(font=("helvetica",font_size))
        entry_medications.config(font=("helvetica",font_size))
        entry_dNotchRad.config(font=("helvetica",font_size))
        entry_dNotchAnk.config(font=("helvetica",font_size))
        btn_add.config(font=("helvetica",font_size))

    def on_height_entry_click(event):
        if entry_height.get() == placeholder_height:
            entry_height.delete(0, tk.END)

    def on_height_focus_out(event):
        if not entry_height.get():
            entry_height.insert(0, placeholder_height)


    def on_weight_entry_click(event):
        if entry_weight.get() == placeholder_weight:
            entry_weight.delete(0, tk.END)

    def on_weight_focus_out(event):
        if not entry_weight.get():
            entry_weight.insert(0, placeholder_weight)


    def on_diagnosis_entry_click(event):
        if entry_diagnosis.get() == placeholder_diagnosis:
            entry_diagnosis.delete(0, tk.END)

    def on_diagnosis_focus_out(event):
        if not entry_diagnosis.get():
            entry_diagnosis.insert(0, placeholder_diagnosis)

    def on_symptoms_entry_click(event):
        if entry_symptoms.get() == placeholder_symptoms:
            entry_symptoms.delete(0, tk.END)

    def on_symptoms_focus_out(event):
        if not entry_symptoms.get():
            entry_symptoms.insert(0, placeholder_symptoms)

    def on_medications_entry_click(event):
        if entry_medications.get() == placeholder_medications:
            entry_medications.delete(0, tk.END)

    def on_medications_focus_out(event):
        if not entry_medications.get():
            entry_medications.insert(0, placeholder_medications)


    def on_dNotchRad_entry_click(event):
        if entry_dNotchRad.get() == placeholder_dNotchRad:
            entry_dNotchRad.delete(0, tk.END)

    def on_dNotchRad_focus_out(event):
        if not entry_dNotchRad.get():
            entry_dNotchRad.insert(0, placeholder_dNotchRad)

    def on_dNotchAnk_entry_click(event):
        if entry_dNotchAnk.get() == placeholder_dNotchAnk:
            entry_dNotchAnk.delete(0, tk.END)

    def on_dNotchAnk_focus_out(event):
        if not entry_dNotchAnk.get():
            entry_dNotchAnk.insert(0, placeholder_dNotchAnk)


    #main frames
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1, fill=BOTH , side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1, fill=BOTH , side=RIGHT)

    frame2_1 = Frame(frame2,bg="white")
    frame2_1.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="white")
    frame2_2.pack(expand=1, fill=BOTH, side=RIGHT,padx=(0,30))

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=1, fill=BOTH)

# ===============================================
    #header content 
    label_precog = Label(frame1_1,bg="white",text="PRECOG",fg="#2B318A")
    label_precog.pack(side=LEFT,pady=10,padx=10)

    btn_home = Button(frame1_2,bg="white",border=0,text="Home",fg="#2B318A",command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_home.pack(side=RIGHT,padx=10)



#    ================================================ 

    # left frame 
    frame2_1_inner = Frame(frame2_1,bg="#2B318A")
    frame2_1_inner.pack(expand=1,fill=BOTH,pady=10,padx=30)

    #inner sub frames

    frame_0_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_0_inner.pack(expand=0,fill=X,padx=30)

    frame_1_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_1_inner.pack(expand=0,padx=20)

    frame_2_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_2_inner.pack(expand=1,fill=BOTH,padx=30)

    # =======================

    #sub frames in 2
    frame_2_inner_1 = Frame(frame_2_inner,bg="#2B318A")
    frame_2_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))

    frame_2_inner_2 = Frame(frame_2_inner,bg="#2B318A")
    frame_2_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))
    # ======================

    frame_3_inner = Frame(frame2_1_inner,bg="#2B318A",height=2)
    frame_3_inner.pack(fill=X,expand=0,padx=30)

    # =============================
    #sub frames in 3
    frame_3_inner_1 = Frame(frame_3_inner,bg="#2B318A")
    frame_3_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))

    frame_3_inner_2 = Frame(frame_3_inner,bg="#2B318A")
    frame_3_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))

    #two sub frames in 3_1 and 3_2 respective

    frame_3_inner_1_1 = Frame(frame_3_inner_1,bg="#2B318A")
    frame_3_inner_1_1.pack(expand=1,fill=BOTH)

    frame_3_inner_1_2 = Frame(frame_3_inner_1,bg="white",height=2)
    frame_3_inner_1_2.pack(expand=0,fill=X)

    frame_3_inner_2_1 = Frame(frame_3_inner_2,bg="#2B318A")
    frame_3_inner_2_1.pack(expand=1,fill=BOTH)

    frame_3_inner_2_2 = Frame(frame_3_inner_2,bg="white",height=2)
    frame_3_inner_2_2.pack(expand=0,fill=X)

    # ===============================

    frame_4_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_4_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_5_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_5_inner.pack(expand=0,fill=X,padx=30)

    frame_6_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_6_inner.pack(expand=1,fill=BOTH,padx=30)
    
    frame_7_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_7_inner.pack(expand=0,fill=X,padx=30)

    frame_8_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_8_inner.pack(expand=1,fill=BOTH,padx=30)

    # =======================

    #sub frames in 2
    frame_8_inner_1 = Frame(frame_8_inner,bg="#2B318A")
    frame_8_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))
    

    frame_8_inner_2 = Frame(frame_8_inner,bg="#2B318A")
    frame_8_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))

    # ==================================

    frame_9_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_9_inner.pack(expand=1,fill=BOTH,padx=30)

    #sub frames in 2
    frame_9_inner_1 = Frame(frame_9_inner,bg="#2B318A")
    frame_9_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))
    

    frame_9_inner_2 = Frame(frame_9_inner,bg="#2B318A")
    frame_9_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))


    frame_10_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_10_inner.pack(expand=1,fill=BOTH,padx=30)

    # ======================================

    # fields on left frames

    btn_back = Button(frame_0_inner,bg="#2B318A",image=backbtnimagefinal,fg="white",border=0,command=lambda:(frame2_1.destroy(),frame2_2.destroy(),frame1_1.destroy(),frame1_2.destroy(),frame3_1.destroy(),going_back_primary_param(name,gender,dob,email,phone,state,city)))




    btn_back.pack(side=LEFT)

    label_add_patient = Label(frame_1_inner,text="ADD PATIENT",bg="#2B318A",fg="white")
    label_add_patient.pack(side=TOP,expand=1,fill=BOTH,anchor=N)  

    placeholder_height = "Height (cm)"
    entry_height = Entry(frame_2_inner_1,border=0,bg="#2B318A",fg="white")
    entry_height.pack(anchor=W,expand=0,fill=X)
    entry_height.insert(0, placeholder_height)
    entry_height.bind("<FocusIn>", on_height_entry_click)
    entry_height.bind("<FocusOut>", on_height_focus_out)

    frame_underline = Frame(frame_2_inner_1,height=2,bg="white")
    frame_underline.pack(anchor=N,expand=0,fill=X)

    placeholder_weight = "Weight (kg)"
    entry_weight = Entry(frame_2_inner_2,border=0,bg="#2B318A",fg="white")
    entry_weight.pack(anchor=W,expand=0,fill=X)
    entry_weight.insert(0, placeholder_weight)
    entry_weight.bind("<FocusIn>", on_weight_entry_click)
    entry_weight.bind("<FocusOut>", on_weight_focus_out)

    frame_underline2 = Frame(frame_2_inner_2,height=2,bg="white")
    frame_underline2.pack(anchor=N,expand=0,fill=X)

    label_smoke = Label(frame_3_inner_1_1,text="Do you smoke?",bg="#2B318A",fg="white")
    label_smoke.pack(side=LEFT,anchor=S)

    smoke_options = ["Yes","No"]
    smoke_var = tk.StringVar()
    smoke_dropdown = Combobox(frame_3_inner_1_1, textvariable=smoke_var, values=smoke_options,state="readonly")
    smoke_dropdown.pack(side=RIGHT,anchor=S)

    label_drink = Label(frame_3_inner_2_1,text="Do you drink?",bg="#2B318A",fg="white")
    label_drink.pack(side=LEFT,anchor=S)

    drink_options = ["Yes","No"]
    drink_var = tk.StringVar()
    drink_dropdown = Combobox(frame_3_inner_2_1, textvariable=drink_var, values=drink_options,state="readonly")
    drink_dropdown.pack(side=RIGHT,anchor=S)
 

    label_diabetes = Label(frame_4_inner,text="Do you have diabetes?",bg="#2B318A",fg="white")
    label_diabetes.pack(side=LEFT,anchor=S)

    diabetes_options = ["Yes","No"]
    diabetes_var = tk.StringVar()
    diabetes_dropdown = Combobox(frame_4_inner, textvariable=diabetes_var, values=diabetes_options,state="readonly")
    diabetes_dropdown.pack(side=RIGHT,anchor=S)


    placeholder_diagnosis = "Any previous diagnosis?"
    entry_diagnosis = Entry(frame_6_inner,bg="#2B318A",fg="white",border=0)
    entry_diagnosis.pack(anchor=S,side=LEFT,expand=1,fill=X)
    entry_diagnosis.insert(0, placeholder_diagnosis)
    entry_diagnosis.bind("<FocusIn>", on_diagnosis_entry_click)
    entry_diagnosis.bind("<FocusOut>", on_diagnosis_focus_out)


    frame_underline4= Frame(frame_8_inner_1,height=2,bg="white")
    frame_underline4.pack(side=BOTTOM,expand=0,fill=X)

    placeholder_symptoms = "Symptoms"
    entry_symptoms = Entry(frame_8_inner_1,bg="#2B318A",fg="white",border=0)
    entry_symptoms.pack(side=BOTTOM,anchor=W,expand=0,fill=X)
    entry_symptoms.insert(0, placeholder_symptoms)
    entry_symptoms.bind("<FocusIn>", on_symptoms_entry_click)
    entry_symptoms.bind("<FocusOut>", on_symptoms_focus_out)



    frame_underline5= Frame(frame_8_inner_2,height=2,bg="white")
    frame_underline5.pack(side=BOTTOM,expand=0,fill=X)

    placeholder_medications = "Medications"
    entry_medications = Entry(frame_8_inner_2,bg="#2B318A",fg="white",border=0)
    entry_medications.pack(side=BOTTOM,anchor=W,expand=0,fill=X)
    entry_medications.insert(0, placeholder_medications)
    entry_medications.bind("<FocusIn>", on_medications_entry_click)
    entry_medications.bind("<FocusOut>", on_medications_focus_out)




    frame_underline6= Frame(frame_9_inner_1,height=2,bg="white")
    frame_underline6.pack(side=BOTTOM,expand=0,fill=X,anchor=W)

    placeholder_dNotchRad = "radial distance"
    entry_dNotchRad = Entry(frame_9_inner_1,bg="#2B318A",fg="white",border=0)
    entry_dNotchRad.pack(side=BOTTOM,anchor=W,expand=0,fill=X)
    entry_dNotchRad.insert(0, placeholder_dNotchRad)    
    entry_dNotchRad.bind("<FocusIn>", on_dNotchRad_entry_click)
    entry_dNotchRad.bind("<FocusOut>", on_dNotchRad_focus_out)



    frame_underline7= Frame(frame_9_inner_2,height=2,bg="white")
    frame_underline7.pack(side=BOTTOM,expand=0,fill=X,anchor=W)

    placeholder_dNotchAnk = "ankle distance"
    entry_dNotchAnk = Entry(frame_9_inner_2,bg="#2B318A",fg="white",border=0)
    entry_dNotchAnk.pack(side=BOTTOM,anchor=W,expand=0,fill=X)
    entry_dNotchAnk.insert(0, placeholder_dNotchAnk) 
    entry_dNotchAnk.bind("<FocusIn>", on_dNotchAnk_entry_click)
    entry_dNotchAnk.bind("<FocusOut>", on_dNotchAnk_focus_out)
    




    btn_add = Button(frame_10_inner,image = addpatientbtnimgfinal,border=0,highlightthickness=0,bg="white",command=lambda:(patient_added(name,gender,dob,email,phone,state,city,entry_height.get(),entry_weight.get(),smoke_dropdown.get(),drink_dropdown.get(),diabetes_dropdown.get(),entry_diagnosis.get(),entry_symptoms.get(),entry_medications.get(),entry_dNotchRad.get(),entry_dNotchAnk.get())))
    btn_add.pack(side=BOTTOM)

    frame2_1_inner.bind("<Configure>", on_frame_configure)



    #btns on right
    btn1= Button(frame2_2,bg="white",image=btn1final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),recordNewTestSelected()))
    btn1.pack(expand=1,fill=BOTH)

    btn2= Button(frame2_2,bg="white",image=btn2SelectedFinal,border=0,command=lambda:())
    btn2.pack(expand=1,fill=BOTH)

    btn3= Button(frame2_2,bg="white",image=btn3final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),patientsSelected()))
    btn3.pack(expand=1,fill=BOTH)

    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Medical Systems",bg="white")
    label_footer.pack(pady=5)

# ========================================================= Add new patient =================================================================================
def addPatientSelected(): 
    def validate_primary_param(name, gender, dob, email, phone, state, city):


        # ==============================================================
       
        frame_3_inner.config(bg="white")
        frame_6_inner.config(bg="white")
        frame_8_inner.config(bg="white")
        frame_9_inner_2_2.config(bg="white")
        frame_4_inner_2_2.config(bg="white")
        frame_4_inner_1_2.config(bg="white")
        frame_9_inner_1_2.config(bg="white")

        if(name=="Name" or not name or email=="Email" or not email or phone=="Phone number" or not phone or city=="City"  or not city or not gender or not dob or not state):
            if(name=="Name" or not name):
                # entry_name.config(fg="red")
                frame_3_inner.config(bg="red")

            if(email=="Email id" or not email):
                # entry_email.config(fg="red")
                frame_6_inner.config(bg="red")

            if(phone=="Phone number" or not phone):
                # entry_phone.config(fg="red")
                frame_8_inner.config(bg="red")

            if(city=="City" or not city):
                # entry_city.config(fg="red") 
                frame_9_inner_2_2.config(bg="red")

            if(not gender):
                # label_gender.config(fg="red")
                frame_4_inner_1_2.config(bg="red")

            if(not dob):
                # label_dob.config(fg="red")
                frame_4_inner_2_2.config(bg="red")

            if(not state):
                # label_state.config(fg="red")
                frame_9_inner_1_2.config(bg="red")

            messagebox.showerror("Empty values", "Please enter all the fields")
            # addPatientSelected()
            return


        # elif not name or not gender or not dob or not email or not phone or not state or not city:
        #     messagebox.showerror("Incomplete Details", "Please enter complete details.")
        #     return 
        

        
        elif not validate_email(email):
            frame_6_inner.config(bg="red")
            messagebox.showerror("Signup Error", "Invalid email address.")
            return
        
        elif not validate_name(name):
            frame_3_inner.config(bg="red")
            messagebox.showerror("Signup Error", "Invalid name. Only letters are allowed.")
            return

        elif not validate_phone(phone):
            frame_8_inner.config(bg="red")
            messagebox.showerror("Signup Error", "Please enter a valid 10-digit phone number using only numeric characters (0-9).")
            return

        elif not validate_city(city):
            frame_9_inner_2_2.config(bg="red")
            messagebox.showerror("Signup Error","Invalid city. Only letters are allowed.")
            return
        
        else:
            frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy()
            secondary_param(name,gender,dob,email,phone,state,city)
        



    def on_name_entry_click(event):
        if entry_name.get() == placeholder_name:
            entry_name.delete(0, tk.END)

    def on_name_focus_out(event):
        if not entry_name.get():
            entry_name.insert(0, placeholder_name)


    def on_email_entry_click(event):
        if entry_email.get() == placeholder_email:
            entry_email.delete(0, tk.END)

    def on_email_focus_out(event):
        if not entry_email.get():
            entry_email.insert(0, placeholder_email)


    def on_phone_entry_click(event):
        if entry_phone.get() == placeholder_phone:
            entry_phone.delete(0, tk.END)

    def on_phone_focus_out(event):
        if not entry_phone.get():
            entry_phone.insert(0, placeholder_phone)


    def on_city_entry_click(event):
        if entry_city.get() == placeholder_city:
            entry_city.delete(0, tk.END)

    def on_city_focus_out(event):
        if not entry_city.get():
            entry_city.insert(0, placeholder_city)

    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)

        label_precog.config(font=("helvetica",font_size+14))
        btn_home.config(font=("helvetica",font_size))

        label_add_patient.config(font=("helvetica",font_size+14))
        entry_name.config(font=("helvetica",font_size))
        label_gender.config(font=("helvetica",font_size))
        gender_dropdown.config(font=("helvetica",font_size))
        label_dob.config(font=("helvetica",font_size))
        dob_entry.config(font=("helvetica",font_size))
        entry_email.config(font=("helvetica",font_size))
        entry_phone.config(font=("helvetica",font_size))
        label_state.config(font=("helvetica",font_size))
        state_dropdown.config(font=("helvetica",font_size))
        entry_city.config(font=("helvetica",font_size))
        btn_next.config(font=("helvetica",font_size))
        # label_precog.config(font=("helvetica",font_size+20))
        # btn_help_support.config(font=("helvetica",font_size))

    #main frames
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1, fill=BOTH , side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1, fill=BOTH , side=RIGHT)

    frame2_1 = Frame(frame2,bg="white")
    frame2_1.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="white")
    frame2_2.pack(expand=1, fill=BOTH, side=RIGHT)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=1, fill=BOTH)

# ===============================================
    # header content 
    label_precog = Label(frame1_1,bg="white",text="PRECOG",fg="#2B318A")
    label_precog.pack(side=LEFT,pady=10,padx=10)

    btn_home = Button(frame1_2,bg="white",border=0,text="Home",fg="#2B318A",command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_home.pack(side=RIGHT,padx=10)


#     btn_help_support = Button(frame1_2,bg="white",border=0,underline=1,text="Help & Support",fg="#2B318A")
#     btn_help_support.pack(side=RIGHT)

# # ============================
    # left frame 
    frame2_1_inner = Frame(frame2_1,bg="#2B318A")
    frame2_1_inner.pack(expand=1,fill=BOTH,pady=10,padx=30)


    #inner sub frames
    frame_0_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_0_inner.pack(expand=1,fill=BOTH,padx=30)   

    frame_1_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_1_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_2_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_2_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_3_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_3_inner.pack(fill=X,expand=0,padx=30)

    frame_4_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_4_inner.pack(expand=1,fill=BOTH,padx=30)

# # ================
    #sub frames in 4 
    frame_4_inner_1 = Frame(frame_4_inner,bg="#2B318A")
    frame_4_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))

    frame_4_inner_2 = Frame(frame_4_inner,bg="#2B318A")
    frame_4_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))

    #two sub frames in 4_1 and 4_2 respective

    frame_4_inner_1_1 = Frame(frame_4_inner_1,bg="#2B318A")
    frame_4_inner_1_1.pack(expand=1,fill=BOTH)

    frame_4_inner_1_2 = Frame(frame_4_inner_1,bg="white",height=2)
    frame_4_inner_1_2.pack(expand=0,fill=X)

    frame_4_inner_2_1 = Frame(frame_4_inner_2,bg="#2B318A")
    frame_4_inner_2_1.pack(expand=1,fill=BOTH)

    frame_4_inner_2_2 = Frame(frame_4_inner_2,bg="white",height=2)
    frame_4_inner_2_2.pack(expand=0,fill=X)

# # ================


    frame_5_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_5_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_6_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_6_inner.pack(fill=X,padx=30)
    
    frame_7_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_7_inner.pack(expand=1,fill=BOTH,padx=30)

    frame_8_inner = Frame(frame2_1_inner,bg="white",height=2)
    frame_8_inner.pack(fill=X,padx=30)

    frame_9_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_9_inner.pack(expand=1,fill=BOTH,padx=30)

    # ================
    #sub frames in 9 
    frame_9_inner_1 = Frame(frame_9_inner,bg="#2B318A")
    frame_9_inner_1.pack(side=LEFT,expand=1,fill=BOTH,padx=(0,10))

    frame_9_inner_2 = Frame(frame_9_inner,bg="#2B318A")
    frame_9_inner_2.pack(side=RIGHT,expand=1,fill=BOTH,padx=(10,0))


    #two sub frames in 9_1 and 9_2 respective

    frame_9_inner_1_1 = Frame(frame_9_inner_1,bg="#2B318A")
    frame_9_inner_1_1.pack(expand=1,fill=BOTH)

    frame_9_inner_1_2 = Frame(frame_9_inner_1,bg="white",height=2)
    frame_9_inner_1_2.pack(expand=0,fill=X)

    frame_9_inner_2_1 = Frame(frame_9_inner_2,bg="#2B318A")
    frame_9_inner_2_1.pack(expand=1,fill=BOTH)

    frame_9_inner_2_2 = Frame(frame_9_inner_2,bg="white",height=2)
    frame_9_inner_2_2.pack(expand=0,fill=X)

    # ================

    frame_10_inner = Frame(frame2_1_inner,bg="#2B318A")
    frame_10_inner.pack(expand=1,fill=BOTH,padx=30)

# # ============================
#     # fields on left frames


    # custom_font = tkFont.Font(underline=True)
    btn_back = Button(frame_0_inner,bg="#2B318A",image=backbtnimagefinal,fg="white",border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_back.pack(side=LEFT)

    label_add_patient = Label(frame_1_inner,text="ADD PATIENT",bg="#2B318A",fg="white")
    label_add_patient.pack(expand=1,fill=BOTH)

    placeholder_name = "Name"
    entry_name = Entry(frame_2_inner,border=0,bg="#2B318A",fg="white")
    entry_name.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_name.insert(0, placeholder_name)
    entry_name.bind("<FocusIn>", on_name_entry_click)
    entry_name.bind("<FocusOut>", on_name_focus_out)

    label_gender = Label(frame_4_inner_1_1,text="Gender",bg="#2B318A",fg="white")
    label_gender.pack(side=LEFT,anchor=S)

    gender_options = ["Male","Female","Other"]
    gender_var = tk.StringVar()
    gender_dropdown = Combobox(frame_4_inner_1_1, textvariable=gender_var, values=gender_options,state="readonly")
    gender_dropdown.pack(side=RIGHT,anchor=S)

    label_dob = Label(frame_4_inner_2_1,text="DOB",bg="#2B318A",fg="white")
    label_dob.pack(side=LEFT,anchor=S)



    dob_var = tk.StringVar()
    dob_entry = DateEntry(frame_4_inner_2_1, textvariable=dob_var, date_pattern='dd/mm/yyyy', showweeknumbers=False, selectbackground="#2B318A")
    dob_entry.pack(side=RIGHT,anchor=S)

    entry_email= Entry(frame_5_inner,border=0,bg="#2B318A",fg="white")
    entry_email.pack(side=LEFT,anchor=S,expand=1,fill=X)
    placeholder_email= "Email id"
    entry_email.insert(0, placeholder_email)
    entry_email.bind("<FocusIn>", on_email_entry_click)
    entry_email.bind("<FocusOut>", on_email_focus_out)

    entry_phone = Entry(frame_7_inner,bg="#2B318A",border=0,fg="white")
    entry_phone.pack(side=LEFT,anchor=S,expand=1,fill=X)
    placeholder_phone = "Phone number"
    entry_phone.insert(0, placeholder_phone)
    entry_phone.bind("<FocusIn>", on_phone_entry_click)
    entry_phone.bind("<FocusOut>", on_phone_focus_out)

    label_state = Label(frame_9_inner_1_1,text="State",bg="#2B318A",fg="white")
    label_state.pack(side=LEFT,anchor=S)

    state_options = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
        "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    state_var = tk.StringVar()
    state_dropdown = Combobox(frame_9_inner_1_1, textvariable=state_var, values=state_options,state="readonly")
    state_dropdown.pack(side=RIGHT,anchor=S)

    entry_city = Entry(frame_9_inner_2_1,border=0,bg="#2B318A",fg="white")
    entry_city.pack(side=LEFT,anchor=S,expand=1,fill=X)
    placeholder_city = "City"
    entry_city.insert(0, placeholder_city)
    entry_city.bind("<FocusIn>", on_city_entry_click)
    entry_city.bind("<FocusOut>", on_city_focus_out)

    def hit_enter(event):
        validate_primary_param(entry_name.get(), gender_dropdown.get(), dob_entry.get(),entry_email.get(), entry_phone.get(), state_dropdown.get(), entry_city.get()) 

    btn_next = Button(frame_10_inner,image=nextbtnimgfinal,border=0,highlightthickness=0,fg="blue",command=lambda:(validate_primary_param(entry_name.get(), gender_dropdown.get(), dob_entry.get(),entry_email.get(), entry_phone.get(), state_dropdown.get(), entry_city.get())))
    btn_next.pack(side=BOTTOM,pady=20)
    root.bind("<Return>", hit_enter)
    frame2_1_inner.bind("<Configure>", on_frame_configure)



# # ============================

    #btns on right
    btn1= Button(frame2_2,bg="white",image=btn1final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),recordNewTestSelected()))
    btn1.pack(expand=1,fill=BOTH)

    btn2= Button(frame2_2,bg="white",image=btn2SelectedFinal,border=0,command=lambda:())
    btn2.pack(expand=1,fill=BOTH)

    btn3= Button(frame2_2,bg="white",image=btn3final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),patientsSelected()))
    btn3.pack(expand=1,fill=BOTH)


    #footer content
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)


def update_users(runthis):

    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        # patient_name_dropdown.config(font=("helvetica",font_size))
        gif_label2.config(font=("helvetica",font_size+10))

    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(side=LEFT,anchor=W) 

    img_label = Label(frame1_1, image=original_img,bg="white")
    img_label.pack(side=LEFT,pady=10,padx=10)   

    frame2_1 = Frame(frame2,bg="#CDDDFF")
    frame2_1.pack(expand=1,fill=BOTH)

    frame_loading = Frame(frame2,bg="#CDDDFF")
    frame_loading.pack(expand=1,fill=BOTH)
    frame_loading.bind("<Configure>", on_frame_configure)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack()

    footer_label = Label(frame3_1,text="Copyright 2024 Acuradyne Systems",bg="white",fg="black")
    footer_label.pack()

    # Load GIF frames
    gif_frames = [loadingAni1final2,loadingAni2final2,loadingAni3final2,loadingAni4final2]


    # Function to update GIF
    def update_gif(frame_number):
        gif_label.config(image=gif_frames[frame_number])
        frame_number = (frame_number + 1) % len(gif_frames)
        gif_label.after(500, update_gif, frame_number)  # Change delay (ms) as needed

    gif_label = Label(frame2_1,image="",bg="#CDDDFF")
    gif_label.pack(side=BOTTOM ,anchor=S)

    gif_label2 = Label(frame_loading,text="Loading content. Please wait...",bg="#CDDDFF",fg="#2B318A")
    gif_label2.pack(side=TOP,anchor=N)


    # Start GIF animation
    update_gif(0)


    # ===============================patients module ==============
    def fetchingData():

        global patient_data,patient_data2,patient_list,patient_list2

        patients_ref = db.collection('patients')

        patient_data = []
        patient_data2 = []

        patient_list = []
        patient_list2 = []


        patients = patients_ref.stream()

        for patient in patients:
            # Assuming the 'name' field exists in each patient document
            name = patient.to_dict().get('name')
            hospitalid= patient.to_dict().get('hospitalId')  # Retrieve the unique ID of the document


            if hospitalid == cur_user['localId']:
                hospital_ref = db.collection('hospitals').document(hospitalid)
                phone =  patient.to_dict().get('phone')
                email = patient.to_dict().get('email')
                height = patient.to_dict().get('height')
                gender = patient.to_dict().get('gender')
                weight = patient.to_dict().get('weight')
                dob = patient.to_dict().get('dob')
                
                ank = patient.to_dict().get('d_notch_ank')
                rad = patient.to_dict().get('d_notch_rad')
                uid = patient.id


                # Get the document data
                doc_snapshot = hospital_ref.get()
                hospitalName = doc_snapshot.to_dict().get('name')

                patient_data2.append(f"{name},{phone}")
                patient_data.append(f"{name},{phone},{hospitalid},{email},{height},{weight},{gender},{dob},{hospitalName}")

                patient_list.append(f"{name}, {phone}")
                patient_list2.append(f"{name}, {phone},{hospitalid},{ank},{rad},{height},{uid},{weight},{gender},{hospitalName},{dob}")



        # Sort patient data alphabetically by name
        patient_data2.sort(key=lambda x: x[0])
        patient_data.sort(key=lambda x: x[0])
        patient_list.sort()
        patient_list2.sort()


        # ==============================================



    
        frame1_1.destroy()
        frame3_1.destroy()
        frame2_1.destroy()
        frame_loading.destroy()
        runthis()
        

    
                # Start other tasks in a separate thread
    thread = threading.Thread(target=fetchingData)
    thread.start()

# =============================================================== Record new test logic ===========================================================================
def recordNewTestSelected():

    global selected_name, name_onselect,ank_onselect,dob_onselect,ank_onselect,rad_onselect,height_onselect,uid_onselect,phone_onselect,hospital_onselect,hospitalName_onselect,gender_onselect,weight_onselect
    name_onselect=""
    phone_onselect=""
    hospital_onselect=""
    ank_onselect=""
    rad_onselect=""
    height_onselect=""
    uid_onselect=""
    dob_onselect=""
    hospitalName_onselect= ""
    gender_onselect= ""
    weight_onselect=""


        

    def open_recording_window(patient_name,no_of_sensors,dob,hospitalName,gender,height,weight,ank,rad,uid):  
        if(patient_name==""):
            messagebox.showerror("Name error","Please select a patient")

        else:
            if(no_of_sensors=="1"):
                frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy()
                singleSensorApp = SingleSensorLogic(root,patient_name,no_of_sensors,dob,hospitalName,gender,height,weight,ank,rad,uid)
               
            elif(no_of_sensors=="2"):
                frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy()
                doubleSensorApp = DoubleSensorLogic(root,patient_name,no_of_sensors,dob,hospitalName,gender,height,weight,ank,rad,uid)

            elif(no_of_sensors=="3"):
                frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy()
                tripleSensorApp = TripleSensorLogic(root,patient_name,no_of_sensors,dob,hospitalName,gender,height,weight,ank,rad,uid)

    
    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        # patient_name_dropdown.config(font=("helvetica",font_size))
        entry_name.config(font=("helvetica",font_size))
        listbox.config(font=("helvetica",font_size))
        # sensor_var.config(font=("helvetica",font_size))
        option1.config(font=("helvetica",font_size+10))
        option2.config(font=("helvetica",font_size+10))
        option3.config(font=("helvetica",font_size+10))
        label_precog.config(font=("helvetica",font_size+14))
        btn_home.config(font=("helvetica",font_size))
        label_newtest.config(font=("helvetica",font_size+14))
        label_noofsensors.config(font=("helvetica",font_size))
        label_nameofpatient.config(font=("helvetica",font_size))
        btn_take_recording.config(font=("helvetica",font_size))
        frame5_record.config(pady=(font_size+20))
        btn_home.config(font=("helvetica",font_size))
        btn_refresh.config(font=("helvetica",font_size))





    #main frames
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1, fill=BOTH , side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1, fill=BOTH , side=RIGHT)

    frame2_1 = Frame(frame2,bg="white")
    frame2_1.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="white")
    frame2_2.pack(expand=1, fill=BOTH, side=RIGHT)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=1, fill=BOTH)

# ===============================================
    #header content 
    label_precog = Label(frame1_1,bg="white",text="PRECOG",fg="#2B318A")
    label_precog.pack(side=LEFT,pady=10,padx=10)

    btn_home = Button(frame1_2,bg="white",border=0,text="Home",fg="#2B318A",command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_home.pack(side=RIGHT,padx=10)

# ====================================
    
#form on left side 
    
    frame2_1_1 = Frame(frame2_1,bg="#2B318A") #this is the main frame on left
    frame2_1_1.pack(expand=1,fill=BOTH,pady=40,padx=40)


    #sub frames inside this frame

    frame0_record_back = Frame(frame2_1_1,bg="#2B318A")
    frame0_record_back.pack(expand=1,fill=BOTH,padx=20)

    frame1_record = Frame(frame2_1_1,bg="#2B318A")
    frame1_record.pack(expand=1,fill=BOTH,padx=20)

    frame2_record = Frame(frame2_1_1)
    frame2_record.pack(expand=1,fill=BOTH,padx=20)

    frame2_1_record = Frame(frame2_record,bg="#2B318A")
    frame2_1_record.pack(side=LEFT,expand=1,fill=BOTH)

    frame2_2_record = Frame(frame2_record,bg="#2B318A")
    frame2_2_record.pack(side=RIGHT,expand=1,fill=BOTH)


    frame3_record = Frame(frame2_1_1)
    frame3_record.pack(expand=1,fill=BOTH,padx=20)

    frame3_1_record = Frame(frame3_record,bg="#2B318A")
    frame3_1_record.pack(side=LEFT,expand=1,fill=BOTH)

    frame3_2_record = Frame(frame3_record,bg="#2B318A")
    frame3_2_record.pack(side=RIGHT,expand=1,fill=BOTH)

    frame4_record = Frame(frame2_1_1,bg="white",height=2)
    frame4_record.pack(expand=0,fill=X,anchor=N,padx=20)

    frame5_record = Frame(frame2_1_1,bg="#2B318A")
    frame5_record.pack(expand=1,fill=BOTH,padx=20)

    # ================================

    # custom_font = tkFont.Font(underline=True)

    btn_back = Button(frame0_record_back,bg="#2B318A",image=backbtnimagefinal,fg="white",border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),Modules()))
    btn_back.pack(side=LEFT)

    btn_refresh= Button(frame0_record_back,bg="#2B318A",text="refresh",fg="white",border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),update_users(recordNewTestSelected)))
    btn_refresh.pack(side=RIGHT)

    label_newtest = Label(frame1_record,text="NEW TEST",bg="#2B318A",fg="white")
    label_newtest.pack(side=TOP)

    # ================================



    label_nameofpatient = Label(frame2_1_record,text="Name of the patient",bg="#2B318A",fg="white")
    label_nameofpatient.pack(side=LEFT,anchor=N) 
    


    def update_listbox(*args):
        global selected_name
        filter_text = entry_var.get().lower()
        listbox.delete(0, tk.END)  # Clear previous items
        filtered_patients = [patient for patient in patient_list if patient.lower().startswith(filter_text)]
        for patient in filtered_patients:
            listbox.insert(tk.END, patient)

    def on_select(event):
        global selected_name, name_onselect,ank_onselect,ank_onselect,rad_onselect,height_onselect,uid_onselect,phone_onselect,hospital_onselect,dob_onselect,hospitalName_onselect,gender_onselect,weight_onselect

        selected_index = listbox.curselection()
        if selected_index:
            selected_data = listbox.get(selected_index)
            # Iterate over patient_list2 to find the element that starts with the selected data                {name}, {phone},  {hospitalid},   {ank},  {rad},  {height}  ,{uid},{  weight},    {gender}    ,{hospitalName},    {dob}
            for patient_data in patient_list2:
                if patient_data.startswith(selected_data):
                    data_here = patient_data.split(',')  
                    name_onselect = data_here[0]
                    phone_onselect = data_here[1]
                    hospital_onselect = data_here[2]
                    ank_onselect = data_here[3]
                    rad_onselect = data_here[4]
                    height_onselect = data_here[5]
                    uid_onselect = data_here[6]
                    weight_onselect = data_here[7]
                    gender_onselect = data_here[8]
                    hospitalName_onselect = data_here[9]
                    dob_onselect = data_here[10]

                    
            print("Selected Patient:", name_onselect)

    # root = tk.Tk()
    # root.title("Patient Selection")

    # patients = ["Patient {}".format(i) for i in range(1, 1001)]  # Example list of patient names

    entry_var = tk.StringVar()
    entry_var.trace_add('write', update_listbox)

    label_search_icon = Label(frame2_2_record,image=searchiconimgfinal,bg="#2B318A")
    label_search_icon.pack(side=RIGHT,anchor=N,expand=0)
    

    entry_name = ttk.Entry(frame2_2_record, textvariable=entry_var)
    entry_name.pack(side=TOP,anchor=E)

    listbox = tk.Listbox(frame2_2_record, selectmode=tk.SINGLE)
    listbox.pack(side=BOTTOM,anchor=E, fill=tk.BOTH, expand=True)
    

    update_listbox()  # Update listbox initially

    

    # patient_name_dropdown.pack(side=RIGHT,anchor=S)
    # patient_name_dropdown.bind('<KeyRelease>', updatePatientList)


    label_noofsensors = Label(frame3_1_record,text="Number of sensors attached",bg="#2B318A",fg="white")
    label_noofsensors.pack(side=LEFT,anchor=S)

    # sensors_options = ["1", "2", "3"]
    sensor_var = tk.StringVar()
    sensor_var.set("1")

    # Create radio buttons
    option1 = tk.Radiobutton(frame3_2_record, text="1", variable=sensor_var, value="1",bg="#2B318A",fg="white",selectcolor="black")
    option2 = tk.Radiobutton(frame3_2_record, text="2", variable=sensor_var, value="2",bg="#2B318A",fg="lightgrey",selectcolor="black")
    option3 = tk.Radiobutton(frame3_2_record, text="3", variable=sensor_var, value="3",bg="#2B318A",fg="lightgrey",selectcolor="black")

    # Place the radio buttons in the window

    option3.pack(anchor=S,side=RIGHT)
    option2.pack(anchor=S,side=RIGHT)
    option1.pack(anchor=S,side=RIGHT)                                            

    # patient_name = patient_name_dropdown.get()
    btn_take_recording = Button(frame5_record,image=nextbtnimgfinal,border=0,highlightthickness=0,command=lambda:(open_recording_window(name_onselect,sensor_var.get(),dob_onselect,hospitalName_onselect,gender_onselect,height_onselect,weight_onselect,ank_onselect,rad_onselect,uid_onselect)),bg="#DCE7FF",fg="#464DB6")
    btn_take_recording.pack(side=BOTTOM)


# ============================

    #btns on right
    btn1= Button(frame2_2,bg="white",image=btn1SelectedFinal,border=0,command=lambda:())
    btn1.pack(expand=1,fill=BOTH)

    btn2= Button(frame2_2,bg="white",image=btn2final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),addPatientSelected()))
    btn2.pack(expand=1,fill=BOTH)

    btn3= Button(frame2_2,bg="white",image=btn3final,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),patientsSelected()))
    btn3.pack(expand=1,fill=BOTH)


    #footer content
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

 # Bind the configure event to the frame
    
    frame2_1_1.bind("<Configure>", on_frame_configure)
    listbox.bind("<<ListboxSelect>>", on_select)

# ================================================================== All modules ==========================================================================

def Modules():

    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        label_precog.config(font=("Barlow",font_size+14))
        # btn_help_support.config(font=("helvetica",font_size))
    # ===============================================
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1, fill=BOTH , side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1, fill=BOTH , side=RIGHT)

    frame2_main = Frame(frame2,bg="white")
    frame2_main.pack(expand=1,fill=BOTH)
    
    frame2_1 = Frame(frame2_main,bg="white")
    frame2_1.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2_main,bg="white")
    frame2_2.pack(expand=1, fill=BOTH, side=RIGHT)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack(expand=1, fill=BOTH)

    # ===============================================


    #header content 
    label_precog = Label(frame1_1,bg="white",text="PRECOG",fg="#2B318A")
    label_precog.pack(side=LEFT,pady=10,padx=10)

    # btn_help_support = Button(frame1_2,bg="white",border=0,underline=1,text="Help & Support",fg="#2B318A")
    # btn_help_support.pack(side=RIGHT)

    #img 
    img_label = tk.Label(frame2_1, image=image2final ,bg="white")
    img_label.pack(expand=1,fill=BOTH)

    #btns on right
    btn1= Button(frame2_2,bg="white",image=btn1final,border=0,activebackground="white",command=lambda:(recordNewTestSelected(),frame3_1.destroy(),frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame2_main.destroy()))
    btn1.pack(expand=1,fill=BOTH)

    btn2= Button(frame2_2,bg="white",image=btn2final,border=0,activebackground="white",command=lambda:(addPatientSelected(),frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame2_main.destroy(),frame3_1.destroy()))
    btn2.pack(expand=1,fill=BOTH)

    btn3= Button(frame2_2,bg="white",image=btn3final,border=0,activebackground="white",command=lambda:(loadingScreen(patientsSelected),frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame2_main.destroy(),frame3_1.destroy()))
    btn3.pack(expand=1,fill=BOTH)


    #footer content
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

    # frame2_main.bind()
    frame2_main.bind("<Configure>", on_frame_configure)

# # =============================================================    Register frame logic here ===========================================================

# def registerFrameLogic():
#     # firebaseConfig = {
#     #     'apiKey': "AIzaSyAc0lGU3SkNpq_3im9HXBDeEIfz9sE6OYs",
#     #     'authDomain': "arterypulseanalyzer.firebaseapp.com",
#     #     'databaseURL': "https://arterypulseanalyzer.firebaseio.com",
#     #     'projectId': "arterypulseanalyzer",
#     #     'storageBucket': "arterypulseanalyzer.appspot.com",
#     #     'messagingSenderId': "367434956236",
#     #     'appId': "1:367434956236:web:30f044b0c21dffd5ecb169"
#     # }
#     # firebase = pyrebase.initialize_app(firebaseConfig)
#     # auth = firebase.auth()


#     def on_name_entry_click(event):
#     # """Function to clear the placeholder text when the entry is clicked."""
#         if entry_for_name.get() == placeholder_name:
#             entry_for_name.delete(0, tk.END)
#             entry_for_name.config(fg='black')  # Change text color to black

#     def on_name_focus_out(event):
#         # """Function to restore the placeholder text if the entry is left empty."""
#         if not entry_for_name.get():
#             entry_for_name.insert(0, placeholder_name)
#             entry_for_name.config(fg='grey')  # Change text color to grey

#     def on_email_entry_click(event):
#     # """Function to clear the placeholder text when the entry is clicked."""
#         if entry_for_email.get() == placeholder_email:
#             entry_for_email.delete(0, tk.END)
#             entry_for_email.config(fg='black')  # Change text color to black

#     def on_email_focus_out(event):
#         # """Function to restore the placeholder text if the entry is left empty."""
#         if not entry_for_email.get():
#             entry_for_email.insert(0, placeholder_email)
#             entry_for_email.config(fg='grey')  # Change text color to grey

#     def on_password_entry_click(event):
#     # """Function to clear the placeholder text when the entry is clicked."""
#         if entry_for_password.get() == placeholder_password:
#             entry_for_password.delete(0, tk.END)
#             entry_for_password.config(fg='black',show="*")  # Change text color to black

#     def on_password_focus_out(event):
#         # """Function to restore the placeholder text if the entry is left empty."""
#         if not entry_for_password.get():
#             entry_for_password.insert(0, placeholder_password)
#             entry_for_password.config(fg='grey',show="")  # Change text color to grey

#     def on_confirmpassword_entry_click(event):
#     # """Function to clear the placeholder text when the entry is clicked."""
#         if entry_for_confirmpassword.get() == placeholder_confirmpassword:
#             entry_for_confirmpassword.delete(0, tk.END)
#             entry_for_confirmpassword.config(fg='black',show="*")  # Change text color to black

#     def on_confirmpassword_focus_out(event):
#         # """Function to restore the placeholder text if the entry is left empty."""
#         if not entry_for_confirmpassword.get():
#             entry_for_confirmpassword.insert(0, placeholder_confirmpassword)
#             entry_for_confirmpassword.config(fg='grey',show="")  # Change text color to grey

#     def on_frame_configure(event):
#         screen_width = root.winfo_width()
#         font_size = int(screen_width / 100)
#         entry_for_email.config(font=("arial",font_size))
#         entry_for_name.config(font=("arial",font_size))
#         entry_for_password.config(font=("arial",font_size))
#         entry_for_confirmpassword.config(font=("arial",font_size))
#         label_Register.config(font=("arial",font_size+20))
#         return font_size


#     def createUser(email, password,confirmpassword,name):
#         if(password==confirmpassword):
#             try:
#                 auth.create_user_with_email_and_password(email, password)
#                 messagebox.showinfo("Signup", "Account created successfully!")
#                 frame1_2.destroy(),frame1_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),landingWindow()
           

#             except:
#                 messagebox.showerror("Signup Error", "Error creating account")

#         else:
#             messagebox.showerror("Password error", "Password and confirm password must be same")




#     # ============================================================

#     # sub frames in main 3 frames
#     frame1_1 = Frame(frame1,bg="white")
#     frame1_1.pack(expand=1,fill=BOTH,side=LEFT)

#     frame1_2 = Frame(frame1,bg="white")
#     frame1_2.pack(expand=1,fill=BOTH,side=RIGHT)


#     #frames inside frame2
#     frameRegister = Frame(frame2, bg="white")
#     frameRegister.pack(expand=1, fill=BOTH, side=LEFT)

#     frame2_2 = Frame(frame2,bg="white")
#     frame2_2.pack(side=RIGHT,expand=1,fill=BOTH)

#     frame3_1 = Frame(frame3,bg="white")
#     frame3_1.pack()
    

#     # ======================== other frames ========================
   

#     frameRegister2 = Frame(frameRegister,bg="white")
#     frameRegister2.pack(expand=1,fill=BOTH,padx=40,pady=10)

#     # # Bind the configure event to the frame
#     frameRegister2.bind("<Configure>", on_frame_configure)

#     frame1_register = Frame(frameRegister2,bg="white")
#     frame1_register.pack(expand=1,fill=BOTH)

#     frame2_register = Frame(frameRegister2,bg="white")
#     frame2_register.pack(expand=1,fill=BOTH)

#     frame3_register = Frame(frameRegister2,bg="black",height=2)
#     frame3_register.pack(expand=0, fill=X)

#     frame4_register = Frame(frameRegister2,bg="white")
#     frame4_register.pack(expand=1, fill=BOTH)

#     frame5_register = Frame(frameRegister2,bg="black",height=2)
#     frame5_register.pack(expand=0, fill=X)

#     frame6_register = Frame(frameRegister2,bg="white")
#     frame6_register.pack(expand=1, fill=BOTH)

#     #sub frames in frame 6 
#     frame6_1_register = Frame(frame6_register,bg="white")
#     frame6_1_register.pack(expand=1, fill=BOTH,side=LEFT)

#     frame6_2_register = Frame(frame6_register,bg="white")
#     frame6_2_register.pack(expand=1, fill=BOTH,side=RIGHT)

#     #two sub frames again 

#     frame6_1_1_register = Frame(frame6_1_register,bg="white")
#     frame6_1_1_register.pack(expand=1, fill=BOTH,side=TOP)

#     frame6_1_2_register = Frame(frame6_1_register,bg="black",height=2)
#     frame6_1_2_register.pack(expand=1, fill=X,side=BOTTOM,anchor=N)

#     #two sub frames 

#     frame6_2_1_register = Frame(frame6_2_register,bg="white")
#     frame6_2_1_register.pack(expand=1, fill=BOTH,side=TOP)

#     frame6_2_2_register = Frame(frame6_2_register,bg="black",height=2)
#     frame6_2_2_register.pack(expand=1, fill=X,side=BOTTOM,anchor=N)

#     #regular frames

#     frame7_register = Frame(frameRegister2,bg="white")
#     frame7_register.pack(expand=1, fill=BOTH)

#     frame8_register = Frame(frameRegister2,bg="white")
#     frame8_register.pack(expand=1,fill=BOTH)


    
# # ============================================================
    


#     # Create a Label widget to display the resized image at top left
#     img_label = tk.Label(frame1_1, image=original_img,bg="white")
#     img_label.pack(side=LEFT,pady=10,padx=10)


#     # custom_font = tkFont.Font(underline=True)

#     #register button at top right 
#     btn_login = Button(frame1_2,bg="white",image=loginbtnimgdarkfinal,border=0,highlightthickness=0,fg="darkblue",command=lambda:(frame1_2.destroy(),frame1_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),frameRegister.destroy(),loginFrameLogic()))
#     btn_login.pack(side=RIGHT,pady=10,padx=10)
 
    

#     label_Register = Label(frame1_register,text="REGISTRATION FORM",fg="#464DB6",bg="white")
#     label_Register.pack(side=BOTTOM)

  

#     placeholder_name = "Name"
#     entry_for_name = Entry(frame2_register,border=0)
#     entry_for_name.pack(side=LEFT,anchor=S)
#     entry_for_name.insert(0, placeholder_name)
#     entry_for_name.bind("<FocusIn>", on_name_entry_click)
#     entry_for_name.bind("<FocusOut>", on_name_focus_out)


#     placeholder_email = "Email id"
#     entry_for_email = Entry(frame4_register,border=0)
#     entry_for_email.pack(side=LEFT,anchor=S)
#     entry_for_email.insert(0, placeholder_email)
#     entry_for_email.bind("<FocusIn>", on_email_entry_click)
#     entry_for_email.bind("<FocusOut>", on_email_focus_out)

#     placeholder_password = "Password"
#     entry_for_password = Entry(frame6_1_1_register,border=0)
#     entry_for_password.pack(side=LEFT,anchor=S)
#     entry_for_password.insert(0, placeholder_password)
#     entry_for_password.bind("<FocusIn>", on_password_entry_click)
#     entry_for_password.bind("<FocusOut>", on_password_focus_out)

#     placeholder_confirmpassword = "Confirm password"
#     entry_for_confirmpassword = Entry(frame6_2_1_register,border=0)
#     entry_for_confirmpassword.pack(side=LEFT,anchor=S)
#     entry_for_confirmpassword.insert(0, placeholder_confirmpassword)
#     entry_for_confirmpassword.bind("<FocusIn>", on_confirmpassword_entry_click)
#     entry_for_confirmpassword.bind("<FocusOut>", on_confirmpassword_focus_out)

  

#     btn_register = Button(frame7_register,image=registerbtnimgfinal,border=0,highlightthickness=0,bg="#464DB6",fg="white",font=("arial",14),command=lambda:(createUser(entry_for_email.get(),entry_for_password.get(),entry_for_confirmpassword.get(),entry_for_name.get())))
#     btn_register.pack(side=BOTTOM)

    
#     #image in frame2_2
#     landingpage_img_label = Label(frame2_2,image=landing_image1,bg="#CDDDFF")
#     landingpage_img_label.pack(expand=1,fill=BOTH)

#      #bottom footer 
#     label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
#     label_footer.pack(pady=16)

# ===========================================================      Login frame logic here   ========================================================

def loginFrameLogic():
    def on_email_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_email.get() == placeholder_email:
            entry_for_email.delete(0, tk.END)
            entry_for_email.config(fg='black')  # Change text color to black

    def on_email_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_email.get():
            entry_for_email.insert(0, placeholder_email)
            entry_for_email.config(fg='grey')  # Change text color to grey

    def on_password_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_password.get() == placeholder_password:
            entry_for_password.delete(0, tk.END)
            entry_for_password.config(fg='black',show="*")  # Change text color to black

    def on_password_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_password.get():
            entry_for_password.insert(0, placeholder_password)
            entry_for_password.config(fg='grey',show="")  # Change text color to grey

    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        entry_for_email.config(font=("arial",font_size))
        entry_for_password.config(font=("arial",font_size))
        label_login.config(font=("arial",font_size+20))
        # return font_size


    def loginNow(emailhere, password):


        def on_frame_configure(event):
            screen_height = root.winfo_height()
            font_size = int(screen_height / 60)
            # patient_name_dropdown.config(font=("helvetica",font_size))
            gif_label2.config(font=("helvetica",font_size+10))



        global cur_user,patient_data,patient_data2,patient_list,patient_list2
        # root.withdraw()

        
        try:
            user = auth.sign_in_with_email_and_password(emailhere, password)
            cur_user = user


            frameLogin.destroy()
            frame2_2.destroy()


            frame2_1 = Frame(frame2,bg="#CDDDFF")
            frame2_1.pack(expand=1,fill=BOTH)

            frame_loading = Frame(frame2,bg="#CDDDFF")
            frame_loading.pack(expand=1,fill=BOTH)
            frame_loading.bind("<Configure>", on_frame_configure)

     


            # Load GIF frames
            gif_frames = [loadingAni1final2,loadingAni2final2,loadingAni3final2,loadingAni4final2]
       

            # Function to update GIF
            def update_gif(frame_number):
                gif_label.config(image=gif_frames[frame_number])
                frame_number = (frame_number + 1) % len(gif_frames)
                gif_label.after(500, update_gif, frame_number)  # Change delay (ms) as needed

            gif_label = Label(frame2_1,image="",bg="#CDDDFF")
            gif_label.pack(side=BOTTOM ,anchor=S)

            gif_label2 = Label(frame_loading,text="Loading content. Please wait...",bg="#CDDDFF",fg="#2B318A")
            gif_label2.pack(side=TOP,anchor=N)


            # Start GIF animation
            update_gif(0)


            # ===============================patients module ==============
            def fetchingData():

                global patient_data,patient_data2,patient_list,patient_list2

                patients_ref = db.collection('patients')

                patient_data = []
                patient_data2 = []

                patient_list = []
                patient_list2 = []


                hospital_ref = db.collection('hospitals').document(cur_user['localId'])
                doc_snapshot = hospital_ref.get()
                hospitalName = doc_snapshot.to_dict().get('name')


                patients = patients_ref.where("hospitalId", '==', cur_user['localId']).stream()

                for patient in patients:
                    # Assuming the 'name' field exists in each patient document
                    name = patient.to_dict().get('name')
                    hospitalid= patient.to_dict().get('hospitalId')  # Retrieve the unique ID of the document


                    if hospitalid == cur_user['localId']:
                        phone =  patient.to_dict().get('phone')
                        email = patient.to_dict().get('email')
                        height = patient.to_dict().get('height')
                        gender = patient.to_dict().get('gender')
                        weight = patient.to_dict().get('weight')
                        dob = patient.to_dict().get('dob')
                        
                        ank = patient.to_dict().get('d_notch_ank')
                        rad = patient.to_dict().get('d_notch_rad')
                        uid = patient.id


                        # Get the document data


                        patient_data2.append(f"{name},{phone}")
                        patient_data.append(f"{name},{phone},{hospitalid},{email},{height},{weight},{gender},{dob},{hospitalName}")

                        patient_list.append(f"{name}, {phone}")
                        patient_list2.append(f"{name}, {phone},{hospitalid},{ank},{rad},{height},{uid},{weight},{gender},{hospitalName},{dob}")



                # Sort patient data alphabetically by name
                patient_data2.sort(key=lambda x: x[0])
                patient_data.sort(key=lambda x: x[0])
                patient_list.sort()
                patient_list2.sort()


                # ==============================================


        
            
                frame1_1.destroy()
                frame1_2.destroy()
                frame3_1.destroy()
                frame2_1.destroy()
                frame_loading.destroy()
                Modules()
              

            
                        # Start other tasks in a separate thread
            thread = threading.Thread(target=fetchingData)
            thread.start()


            
      
            # root.deiconify()
            
            

        except :
            # frame3_login.config(bg="red")
            # frame5_login.config(bg="red")
            # entry_for_email.config(fg="red")
            frame3_login.config(bg="red")
            frame5_login.config(bg="red")
            # entry_for_password.config(fg="red")
            messagebox.showerror("Login Error","Invalid email or password.")  





    def hitlogin(event):
        loginNow(entry_for_email.get(),entry_for_password.get())

     

     #two sub frames in first frame     
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1,fill=BOTH,side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1,fill=BOTH,side=RIGHT)

    # two sub frames in frame2 
    frameLogin = Frame(frame2, bg="white")
    frameLogin.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="white")
    frame2_2.pack(side=RIGHT,expand=1,fill=BOTH)

    frameLogin2 = Frame(frameLogin,bg="white")
    frameLogin2.pack(expand=1,fill=BOTH,padx=40,pady=10)

    # # Bind the configure event to the frame
    frameLogin2.bind("<Configure>", on_frame_configure)

     # # sub frames for other widgets in frameLogin2

    frame1_login = Frame(frameLogin2,bg="white")
    frame1_login.pack(expand=1,fill=BOTH)

    frame2_login = Frame(frameLogin2,bg="white")
    frame2_login.pack(expand=1,fill=BOTH)

    frame3_login = Frame(frameLogin2,bg="black",height=2)
    frame3_login.pack(expand=0, fill=X)

    frame4_login = Frame(frameLogin2,bg="white")
    frame4_login.pack(expand=1, fill=BOTH)

    frame5_login = Frame(frameLogin2,bg="black",height=2)
    frame5_login.pack(expand=0, fill=X)

    frame6_login = Frame(frameLogin2,bg="white")
    frame6_login.pack(expand=1, fill=BOTH)

    frame7_login = Frame(frameLogin2,bg="white")
    frame7_login.pack(expand=1, fill=BOTH)

    #footer
    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack()

    # Create a Label widget to display the resized image
    img_label = tk.Label(frame1_1, image=original_img,bg="white")
    img_label.pack(side=LEFT,pady=10,padx=10)


    #image in frame2_2
    landingpage_img_label = Label(frame2_2,image=landing_image1,bg="#CDDDFF")
    landingpage_img_label.pack(expand=1,fill=BOTH)
   


    label_login = Label(frame1_login,text="LOG IN",fg="#464DB6",bg="white")
    label_login.pack(side=BOTTOM)

  

    placeholder_email = "Email"
    entry_for_email = Entry(frame2_login,border=0)
    entry_for_email.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_email.insert(0, placeholder_email)
    entry_for_email.bind("<FocusIn>", on_email_entry_click)
    entry_for_email.bind("<FocusOut>", on_email_focus_out)

    # # label = Label(frame4,text="Enter Your Password")
    # # label_password.pack()

    placeholder_password = "Password"
    entry_for_password = Entry(frame4_login,border=0)
    entry_for_password.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_password.insert(0, placeholder_password)
    entry_for_password.bind("<FocusIn>", on_password_entry_click)
    entry_for_password.bind("<FocusOut>", on_password_focus_out)

    btn_login = Button(frame6_login,image=loginbtnimgdarkfinal,border=0,highlightthickness=0,bg="#464DB6",fg="white",font=("arial",14),command=lambda:(loginNow(entry_for_email.get(),entry_for_password.get())))
    btn_login.pack(side=BOTTOM)

    root.bind("<Return>", hitlogin)
    # Bind Enter key to trigger button click



    #bottom footer 
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

# ===================================================================== landing page logic here ===================================================================
    
def landingWindow():

    def calculate_font_size():
        # Calculate font size based on the current screen width
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        return font_size


    def update_font_size(event):
        # Update the font size when the window is resized
        dynamic_font_size = calculate_font_size()
        # custom_font1.configure(size=dynamic_font_size)
        # labeltitle.config(font=("arial",dynamic_font_size))

# =========================================================

    #two sub frames in first frame
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1,fill=BOTH)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1,fill=BOTH)


    #two sub frames inside second frame
    frame2_1 = Frame(frame2,bg="#CDDDFF")
    frame2_1.pack(side=LEFT,expand=1,fill=BOTH)

    frame2_2 = Frame(frame2,bg="#CDDDFF")
    frame2_2.pack(side=RIGHT,expand=1,fill=BOTH)

    #two sub frames inside frame2_1 
    frame2_1_1 = Frame(frame2_1,bg="#CDDDFF")
    frame2_1_1.pack(side=TOP,expand=1,fill=BOTH)

    frame2_1_2 = Frame(frame2_1,bg="#CDDDFF")
    frame2_1_2.pack(side=BOTTOM,expand=1,fill=BOTH)
    #adding logo to top frames

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack()


# =======================================================
    

    # Create a Label widget to display the image
    img_label = tk.Label(frame1_1, image=original_img,bg="white")
    img_label.pack(side=LEFT,pady=(10),padx=10)
    

    # label in frame2.1.1
    labeltitle = Label(frame2_1_1,image=precogLogo,bg="#CDDDFF")
    labeltitle.pack(side=BOTTOM)
     # # # Bind the resize event to the update_font_size function
    # labeltitle.bind("<Configure>", update_font_size)

    btn_login = Button(frame2_1_2,image=loginbtnimgfinal,border=0,highlightthickness=0,relief=FLAT,fg="#464DB6",bg="#DCE7FF",font=("arial",14),command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame2_1_1.destroy(),frame2_1_2.destroy(),frame3_1.destroy(),loginFrameLogic()))
    btn_login.pack(side=TOP)


    #image in frame2_2
    landingpage_img_label = Label(frame2_2,image=landing_image1,bg="#CDDDFF")
    landingpage_img_label.pack(expand=1,fill=BOTH)


    #bottom footer 
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

# =====================================================================    register device ============================================================================
def registerDevice():


    def on_email_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_email.get() == placeholder_email:
            entry_for_email.delete(0, tk.END)
            entry_for_email.config(fg='black')  # Change text color to black

    def on_email_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_email.get():
            entry_for_email.insert(0, placeholder_email)
            entry_for_email.config(fg='grey')  # Change text color to grey

    def on_password_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_password.get() == placeholder_password:
            entry_for_password.delete(0, tk.END)
            entry_for_password.config(fg='black',show="*")  # Change text color to black

    def on_password_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_password.get():
            entry_for_password.insert(0, placeholder_password)
            entry_for_password.config(fg='grey',show="")  # Change text color to grey



    def on_frame_configure(event):
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        entry_for_email.config(font=("helvetica",font_size))
        entry_for_password.config(font=("helvetica",font_size))
        label_Register.config(font=("helvetica",font_size+20))
   


    def createDevice(email, password):

        if mac_address in mac_ids:
            if status==True:
                messagebox.showerror("Registration error","Your device has already been registered")
                frame1_1.destroy()
                frame1_2.destroy()
                frameRegister.destroy()
                frame2_2.destroy()
                frame3_1.destroy()
                onlyRegister()
                return
            else:
                messagebox.showerror("Registration error","Your device has already been registered. We will approve your device soon.")
                frame1_1.destroy()
                frame1_2.destroy()
                frameRegister.destroy()
                frame2_2.destroy()
                frame3_1.destroy()
                onlyRegister()
                return

        # ==============================================================

        if not email or not password :
            messagebox.showerror("Incomplete Details", "Please enter complete details.")
            return 
        
        elif(email=="Email id"  or password=="Password"):
            messagebox.showerror("Empty values", "Please enter all the fields")
            # addPatientSelected()
            return
        
        elif not validate_email(email):
            messagebox.showerror("Signup Error", "Invalid email address.")
            return

        else:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user_ref = db.collection('macid').document(mac_address)
                user_ref.set({
                    'access token': "",
                    'hospitalId': user['localId'],
                    'status': False
                    
                })


                # Reference to the document
                doc_ref = db.collection('hospitals').document(user['localId'] )

                # Update the array field by appending the new value
                doc_ref.update({
                    'macids': firestore.ArrayUnion([mac_address])
                })
                            

                
                messagebox.showinfo("Login", "Device registered successfully!\n We will approve your request soon")
                frame1_1.destroy()
                frame1_2.destroy()
                frameRegister.destroy()
                frame2_2.destroy()
                frame3_1.destroy()
                onlyRegister()
            
            except Exception as e:
                messagebox.showerror("Login Error", e)

                

    



    # ============================================================

    # sub frames in main 3 frames
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1,fill=BOTH,side=LEFT)
    

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1,fill=BOTH,side=RIGHT)


    #frames inside frame2
    frameRegister = Frame(frame2, bg="white")
    frameRegister.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="white")
    frame2_2.pack(side=RIGHT,expand=1,fill=BOTH)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack()
    

    # ======================== other frames ========================
   

    frameRegister2 = Frame(frameRegister,bg="white")
    frameRegister2.pack(expand=1,fill=BOTH,padx=40,pady=10)

    # # Bind the configure event to the frame
    frameRegister2.bind("<Configure>", on_frame_configure)

    frame0_register = Frame(frameRegister2,bg="white")
    frame0_register.pack(expand=0,fill=X)


    frame1_register = Frame(frameRegister2,bg="white")
    frame1_register.pack(expand=1,fill=BOTH)

    frame2_register = Frame(frameRegister2,bg="white")
    frame2_register.pack(expand=1,fill=BOTH)

    frame3_register = Frame(frameRegister2,bg="black",height=1)
    frame3_register.pack(expand=0, fill=X)

    frame4_register = Frame(frameRegister2,bg="white")
    frame4_register.pack(expand=1,fill=BOTH)

    frame5_register = Frame(frameRegister2,bg="black",height=1)
    frame5_register.pack(expand=0, fill=X)


    frame6_register = Frame(frameRegister2,bg="white")
    frame6_register.pack(expand=1, fill=BOTH)

    frame7_register = Frame(frameRegister2,bg="white")
    frame7_register.pack(expand=1,fill=BOTH)


    
# ============================================================
    


    # Create a Label widget to display the resized image at top left
    img_label = tk.Label(frame1_1, image=original_img,bg="white")
    img_label.pack(side=LEFT,pady=10,padx=10)
    
    btn_back = Button(frame0_register,bg="white",image=backbtnimageblue2,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frameRegister.destroy(),frame2_2.destroy(),frame3_1.destroy(),onlyRegister()))
    btn_back.pack(side=LEFT)

    label_Register = Label(frame1_register,text="LOG IN",fg="#464DB6",bg="white")
    label_Register.pack(side=BOTTOM)

    placeholder_email = "Email id"
    entry_for_email = Entry(frame2_register,border=0)
    entry_for_email.pack(side=LEFT,anchor=S)
    entry_for_email.insert(0, placeholder_email)
    entry_for_email.bind("<FocusIn>", on_email_entry_click)
    entry_for_email.bind("<FocusOut>", on_email_focus_out)

    placeholder_password = "Password"
    entry_for_password = Entry(frame4_register,border=0)
    entry_for_password.pack(side=LEFT,anchor=S)
    entry_for_password.insert(0, placeholder_password)
    entry_for_password.bind("<FocusIn>", on_password_entry_click)
    entry_for_password.bind("<FocusOut>", on_password_focus_out)  

    btn_register = Button(frame6_register,image=registerbtnimgfinal,border=0,highlightthickness=0,bg="#464DB6",fg="white",font=("arial",14),command=lambda:(createDevice(entry_for_email.get(),entry_for_password.get())))
    btn_register.pack(side=BOTTOM)

    
    #image in frame2_2
    landingpage_img_label = Label(frame2_2,image=landing_image1,bg="#CDDDFF")
    landingpage_img_label.pack(expand=1,fill=BOTH)

     #bottom footer 
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=16)

# ====================================================================   register hospital ============================================================================

def registerHospital():  

    def on_name_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_name.get() == placeholder_name:
            entry_for_name.delete(0, tk.END)
            entry_for_name.config(fg='black')  # Change text color to black

    def on_name_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_name.get():
            entry_for_name.insert(0, placeholder_name)
            entry_for_name.config(fg='grey')  # Change text color to grey

    def on_address_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_address.get() == placeholder_address:
            entry_for_address.delete(0, tk.END)
            entry_for_address.config(fg='black')  # Change text color to black

    def on_address_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_address.get():
            entry_for_address.insert(0, placeholder_address)
            entry_for_address.config(fg='grey')  # Change text color to grey

    def on_phone_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_phone.get() == placeholder_phone:
            entry_for_phone.delete(0, tk.END)
            entry_for_phone.config(fg='black')  # Change text color to black

    def on_phone_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_phone.get():
            entry_for_phone.insert(0, placeholder_phone)
            entry_for_phone.config(fg='grey')  # Change text color to grey

    def on_email_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_email.get() == placeholder_email:
            entry_for_email.delete(0, tk.END)
            entry_for_email.config(fg='black')  # Change text color to black

    def on_email_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_email.get():
            entry_for_email.insert(0, placeholder_email)
            entry_for_email.config(fg='grey')  # Change text color to grey

    def on_password_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_password.get() == placeholder_password:
            entry_for_password.delete(0, tk.END)
            entry_for_password.config(fg='black',show="*")  # Change text color to black

    def on_password_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_password.get():
            entry_for_password.insert(0, placeholder_password)
            entry_for_password.config(fg='grey',show="")  # Change text color to grey

    def on_confirmpassword_entry_click(event):
    # """Function to clear the placeholder text when the entry is clicked."""
        if entry_for_confirmpassword.get() == placeholder_confirmpassword:
            entry_for_confirmpassword.delete(0, tk.END)
            entry_for_confirmpassword.config(fg='black',show="*")  # Change text color to black

    def on_confirmpassword_focus_out(event):
        # """Function to restore the placeholder text if the entry is left empty."""
        if not entry_for_confirmpassword.get():
            entry_for_confirmpassword.insert(0, placeholder_confirmpassword)
            entry_for_confirmpassword.config(fg='grey',show="")  # Change text color to grey

    def on_frame_configure(event):
        screen_width = root.winfo_width()
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        entry_for_email.config(font=("helvetica",font_size))
        entry_for_name.config(font=("helvetica",font_size))
        entry_for_password.config(font=("helvetica",font_size))
        entry_for_phone.config(font=("helvetica",font_size))
        entry_for_address.config(font=("helvetica",font_size))
        entry_for_confirmpassword.config(font=("helvetica",font_size))
        label_Register.config(font=("helvetica",font_size+20))
        return font_size


    def createUser(email, password,confirmpassword,name,phone,address):

        frame3_register.config(bg="white")

        
        frame5_register.config(bg="white")

        frame_underline_register2.config(bg="white")
                


        frame_underline_register.config(bg="white")



        frame6_1_2_register.config(bg="white")


   
        frame6_2_2_register.config(bg="white")








# Reference to the collection
        collection_ref = db.collection('macid')

        # Fetch all documents from the collection
        documents = collection_ref.stream()

        # Extract unique IDs (mac IDs)
        mac_ids = [doc.id for doc in documents]

        if mac_address in mac_ids:
            messagebox.showerror("Registration","You have already registered your hospital. We will approve your request soon.")
            frame1_1.destroy(),frame1_2.destroy(),frameRegister.destroy(),frame2_2.destroy(),frame3_1.destroy(),onlyRegister()

            return
        

        # ==============================================================

        if not email or not password or not confirmpassword or not name or not phone or not address:
            messagebox.showerror("Incomplete Details", "Please enter complete details.")
            return 
        
        elif(name=="Hospital/Clinic name" or email=="Email id" or phone=="Phone number" or address=="Address" or password=="Password" or confirmpassword=="Confirm password"or not email or not password or not confirmpassword or not name or not phone or not address):

            if(name=="Hospital/Clinic name" or not name.strip()):
                messagebox.showerror("Empty values", "Please enter all the fields")
                frame3_register.config(bg="red")

            
            if(email=="Email id" or not email.strip()):
                messagebox.showerror("Empty values", "Please enter all the fields")
                frame5_register.config(bg="red")

            if(phone=="Phone number" or not phone.strip()):
                messagebox.showerror("Empty values", "Please enter all the fields")
                frame_underline_register2.config(bg="red")
                


            if(address=="Address" or not address.strip()):
                messagebox.showerror("Empty values", "Please enter all the fields")
                frame_underline_register.config(bg="red")



            if(password=="Password" or not password.strip()):
                messagebox.showerror("Empty values", "Please enter all the fields")
                frame6_1_2_register.config(bg="red")


            
            if(confirmpassword=="Confirm password" or not confirmpassword.strip()):
                messagebox.showerror("Empty values", "Please enter all the fields")
                frame6_2_2_register.config(bg="red")


       
            return
        
        elif not validate_email(email):
            frame5_register.config(bg="red")
            messagebox.showerror("Signup Error", "Invalid email address.")
            return

        elif not validate_phone(phone):
            frame_underline_register2.config(bg="red")
            messagebox.showerror("Signup Error", "Invalid phone number. Only numbers are allowed.")
            return

        elif(password==confirmpassword):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                print(user['localId'])
                
                user_ref = db.collection('hospitals').document(user['localId'])
                user_ref.set({
                    'email': email,
                    'address':address,
                    'name': name,
                    'phone': phone,
                    'macid': mac_address,
                    'patients': []
                })

                user_ref = db.collection('macid').document(mac_address)
                user_ref.set({
                    'access_token': "",
                    'hospitalId': user['localId'],
                    'status': False,
                    'email': email,
                    'name': name,

                })

                messagebox.showinfo("Registration", "Registration request has been sent successfuly. We will approve your device soon. Kindly restart your application.")


                frame1_2.destroy(),frame1_1.destroy(),frame2_2.destroy(),frameRegister.destroy(),frame3_1.destroy(),onlyRegister()
                return
           

            except Exception as e:
                messagebox.showerror("Signup Error", f"Error creating account{e}")

        else:
            frame6_1_2_register.config(bg="red")
            frame6_2_2_register.config(bg="red")
            messagebox.showerror("Password error", "Password and confirm password must be same")




    # ============================================================

    # sub frames in main 3 frames
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1,fill=BOTH,side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1,fill=BOTH,side=RIGHT)


    #frames inside frame2
    frameRegister = Frame(frame2, bg="white")
    frameRegister.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="white")
    frame2_2.pack(side=RIGHT,expand=1,fill=BOTH)

    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack()
    

    # ======================== other frames ========================
   

    frameRegister2 = Frame(frameRegister,bg="white")
    frameRegister2.pack(expand=1,fill=BOTH,padx=40,pady=10)

    # # Bind the configure event to the frame
    frameRegister2.bind("<Configure>", on_frame_configure)

    frame0_register  = Frame(frameRegister2,bg="white")
    frame0_register.pack(expand=0,fill=X)

    frame1_register = Frame(frameRegister2,bg="white")
    frame1_register.pack(expand=1,fill=BOTH)

    frame2_register = Frame(frameRegister2,bg="white")
    frame2_register.pack(expand=1,fill=BOTH)

    frame3_register = Frame(frameRegister2,bg="black",height=1)
    frame3_register.pack(expand=0, fill=X)

    frame_address_register = Frame(frameRegister2,bg="white")
    frame_address_register.pack(expand=1,fill=BOTH)

    frame_underline_register = Frame(frameRegister2,bg="black",height=1)
    frame_underline_register.pack(expand=0, fill=X)

    frame_phone_register = Frame(frameRegister2,bg="white")
    frame_phone_register.pack(expand=1,fill=BOTH)

    frame_underline_register2 = Frame(frameRegister2,bg="black",height=1)
    frame_underline_register2.pack(expand=0, fill=X)

    frame4_register = Frame(frameRegister2,bg="white")
    frame4_register.pack(expand=1, fill=BOTH)

    frame5_register = Frame(frameRegister2,bg="black",height=1)
    frame5_register.pack(expand=0, fill=X)

    frame6_register = Frame(frameRegister2,bg="white")
    frame6_register.pack(expand=1, fill=BOTH)

    #sub frames in frame 6 
    frame6_1_register = Frame(frame6_register,bg="white")
    frame6_1_register.pack(expand=1, fill=BOTH,side=LEFT,padx=(0,10))

    frame6_2_register = Frame(frame6_register,bg="white")
    frame6_2_register.pack(expand=1, fill=BOTH,side=RIGHT,padx=(10,0))

    #two sub frames again 

    frame6_1_1_register = Frame(frame6_1_register,bg="white")
    frame6_1_1_register.pack(expand=1, fill=BOTH,side=TOP,anchor=S)

    frame6_1_2_register = Frame(frame6_1_register,bg="black",height=1)
    frame6_1_2_register.pack(expand=0, fill=X,side=BOTTOM,anchor=S)

    #two sub frames 

    frame6_2_1_register = Frame(frame6_2_register,bg="white")
    frame6_2_1_register.pack(expand=1, fill=BOTH,side=TOP,anchor=S)

    frame6_2_2_register = Frame(frame6_2_register,bg="black",height=1)
    frame6_2_2_register.pack(expand=0, fill=X,side=BOTTOM,anchor=S)

    #regular frames

    frame7_register = Frame(frameRegister2,bg="white")
    frame7_register.pack(expand=1, fill=BOTH)

    frame8_register = Frame(frameRegister2,bg="white")
    frame8_register.pack(expand=1,fill=BOTH)


    
# ============================================================
    


    # Create a Label widget to display the resized image at top left
    img_label = tk.Label(frame1_1, image=original_img,bg="white")
    img_label.pack(side=LEFT,pady=10,padx=10)


    # custom_font = tkFont.Font(underline=True)

 
    btn_back = Button(frame0_register,bg="white",image=backbtnimageblue2,border=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frameRegister.destroy(),frame2_2.destroy(),frame3_1.destroy(),onlyRegister()))
    btn_back.pack(side=LEFT,anchor=S)

    label_Register = Label(frame1_register,text="REGISTRATION FORM",fg="#464DB6",bg="white")
    label_Register.pack(side=BOTTOM)

  

    placeholder_name = "Hospital/Clinic name"
    entry_for_name = Entry(frame2_register,border=0)
    entry_for_name.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_name.insert(0, placeholder_name)
    entry_for_name.bind("<FocusIn>", on_name_entry_click)
    entry_for_name.bind("<FocusOut>", on_name_focus_out)

    placeholder_address = "Address"
    entry_for_address = Entry(frame_address_register,border=0)
    entry_for_address.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_address.insert(0, placeholder_address)
    entry_for_address.bind("<FocusIn>", on_address_entry_click)
    entry_for_address.bind("<FocusOut>", on_address_focus_out)

    placeholder_phone = "Phone number"
    entry_for_phone = Entry(frame_phone_register,border=0)
    entry_for_phone.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_phone.insert(0, placeholder_phone)
    entry_for_phone.bind("<FocusIn>", on_phone_entry_click)
    entry_for_phone.bind("<FocusOut>", on_phone_focus_out)



    placeholder_email = "Email id"
    entry_for_email = Entry(frame4_register,border=0)
    entry_for_email.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_email.insert(0, placeholder_email)
    entry_for_email.bind("<FocusIn>", on_email_entry_click)
    entry_for_email.bind("<FocusOut>", on_email_focus_out)

    placeholder_password = "Password"
    entry_for_password = Entry(frame6_1_1_register,border=0)
    entry_for_password.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_password.insert(0, placeholder_password)
    entry_for_password.bind("<FocusIn>", on_password_entry_click)
    entry_for_password.bind("<FocusOut>", on_password_focus_out)

    placeholder_confirmpassword = "Confirm password"
    entry_for_confirmpassword = Entry(frame6_2_1_register,border=0)
    entry_for_confirmpassword.pack(side=LEFT,anchor=S,expand=1,fill=X)
    entry_for_confirmpassword.insert(0, placeholder_confirmpassword)
    entry_for_confirmpassword.bind("<FocusIn>", on_confirmpassword_entry_click)
    entry_for_confirmpassword.bind("<FocusOut>", on_confirmpassword_focus_out)

  

    btn_register = Button(frame7_register,image=registerbtnimgfinal,border=0,highlightthickness=0,bg="#464DB6",fg="white",font=("arial",14),command=lambda:(createUser(entry_for_email.get(),entry_for_password.get(),entry_for_confirmpassword.get(),entry_for_name.get(),entry_for_phone.get(),entry_for_address.get())))
    btn_register.pack(side=BOTTOM)

    
    #image in frame2_2
    landingpage_img_label = Label(frame2_2,image=landing_image1,bg="#CDDDFF")
    landingpage_img_label.pack(expand=1,fill=BOTH)

     #bottom footer 
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

# =================================================================== only register ===================================================================================
    
def onlyRegister():

    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
  

    def on_frame_configure(event):
        screen_width = root.winfo_width()
        screen_height = root.winfo_height()
        font_size = int(screen_height / 60)
        registerYour.config(font=("helvetica",font_size+20))
        


    # ============================================================

    # sub frames in main 3 frames
    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1,fill=BOTH,side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1,fill=BOTH,side=RIGHT)


    #frames inside frame2
    frame2_1 = Frame(frame2,bg="#CDDDFF")
    frame2_1.pack(expand=1, fill=BOTH, side=LEFT)

    frame2_2 = Frame(frame2,bg="#CDDDFF")
    frame2_2.pack(side=RIGHT,expand=1,fill=BOTH)


    #frame inside frame3
    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack()
    

    # ======================== other frames ========================
   

    #3 sub frames inside frame 2_1 
    frame2_1_1 = Frame(frame2_1,bg="#CDDDFF")
    frame2_1_1.pack(expand=1, fill=BOTH)

    frame2_1_2 = Frame(frame2_1,bg="#CDDDFF")
    frame2_1_2.pack()

    frame2_1_3 = Frame(frame2_1,bg="#CDDDFF")
    frame2_1_3.pack(expand=1, fill=BOTH)

    #two more sub frames inside frame213

    frame2_1_3_1 = Frame(frame2_1_3,bg="#CDDDFF")
    frame2_1_3_1.pack(expand=1,fill=BOTH)


    # frame2_1_3_2 = Frame(frame2_1_3,bg="#CDDDFF")
    # frame2_1_3_2.pack(side=RIGHT,expand=1,fill=BOTH)




# ============================================================
    


    # Create a Label widget to display the resized image at top left
    img_label = tk.Label(frame1_1, image=original_img,bg="white")
    img_label.pack(side=LEFT,pady=10,padx=10)    


    precogLogoLabel = Label(frame2_1_1,image=precogLogo,bg="#CDDDFF")
    precogLogoLabel.pack(side=BOTTOM,anchor=S)


    registerYour = Label(frame2_1_2,bg="#CDDDFF",text="Register your")
    registerYour.pack(anchor=S,pady=(40,10))

    btnHospitalimg = Button(frame2_1_3_1,image=btnHospital,bg="#CDDDFF",border=0,highlightthickness=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),registerHospital()))
    btnHospitalimg.pack(expand=0)

    # btnDeviceimg = Button(frame2_1_3_2,image=btnDevice,bg="#CDDDFF",border=0,highlightthickness=0,command=lambda:(frame1_1.destroy(),frame1_2.destroy(),frame2_1.destroy(),frame2_2.destroy(),frame3_1.destroy(),registerDevice()))
    # btnDeviceimg.pack(side=LEFT,anchor=N,expand=0,padx=(20,0))


    #image in frame2_2
    landingpage_img_label = Label(frame2_2,image=landing_image1,bg="#CDDDFF")
    landingpage_img_label.pack(expand=1,fill=BOTH)

     #bottom footer 
    label_footer = Label(frame3_1,text="Copyright © 2024 Acuradyne Systems",bg="white")
    label_footer.pack(pady=5)

    frame2_1.bind("<Configure>", on_frame_configure)

# ==================================================================== loading window ===================================================================================
def loadingScreen(takeFunction):
    def endLoading():
        takeFunction()
        frame1_1.destroy()
        frame1_2.destroy()
        frame2_1.destroy()
        frame3_1.destroy()

    frame1_1 = Frame(frame1,bg="white")
    frame1_1.pack(expand=1,fill=BOTH,side=LEFT)

    frame1_2 = Frame(frame1,bg="white")
    frame1_2.pack(expand=1,fill=BOTH,side=RIGHT)


    #frames inside frame2
    frame2_1 = Frame(frame2,bg="#CDDDFF")
    frame2_1.pack(expand=1, fill=BOTH)


    #frame inside frame3
    frame3_1 = Frame(frame3,bg="white")
    frame3_1.pack()


    label_loading = Label(frame2_1,text="loading your content")
    label_loading.pack()

    endLoading()

# ================================================================     Main window logic   ================================================================================

# main window
root = Tk()


root.withdraw()  # Hide the main window temporarily

global cur_user,mac_ids, mac_address,status,name_onselect
cur_user = ""
name_onselect = ""

def close_splash():  # this is the function to close the splash screen 
    # Check internet connection 
    if check_internet_connection():
        print("Internet connection available")

        # Reference to the collection
        collection_ref = db.collection('macid')

        # Fetch all documents from the collection
        documents = collection_ref.stream()

        # Extract unique IDs (mac IDs)
        mac_ids = [doc.id for doc in documents]

        # Print the unique IDs
        print("Unique IDs (mac IDs) of all documents:")
        print(mac_ids)

        status = False

        if mac_address in mac_ids:
            
            # Reference to the document
            doc_ref = db.collection('macid').document(mac_address)  

            # Get the document snapshot
            doc_snapshot = doc_ref.get()
            status = doc_snapshot.get('status')

            if status:
                splash.destroy()
                root.deiconify()
                landingWindow()

            else:
                splash.destroy()
                root.deiconify()
                onlyRegister()
                
        else:
            # messagebox.showerror("Registration Issue", "Your device is not registered")
            splash.destroy()
            root.deiconify()
            onlyRegister()
            
            
    else:
        
        print("No internet connection")
        splash.destroy()
        root.deiconify()
        messagebox.showerror("Connectivity issues","Check your internet connectivity")
        root.destroy()

    



splash = tk.Toplevel()   # Create the splash screen
splash.overrideredirect(True)  # Remove window borders and title bar

# Get the screen width
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - 660) // 2
y_position = (screen_height - 630) // 2

# root.geometry()
splash.geometry(f'660x630+{x_position}+{y_position}')
splash.configure(bg="white")


splash.resizable(False, False)  # Disable resizing


# Save the binary image data to a temporary file
splash_img_data = get_embedded_image_data("images\\splashfinal.png")
splash_img_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
splash_img_temp_file.write(splash_img_data)
splash_img_temp_file.close()

# Create a PhotoImage object using the path to the temporary file
splashImg = PhotoImage(file=splash_img_temp_file.name)

# After using the PhotoImage object, don't forget to clean up the temporary file
os.unlink(splash_img_temp_file.name)
# splash_image = tk.PhotoImage(file=)
label = tk.Label(splash, image=splashImg)
label.pack(expand=True, fill="both")

# Get the screen width
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

 # # image here  =============================
# Load and resize images
precog_logo_data = get_embedded_image_data("images\\precoglogofinal.png")
precog_logo = PIL.Image.open(io.BytesIO(precog_logo_data))
# precog_logo = precog_logo.resize((desired_width, desired_height))  # Replace desired_width and desired_height with actual values
precogLogo = PIL.ImageTk.PhotoImage(precog_logo)

# Retrieve the binary image data
precog_logo_data = get_embedded_image_data("images\\precoglogofinal.png")
# Create an Image object from the binary data
precog_logo = PIL.Image.open(io.BytesIO(precog_logo_data))
# Convert the Image object to a PhotoImage object for use in Tkinter
precogLogo = PIL.ImageTk.PhotoImage(precog_logo)

original_img_data = get_embedded_image_data("images\\acuradynelogofinal.png")
original_img = PIL.Image.open(io.BytesIO(original_img_data))
original_img = PIL.ImageTk.PhotoImage(original_img)

buttonHospital1 = get_embedded_image_data("images\\register_hospital_btn.png")
buttonHospital2= PIL.Image.open(io.BytesIO(buttonHospital1))
btnHospital = PIL.ImageTk.PhotoImage(buttonHospital2)

support1 = get_embedded_image_data("images\\support_step1.png")
support1final= PIL.Image.open(io.BytesIO(support1))
support1final2 = PIL.ImageTk.PhotoImage(support1final)

support2 = get_embedded_image_data("images\\support_step2.png")
support2final= PIL.Image.open(io.BytesIO(support2))
support2final2 = PIL.ImageTk.PhotoImage(support2final)

support3 = get_embedded_image_data("images\\support_step3.png")
support3final= PIL.Image.open(io.BytesIO(support3))
support3final2 = PIL.ImageTk.PhotoImage(support3final)

buttonDevice1 = get_embedded_image_data("images\\register_device_btn.png")
buttonDevice2= PIL.Image.open(io.BytesIO(buttonDevice1))
btnDevice = PIL.ImageTk.PhotoImage(buttonDevice2)

image2_data = get_embedded_image_data("images\\landingpageimg.png")
image2 = PIL.Image.open(io.BytesIO(image2_data))
image2final = PIL.ImageTk.PhotoImage(image2)

registerbtnimg_data = get_embedded_image_data("images\\registerbutton.png")
registerbtnimg = PIL.Image.open(io.BytesIO(registerbtnimg_data))
registerbtnimgfinal = PIL.ImageTk.PhotoImage(registerbtnimg)

loginbtnimg_data = get_embedded_image_data("images\\loginbutton.png")
loginbtnimg = PIL.Image.open(io.BytesIO(loginbtnimg_data))
loginbtnimgfinal = PIL.ImageTk.PhotoImage(loginbtnimg)

loginbtnimgdark_data = get_embedded_image_data("images\\loginbuttondark.png")
loginbtnimgdark = PIL.Image.open(io.BytesIO(loginbtnimgdark_data))
loginbtnimgdarkfinal = PIL.ImageTk.PhotoImage(loginbtnimgdark)

btn1_data = get_embedded_image_data("images\\btn1.png")
btn1 = PIL.Image.open(io.BytesIO(btn1_data))
btn1final = PIL.ImageTk.PhotoImage(btn1)

btn2_data = get_embedded_image_data("images\\btn2.png")
btn2 = PIL.Image.open(io.BytesIO(btn2_data))
btn2final = PIL.ImageTk.PhotoImage(btn2)

btn3_data = get_embedded_image_data("images\\btn3.png")
btn3 = PIL.Image.open(io.BytesIO(btn3_data))
btn3final = PIL.ImageTk.PhotoImage(btn3)

device_image1_data = get_embedded_image_data("images\\device1.png")
device_image1 = PIL.Image.open(io.BytesIO(device_image1_data))
deviceImage1 = PIL.ImageTk.PhotoImage(device_image1)

device_image2_data = get_embedded_image_data("images\\device1.png")
device_image2 = PIL.Image.open(io.BytesIO(device_image2_data))
deviceImage2 = PIL.ImageTk.PhotoImage(device_image2)

device_image3_data = get_embedded_image_data("images\\device1.png")
device_image3 = PIL.Image.open(io.BytesIO(device_image3_data))
deviceImage3 = PIL.ImageTk.PhotoImage(device_image3)

btn1selected_data = get_embedded_image_data("images\\btn1select.png")
btn1selected = PIL.Image.open(io.BytesIO(btn1selected_data))
btn1SelectedFinal = PIL.ImageTk.PhotoImage(btn1selected)

btn2selected_data = get_embedded_image_data("images\\btn2select.png")
btn2selected = PIL.Image.open(io.BytesIO(btn2selected_data))
btn2SelectedFinal = PIL.ImageTk.PhotoImage(btn2selected)

backbtnimage_data = get_embedded_image_data("images\\backbtnfinal.png")
backbtnimage = PIL.Image.open(io.BytesIO(backbtnimage_data))
backbtnimagefinal = PIL.ImageTk.PhotoImage(backbtnimage)

backbtnimageblue_data = get_embedded_image_data("images\\backbtnblue.png")
backbtnimageblue = PIL.Image.open(io.BytesIO(backbtnimageblue_data))
backbtnimageblue2 = PIL.ImageTk.PhotoImage(backbtnimageblue)

backbtnimageneon_data = get_embedded_image_data("images\\backbtnneon.png")
backbtnimageneon = PIL.Image.open(io.BytesIO(backbtnimageneon_data))
backbtnimageneon2 = PIL.ImageTk.PhotoImage(backbtnimageneon)

downloadbtn_data = get_embedded_image_data("images\\downloadbtn2.png")
downloadbtn = PIL.Image.open(io.BytesIO(downloadbtn_data))
downloadbutton2 = PIL.ImageTk.PhotoImage(downloadbtn)

patientlistimg_data = get_embedded_image_data("images\\patientinfo.png")
patientlistimg = PIL.Image.open(io.BytesIO(patientlistimg_data))
patientlistimgfinal = PIL.ImageTk.PhotoImage(patientlistimg)

search_icon = get_embedded_image_data("images\\searchicon.png")
searchiconimg = PIL.Image.open(io.BytesIO(search_icon))
searchiconimgfinal = PIL.ImageTk.PhotoImage(searchiconimg)

next_btn = get_embedded_image_data("images\\nextbtn.png")
nextbtnimg = PIL.Image.open(io.BytesIO(next_btn))
nextbtnimgfinal = PIL.ImageTk.PhotoImage(nextbtnimg)

add_patient_btn = get_embedded_image_data("images\\addpatientbtn.png")
addpatientbtnimg = PIL.Image.open(io.BytesIO(add_patient_btn))
addpatientbtnimgfinal = PIL.ImageTk.PhotoImage(addpatientbtnimg)

loadingImage = get_embedded_image_data("images\\loadingImage.jpg")
loadingImage2 = PIL.Image.open(io.BytesIO(loadingImage))
loadingImageFinal = PIL.ImageTk.PhotoImage(loadingImage2)

landing_image_data = get_embedded_image_data("images\\landingPage.png")
landing_image = PIL.Image.open(io.BytesIO(landing_image_data))
landing_image1 = PIL.ImageTk.PhotoImage(landing_image)

showReportButton = get_embedded_image_data("images\\showReportButton.png")
showReportButton2 = PIL.Image.open(io.BytesIO(showReportButton))
showReportButtonfinal = PIL.ImageTk.PhotoImage(showReportButton2)

startrecordingbtn = get_embedded_image_data("images\\startrecordingbtn.png")
startrecordingbtn2 = PIL.Image.open(io.BytesIO(startrecordingbtn))
startrecordingbtn3 = PIL.ImageTk.PhotoImage(startrecordingbtn2)

stoprecordingbtn = get_embedded_image_data("images\\stoprecordingbtn.png")
stoprecordingbtn2 = PIL.Image.open(io.BytesIO(stoprecordingbtn))
stoprecordingbtn3 = PIL.ImageTk.PhotoImage(stoprecordingbtn2)

refreshportbtn = get_embedded_image_data("images\\refreshportbtn.png")
refreshportbtn2 = PIL.Image.open(io.BytesIO(refreshportbtn))
refreshportbtn3 = PIL.ImageTk.PhotoImage(refreshportbtn2)

connectbtn = get_embedded_image_data("images\\connectbtn.png")
connectbtn2 = PIL.Image.open(io.BytesIO(connectbtn))
connectbtn3 = PIL.ImageTk.PhotoImage(connectbtn2)

disconnectbtn = get_embedded_image_data("images\\disconnectbtn.png")
disconnectbtn2 = PIL.Image.open(io.BytesIO(disconnectbtn))
disconnectbtn3 = PIL.ImageTk.PhotoImage(disconnectbtn2)

generatereportbtn = get_embedded_image_data("images\\generatereportbtn.png")
generatereportbtn2 = PIL.Image.open(io.BytesIO(generatereportbtn))
generatereportbtn3 = PIL.ImageTk.PhotoImage(generatereportbtn2)  

# ==========loading images =========================
loadingAni1 = get_embedded_image_data("images\\loadingAni1.png")
loadingAni1final = PIL.Image.open(io.BytesIO(loadingAni1))
loadingAni1final2 = PIL.ImageTk.PhotoImage(loadingAni1final)

loadingAni2 = get_embedded_image_data("images\\loadingAni2.png")
loadingAni2final = PIL.Image.open(io.BytesIO(loadingAni2))
loadingAni2final2 = PIL.ImageTk.PhotoImage(loadingAni2final)

loadingAni3 = get_embedded_image_data("images\\loadingAni3.png")
loadingAni3final = PIL.Image.open(io.BytesIO(loadingAni3))
loadingAni3final2 = PIL.ImageTk.PhotoImage(loadingAni3final)

loadingAni4 = get_embedded_image_data("images\\loadingAni4.png")
loadingAni4final = PIL.Image.open(io.BytesIO(loadingAni4))
loadingAni4final2 = PIL.ImageTk.PhotoImage(loadingAni4final)

# ============================================================

x_position = (screen_width - 1024) // 2
y_position = (screen_height - 640) // 2

root.geometry(f'1024x640+{x_position}+{y_position}')
root.configure(bg='#fff')
root.title("Precog")

# Get embedded image data
app_logo = get_embedded_image_data("images\\desktopicon.ico")

# Open the image from binary data
app_logo2 = PIL.Image.open(io.BytesIO(app_logo))


# Save the image to a temporary file
temp_icon_file = "temp_icon.ico"
app_logo2.save(temp_icon_file)

# Set the icon for the application window
root.iconbitmap(temp_icon_file)

# Remove the temporary icon file
os.remove(temp_icon_file)


#main three frames 
frame1 = Frame(root,bg="white")
frame1.pack(expand=0,side=TOP,fill=X)

frame2 = Frame(root,bg="white")
frame2.pack(expand=1,fill=BOTH)

frame3 = Frame(root,bg="white")
frame3.pack(expand=0, side=BOTTOM,fill=X)

mac_address = get_mac_address()
print("MAC Address:", mac_address)

splash.after(100,close_splash)

root.mainloop()

