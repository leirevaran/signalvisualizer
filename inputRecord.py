import tkinter as tk
import time
import threading
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import SpanSelector, Button
from scipy.io.wavfile import write

from controlMenu import ControlMenu

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
        self.selectedAudio = np.empty(1)
        self.cm = ControlMenu()
        self.recordMenu()

    def recordMenu(self):
        rm = tk.Toplevel()
        rm.resizable(False, False)
        rm.title('Record')
        rm.iconbitmap('icons/icon.ico')
        rm.lift() # Place the toplevel window at the top

        # Adapt the window to different sizes
        for i in range(2):
            rm.columnconfigure(i, weight=1)

        for i in range(3):
            rm.rowconfigure(i, weight=1)

        # If the 'generate' menu is closed, close also the generated figure
        def on_closing():
            rm.destroy()
            # plt.close(self.fig)
        rm.protocol("WM_DELETE_WINDOW", on_closing)

        # BUTTONS
        but_play = tk.Button(rm, command=lambda: self.startrecording(but_play, but_stop), text='⏺', font=('Arial', 40, 'bold'))
        but_stop = tk.Button(rm, command=lambda: self.stoprecording(rm, but_play, but_stop), text='⏹', font=('Arial', 40, 'bold'), state='disabled')
        but_help = ttk.Button(rm, command=lambda: self.controller.help.createHelpMenu(self, 7), text='🛈', width=2)

        but_play.grid(column=0, row=0, sticky=tk.EW)
        but_stop.grid(column=1, row=0, sticky=tk.EW)
        but_help.grid(column=0, row=2, sticky=tk.EW, columnspan=2, padx=100, pady=5)

        # TIME LABEL
        self.lab_time = ttk.Label(rm, text='00:00', font=('TkDefaultFont 30'))
        self.lab_time.grid(column=0, row=1, columnspan=2)

    def startrecording(self, but_play, but_stop):
        but_play.config(state='disabled')
        but_stop.config(state='active')
        self.isrecording = True
        t = threading.Thread(target=self.record)
        t.start()

    def stoprecording(self, rm, but_play, but_stop):
        but_play.config(state='active')
        but_stop.config(state='disabled')
        self.fig, self.ax = plt.subplots()
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
        recInt = np.frombuffer(b"".join(self.frames), dtype=np.int16) # it must be int16, not float
        lenMyRecord = len(recInt)
        duration = lenMyRecord / self.fs
        time = np.linspace(start=0, stop=duration, num=lenMyRecord)
        # Convert the recording into float
        write('wav/recording.wav', self.fs, recInt) # generates a wav file in the current folder
        recFloat, _ = sf.read('wav/recording.wav', dtype='float32')

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        fig, ax = self.fig, self.ax
        self.addLoadButton(fig, ax, self.fs, time, recFloat, duration, rm, 'Recording')

        # Plot the recording
        ax.plot(time, recInt)
        fig.canvas.manager.set_window_title('Record')
        ax.set(xlim=[0, duration], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0

        plt.show()

    def addLoadButton(self, fig, ax, fs, time, audio, duration, menu, name):
        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.selectedAudio.shape == (1,): 
                self.cm.createControlMenu(name, fs, audio, duration, self.controller)
            else:
                time = np.arange(0, len(self.selectedAudio)/fs, 1/fs) # time array of the audio
                durSelec = max(time) # duration of the selected fragment
                self.cm.createControlMenu(name, fs, self.selectedAudio, durSelec, self.controller)
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
