import tkinter as tk, tkinter.filedialog
import struct
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
        self.audioFrag = np.empty(1)
        self.cm = ControlMenu()
        self.loadAudioFile()

    def loadAudioFile(self):
        # Ask the user to select a .wav file
        file = tk.filedialog.askopenfilename(title="Open file", filetypes=(("wav files","*.wav"),)) # select audio file
        if file == '': # if no file has been selected
            return

        # Variables of the wav file
        audio, fs = sf.read(file, dtype='float32')
        time = np.arange(0, len(audio)/fs, 1/fs) # Time axis

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

        # Plot the audio file
        figFile, axFile = plt.subplots(figsize=(12,5))
        axFile.plot(time, audio)
        fileName = Path(file).stem # take only the name of the file without the '.wav' and the path
        figFile.canvas.manager.set_window_title(fileName) # set title to the figure window
        axFile.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        axFile.set(xlim=[0, max(time)], xlabel='Time (s)', ylabel='Waveform', title='Load an audio file')

        # Add a 'Load' button that takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.audioFrag.shape == (1,): # if no fragment has been selected, load the whole signal
                self.cm.createControlMenu(self, fileName, fs, audio)
            else:
                self.cm.createControlMenu(self, fileName, fs, self.audioFrag)
            plt.close(figFile) # close the figure of the waveform

        axload = figFile.add_axes([0.8, 0.01, 0.09, 0.05])
        but_load = Button(axload, 'Load')
        but_load.on_clicked(load)
        axload._but_save = but_load # reference to the Button (otherwise the button does nothing)

        # Plays the audio of the selected fragment
        def listenFragment(xmin, xmax):
            ini, end = np.searchsorted(time, (xmin, xmax))
            self.audioFrag = audio[ini:end+1]
            sd.play(self.audioFrag, fs)
        
        # Select a fragment with the cursor and play the audio of that fragment
        self.span = SpanSelector(axFile, listenFragment, 'horizontal', useblit=True, interactive=True, drag_from_anywhere=True)
        
        plt.show() # show the figure