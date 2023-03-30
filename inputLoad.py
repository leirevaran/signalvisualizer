import tkinter as tk, tkinter.filedialog
import wave
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
        self.audio, self.audiofs = sf.read(file, dtype='float32')
        self.audiotime = np.arange(0, len(self.audio)/self.audiofs, 1/self.audiofs) # Time axis

        # If the file is stereo (2 channels), convert it to mono (1 channel)
        # We are not using wave.open(file, 'rb') because it gives "wave.Error: unknown format: 3" with some wav files
        with open(file, 'rb') as wav:
            header_beginning = wav.read(0x18)
            wavChannels, = struct.unpack_from('<H', header_beginning, 0x16)
            if wavChannels > 1:
                tk.messagebox.showwarning(title="Stereo file", message="This file is in stereo mode. It will be converted into a mono file.") # show warning
                ampMax = np.ndarray.max(abs(self.audio)) # max amplitude
                self.audio = np.sum(self.audio, axis=1) # from stereo to mono
                self.audio = self.audio * ampMax / np.ndarray.max(abs(self.audio)) # normalize and leave with the max amplitude

        # Plot the audio file
        figFile, axFile = plt.subplots(figsize=(12,5))
        axFile.plot(self.audiotime, self.audio)
        fileName = Path(file).stem # take only the name of the file without the '.wav' and the path
        figFile.canvas.manager.set_window_title(fileName) # set title to the figure window
        axFile.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        axFile.set(xlim=[0, max(self.audiotime)], xlabel='Time (s)', ylabel='Waveform', title='Load an audio file')

        # Select a fragment with the cursor and play the audio of that fragment
        span = SpanSelector(axFile, self.listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)

        # Add a 'Load' button that takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.audioFrag.shape == (1,): # if no fragment has been selected
                text = "First select a fragment with the left button of the cursor."
                tk.messagebox.showerror(parent=self, title="No fragment selected", message=text) # show error
                return
            plt.close(figFile) # close the figure of the waveform
            span.clear()
            self.cm.createControlMenu(self, fileName, self.audiofs, self.audioFrag)

        axload = figFile.add_axes([0.8, 0.01, 0.09, 0.05])
        but_load = Button(axload, 'Load')
        but_load.on_clicked(load)
        
        plt.show() # show the figure

    # Plays the audio of the selected fragment
    def listenFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.audiotime, (xmin, xmax))
        self.audioFrag = self.audio[ini:end+1]
        sd.play(self.audioFrag, self.audiofs)