import tkinter as tk
import wave
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Cursor

class LoadApp(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.loadAudioFile()

    def loadAudioFile(self):
        # Load audio file
        filename = tk.filedialog.askopenfilename(title = "Open file",filetypes = (("wav files","*.wav"),)) # select audio file
        if filename == '': # if no file has been selected
            return

        # Variables of the wav file
        wav = wave.open(filename, 'r')
        self.audio = wav.readframes(-1)
        self.audio, self.audiofs = sf.read(filename, dtype='float32')
        audiotime = np.arange(0, len(self.audio)/self.audiofs, 1/self.audiofs) # Time axe
        
        # Convert from stereo to mono
        if wav.getnchannels() > 1:
            tk.messagebox.showwarning(title="Stereo file", message="This file is in stereo mode. It will be converted into a mono file.") # show warning
            ampMax = np.ndarray.max(abs(self.audio)) # max amplitude
            self.audio = np.sum(self.audio, axis=1) # from stereo to mono
            self.audio = self.audio * ampMax / np.ndarray.max(abs(self.audio)) # normalize and leave with the max amplitude

        # Plot the audio file
        fig, self.ax = plt.subplots(figsize=(12,5))
        self.ax.plot(audiotime, self.audio)
        self.ax.axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        self.ax.set(xlim=[0, max(audiotime)], xlabel='Time (s)', ylabel='Waveform', title='Load an audio file')

        # Add widgets to the figure
        axplay = plt.axes([0.7, 0.01, 0.09, 0.05]) # [eje x, eje y, anchura del boton, altura del boton]
        playButton = Button(axplay, 'Play')
        playButton.on_clicked(self.playSound)
        
        axstop = plt.axes([0.8, 0.01, 0.09, 0.05])
        stopButton = Button(axstop, 'Stop')
        stopButton.on_clicked(self.stopSound)  

        # Selection of a fragment with the cursor
        cursor = Cursor(self.ax, horizOn=False, useblit=True, color='black', linewidth=1)
        self.cid = plt.connect('button_press_event', self.onclick)

        plt.show() # show the figure

    def onclick(self, event):
        if event.inaxes:
            self.ax.axvline(x=event.xdata, color='red')
            plt.disconnect(self.cid)
            self.plotFragment(30000, 50000)

    def playSound(self, event):
        sd.play(self.audio, self.audiofs)

    def stopSound(self, event):
        sd.stop()

    def plotFragment(self, ini, end):
        # Variables of the segment of the waveform
        audioFrag = np.empty(end-ini+1)
        u=0
        for i in range(ini,end+1):
            audioFrag[u] = self.audio[i]
            u+=1
        audiotimeFrag = np.arange(0, len(audioFrag)/self.audiofs, 1/self.audiofs)

        # Plot the waveform and the spectrum of the audio segment
        figFrag, axFrag = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title

        axFrag[0].plot(audiotimeFrag, audioFrag)
        axFrag[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        axFrag[0].set(xlim=[0, max(audiotimeFrag)], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
        axFrag[1].magnitude_spectrum(audioFrag, Fs=self.audiofs, scale='dB', color='C2')
        axFrag[1].set(xlim=[0, max(audiotimeFrag)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum')

        plt.show() # show the figure