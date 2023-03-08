import tkinter as tk, tkinter.filedialog
import wave
import math
import librosa, librosa.display 
import scipy.signal
import parselmouth
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from tkinter import ttk
from tkinter import PhotoImage
from matplotlib import backend_bases
from matplotlib.widgets import Button, Cursor, SpanSelector, MultiCursor
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import Rectangle
from scipy.io.wavfile import write
from pathlib import Path

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Load(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.audioFrag = np.empty(1)
        self.loadAudioFile()

    def loadAudioFile(self):
        # Load audio file
        file = tk.filedialog.askopenfilename(title = "Open file",filetypes = (("wav files","*.wav"),)) # select audio file
        if file == '': # if no file has been selected
            return

        # Variables of the wav file
        wav = wave.open(file, 'r')
        self.audio, self.audiofs = sf.read(file, dtype='float32')
        self.audiotime = np.arange(0, len(self.audio)/self.audiofs, 1/self.audiofs) # Time axis

        # Convert from stereo to mono
        if wav.getnchannels() > 1:
            tk.messagebox.showwarning(title="Stereo file", message="This file is in stereo mode. It will be converted into a mono file.") # show warning
            ampMax = np.ndarray.max(abs(self.audio)) # max amplitude
            self.audio = np.sum(self.audio, axis=1) # from stereo to mono
            self.audio = self.audio * ampMax / np.ndarray.max(abs(self.audio)) # normalize and leave with the max amplitude
        
        # Plot the audio file
        self.figFile, self.axFile = plt.subplots(figsize=(12,5))
        self.axFile.plot(self.audiotime, self.audio)
        self.fileName = Path(file).stem # take only the name of the file without the '.wav' and the path
        self.figFile.canvas.manager.set_window_title(self.fileName) # set title to the figure window
        self.axFile.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        self.axFile.set(xlim=[0, max(self.audiotime)], xlabel='Time (s)', ylabel='Waveform', title='Load an audio file')

        def load(event):
            if self.audioFrag.shape == (1,): # if no fragment has been selected
                text = "First select a fragment with the left button of the cursor."
                tk.messagebox.showerror(parent=self, title="No fragment selected", message=text) # show error
                return
            self.plotFragment()
            plt.close(self.figFile) # close the figure of the waveform
            self.span.clear()
        
        axload = self.figFile.add_axes([0.8, 0.01, 0.09, 0.05])
        but_load = Button(axload, 'Load')
        but_load.on_clicked(load)
        
        # Select a fragment with the cursor and play the audio of that fragment
        self.span = SpanSelector(self.axFile, self.selectFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)
        
        plt.show() # show the figure

    def selectFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.audiotime, (xmin, xmax))
        self.audioFrag = self.audio[ini:end+1]
        sd.play(self.audioFrag, self.audiofs)

    def listenFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.audiotimeFrag, (xmin, xmax))
        audio = self.audioFrag[ini:end+1]
        sd.play(audio, self.audiofs)

    def createSpanSelector(self, ax):
        span = SpanSelector(ax, self.listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)
        return span

    def plotFragment(self):
        # Variables of the segment of the waveform
        self.audiotimeFrag = np.arange(0, len(self.audioFrag)/self.audiofs, 1/self.audiofs)
        self.audioFragDuration = max(self.audiotimeFrag)
        self.audioFragLen = len(self.audioFrag)

        # self.plotFT() # Plot the Fast Fourier Transform (FFT) of the fragment
        # self.createControlMenu() # Open the control menu window
        cm = ControlMenu()
        cm.createControlMenu(self, self.fileName, self.audiofs, self.audioFrag, self.audiotimeFrag, self.audioFragDuration, self.audioFragLen)

    