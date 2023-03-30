import tkinter as tk
import os
import wave
import time
import threading
import ctypes
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import Button, SpanSelector

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Record(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.fig, self.ax = plt.subplots()
        self.recording = False
        self.fs = 44100
        self.recordFrag = np.empty(1)
        self.cm = ControlMenu()
        self.recordMenu()

    def recordMenu(self):
        rm = tk.Toplevel()
        rm.resizable(True, True)
        rm.title('Record')
        # rm.iconbitmap('icon.ico')
        rm.wm_transient(self) # Place the toplevel window at the top
        # self.cm.windowGeometry(rm, 850, 250)

        # Adapt the window to different sizes
        for i in range(1):
            rm.columnconfigure(i, weight=1)

        for i in range(2):
            rm.rowconfigure(i, weight=1)

        # BUTTONS
        self.but_reco = tk.Button(rm, text='🎤', font=('Arial', 100, 'bold'), command=lambda: self.clickHandler())
        self.but_reco.grid()

        self.lab_time = ttk.Label(rm, text='00:00')
        self.lab_time.grid()

    def clickHandler(self):
        if self.recording:
            self.recording = False
            self.but_reco.config(fg='black')
        else:
            self.recording = True
            self.but_reco.config(fg='red')
            self.thread = threading.Thread(target=self.record)
            self.thread.setDaemon(True)
            self.thread.start()

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=self.fs, input=True, frames_per_buffer=1024)
        frames = []
        start = time.time()

        while self.recording:
            data = stream.read(1024)
            frames.append(data)

            duration = time.time() - start
            secs = duration % 60
            mins = duration // 60
            self.lab_time.config(text=f"{int(mins):02d}:{int(secs):02d}")

        stream.stop_stream()
        stream.close()
        audio.terminate()
        # self.raise_exception()
        # self.thread.join()

        # Create a wav file with the recorded data
        exists = True
        i = 1
        while exists: 
            if os.path.exists(f"recording{i}.wav"):
                i += 1
            else:
                exists = False
        file = wave.open(f"recording{i}.wav", "wb")
        file.setnchannels(1)
        file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        file.setframerate(self.fs)
        file.writeframes(b"".join(frames))
        file.close()

        wav = wave.open(f"recording{i}.wav", 'rb')
        wav_frames = wav.getnframes()
        wav_time = wav_frames / self.fs
        signal_wave = wav.readframes(-1)
        wav.close()

        self.myrecording = np.frombuffer(signal_wave, dtype=np.int16)
        self.time = np.linspace(0, wav_time, num=wav_frames)

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.recordFrag.shape == (1,): 
                text = "First select a fragment with the left button of the cursor."
                tk.messagebox.showerror(parent=self, title="No fragment selected", message=text) # show error
                return
            plt.close(self.fig)
            self.span.clear()
            # rm.destroy()
            self.cm.createControlMenu(self, 'Record', self.fs, self.recordFrag)

        # Adds a 'Load' button to the figure
        axload = self.fig.add_axes([0.8, 0.01, 0.09, 0.05])
        self.but_load = Button(axload, 'Load')
        self.but_load.on_clicked(load)

        # Plot the recording
        self.ax.plot(self.time, self.myrecording)
        self.fig.canvas.manager.set_window_title('Record')
        self.ax.set(xlim=[0, wav_time], xlabel='Time (s)', ylabel='Amplitude')
        self.ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0

        self.span = SpanSelector(self.ax, self.listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)

        plt.show()

    def listenFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.time, (xmin, xmax))
        self.recordFrag = self.myrecording[ini:end+1]
        sd.play(self.recordFrag, self.fs)

    # def raise_exception(self):
    #     print('hello?')
    #     thread_id = threading.get_ident()
    #     res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) # aqui coge y lo para todo
    #     print('entra')
    #     if res > 1:
    #         ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
    #         print('Exception raise failure')