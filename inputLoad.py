import tkinter as tk, tkinter.filedialog
import struct
import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, SpanSelector
from pathlib import Path

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Load(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.selectedAudio = np.empty(1)
        self.cm = ControlMenu()
        self.loadAudio()

    def loadAudio(self):
        # Ask the user to select a .wav file
        file = tk.filedialog.askopenfilename(title="Open file", initialdir='library/', filetypes=(("wav files","*.wav"),)) # select audio file
        if file == '': # if no file has been selected
            return

        audio, fs = sf.read(file, dtype='float32')

        # If the file is stereo (2 channels), convert it to mono (1 channel)
        # We are not using wave.open(file, 'rb') because it gives "wave.Error: unknown format: 3" with some wav files
        with open(file, 'rb') as wav:
            header_beginning = wav.read(0x18)
            wavChannels, = struct.unpack_from('<H', header_beginning, 0x16)
            if wavChannels > 1:
                tk.messagebox.showwarning(title="Stereo file", message="This file is in stereo mode. It will be converted into a mono file.") # show warning
                ampMax = np.ndarray.max(abs(audio)) # max amplitude
                audio = np.sum(audio, axis=1) # from stereo to mono
                audio = audio * ampMax / np.ndarray.max(abs(audio)) # normalize and leave with the max amplitude
        
        self.plotAudio(file, audio, fs)

    def plotAudio(self, file, audio, fs):
        figFile, axFile = plt.subplots(figsize=(12,5))
        fileName = Path(file).stem # take only the name of the file without the '.wav' and the path
        figFile.canvas.manager.set_window_title(fileName) # set title to the figure window
        
        time = np.arange(0, len(audio)/fs, 1/fs) # Time axis
        duration = librosa.get_duration(filename=file)
        self.addLoadButton(figFile, axFile, fs, time, audio, duration, fileName)

        # Plot the audio file
        axFile.plot(time, audio)
        axFile.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        axFile.set(xlim=[0, max(time)], xlabel='Time (s)', ylabel='Waveform', title='Load an audio file')

        plt.show() # show the figure

    def addLoadButton(self, fig, ax, fs, time, audio, duration, name):
        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.selectedAudio.shape == (1,): 
                self.cm.createControlMenu(name, fs, audio, duration, self.controller)
            else:
                time = np.arange(0, len(self.selectedAudio)/fs, 1/fs) # time array of the audio
                durSelec = max(time) # duration of the selected fragment
                self.cm.createControlMenu(name, fs, self.selectedAudio, durSelec, self.controller)
            plt.close(fig)

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