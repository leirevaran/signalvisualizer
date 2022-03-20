import tkinter as tk
import wave
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Cursor
from matplotlib.backend_bases import MouseButton

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
        fig, ax = plt.subplots(figsize=(12,5))
        ax.plot(audiotime, self.audio)
        plt.title("Load an audio file")
        plt.ylabel("Waveform")
        plt.xlabel("Time (s)")

        # Add widgets to the figure
        axplay = plt.axes([0.7, 0.01, 0.09, 0.05]) # [eje x, eje y, anchura del boton, altura del boton]
        playButton = Button(axplay, 'Play')
        playButton.on_clicked(self.playSound())
        
        axstop = plt.axes([0.8, 0.01, 0.09, 0.05])
        stopButton = Button(axstop, 'Stop')
        stopButton.on_clicked(self.stopSound())

        # Selection of a fragment with the cursor
        cursor = Cursor(ax, horizOn=False, useblit=True, color='black', linewidth=1)

        def on_move(event):
            x, y = event.x, event.y
            if event.inaxes:
                print('data coords %f %f' % (event.xdata, event.ydata))
                self.begin = ax.axvline(x=event.xdata, color='red')
                self.end = ax.axvline(x=event.xdata, color='red')
                print(self.begin)
                print(self.end)

        plt.connect('button_press_event', on_move)

        plt.show()

    def playSound(self):
        sd.play(self.audio, self.audiofs)

    def stopSound(self):
        sd.stop()