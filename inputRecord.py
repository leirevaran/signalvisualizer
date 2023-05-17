import tkinter as tk
import time
import threading
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import SpanSelector, Button

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
        self.fig, self.ax = plt.subplots()
        self.selectedAudio = np.empty(1)
        self.recordMenu()

    def recordMenu(self):
        rm = tk.Toplevel()
        rm.resizable(True, True)
        rm.title('Record')
        rm.iconbitmap('icons/icon.ico')
        rm.wm_transient(self) # Place the toplevel window at the top
        hm = HelpMenu()

        # Adapt the window to different sizes
        for i in range(1):
            rm.columnconfigure(i, weight=1)

        for i in range(2):
            rm.rowconfigure(i, weight=1)

        # If the 'generate' menu is closed, close also the generated figure
        def on_closing():
            rm.destroy()
            plt.close(self.fig)
        rm.protocol("WM_DELETE_WINDOW", on_closing)

        # BUTTONS
        # play = PhotoImage(file='icons/play.png')
        # stop = PhotoImage(file='icons/stop.png')
        # but_reco = tk.Button(rm, text='🎤', font=('Arial', 100, 'bold'), command=lambda: self.clickHandler())
        but_play = ttk.Button(rm, command=lambda: self.startrecording(), text='Start recording')
        but_stop = ttk.Button(rm, command=lambda: self.stoprecording(rm), text='Stop recording')
        but_help = ttk.Button(rm, command=lambda: hm.createHelpMenu(self, 7), text='🛈', width=2)

        but_play.grid()
        but_stop.grid()
        but_help.grid()

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
        myrecording = np.frombuffer(b"".join(self.frames), dtype=np.int16)
        lenMyRecord = len(myrecording)
        duration = lenMyRecord / self.fs
        time = np.linspace(start=0, stop=duration, num=lenMyRecord)

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        fig, ax = self.fig, self.ax
        self.addLoadButton(fig, ax, self.fs, time, myrecording, rm, 'Recording')
        # rm.destroy()

        # Plot the recording
        ax.plot(time, myrecording)
        fig.canvas.manager.set_window_title('Record')
        ax.set(xlim=[0, duration], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0

        plt.show()

    def addLoadButton(self, fig, ax, fs, time, audio, menu, name):
        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.selectedAudio.shape == (1,): 
                self.cm.createControlMenu(self, name, fs, audio)
            else:
                self.cm.createControlMenu(self, name, fs, self.selectedAudio)
            plt.close(fig)
            menu.destroy()

        # Adds a 'Load' button to the figure
        axload = fig.add_axes([0.8, 0.01, 0.09, 0.05]) # [left, bottom, width, height]
        but_load = Button(axload, 'Load')
        but_load.on_clicked(load)
        axload._but_load = but_load # reference to the Button (otherwise the button does nothing)

        def listenFrag(xmin, xmax):
            ini, end = np.searchsorted(time, (xmin, xmax))
            self.selectedAudio = audio[ini:end+1]
            sd.play(self.selectedAudio, fs)
            
        self.span = SpanSelector(ax, listenFrag, 'horizontal', useblit=True, interactive=True, drag_from_anywhere=True)
