import tkinter as tk
import time
import threading
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk

from controlMenu import ControlMenu
from help import HelpMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Record(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.isrecording = False
        self.fs = 44100
        self.cm = ControlMenu()
        self.recordMenu()

    def recordMenu(self):
        rm = tk.Toplevel()
        rm.resizable(True, True)
        rm.title('Record')
        # rm.iconbitmap('icon.ico')
        rm.wm_transient(self) # Place the toplevel window at the top
        # self.cm.windowGeometry(rm, 850, 250)
        hm = HelpMenu()

        # Adapt the window to different sizes
        for i in range(1):
            rm.columnconfigure(i, weight=1)

        for i in range(2):
            rm.rowconfigure(i, weight=1)

        # BUTTONS
        # play = PhotoImage(file='icons/play.png')
        # stop = PhotoImage(file='icons/stop.png')
        # self.but_reco = tk.Button(rm, text='🎤', font=('Arial', 100, 'bold'), command=lambda: self.clickHandler())
        self.but_play = ttk.Button(rm, command=lambda: self.startrecording(), text='Start recording')
        self.but_stop = ttk.Button(rm, command=lambda: self.stoprecording(rm), text='Stop recording')
        self.but_help = ttk.Button(rm, command=lambda: hm.createHelpMenu(self, 7), text='🛈', width=2)

        self.but_play.grid()
        self.but_stop.grid()
        self.but_help.grid()

        self.lab_time = ttk.Label(rm, text='00:00')
        self.lab_time.grid()

    def startrecording(self):
        self.isrecording = True
        t = threading.Thread(target=self.record)
        t.start()

    def stoprecording(self, rm):
        self.isrecording = False
        self.plotRecording(rm)

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=self.fs, input=True, frames_per_buffer=1024)
        self.frames = []
        start = time.time()

        while self.isrecording:
            data = stream.read(1024)
            self.frames.append(data)

            dur = time.time() - start
            secs = dur % 60
            mins = dur // 60
            self.lab_time.config(text=f"{int(mins):02d}:{int(secs):02d}")

        stream.stop_stream()
        stream.close()
        audio.terminate()

    def plotRecording(self, rm):
        fig, ax = plt.subplots()

        myrecording = np.frombuffer(b"".join(self.frames), dtype=np.int16)
        lenMyRecord = len(myrecording)
        duration = lenMyRecord / self.fs
        time = np.linspace(start=0, stop=duration, num=lenMyRecord)

        fig, ax = self.cm.generateWindow(self, fig, ax, self.fs, time, myrecording, rm, 'Recording')
        # rm.destroy()

        # Plot the recording
        ax.plot(time, myrecording)
        fig.canvas.manager.set_window_title('Record')
        ax.set(xlim=[0, duration], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0

        plt.show()