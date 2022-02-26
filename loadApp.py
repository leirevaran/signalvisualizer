import tkinter as tk
import wave
import soundfile as sf
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LoadApp(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # creation of widgets
        self.loadButton = tk.Button(self, text="Load audio", command=lambda: self.loadAudioFile())
        self.playButton = tk.Button(self, text="Play audio", command=lambda: self.playSound())
        self.playButton.configure(state="disabled")
        #self.playButton.grid(row=1,column=8)

        # add the widgets to the frame
        self.loadButton.pack() 
        self.playButton.pack()

        # creation of graph for the waveform
        fig = plt.figure()
        fig.subplots_adjust(top=0.8)
        ax1 = fig.add_subplot(211)
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Waveform')
        self.canvas = FigureCanvasTkAgg(fig, master) # Convert the Figure to a tkinter widget
        self.canvas.get_tk_widget().pack() # Show the widget on the screen
        #self.__new__canvas.draw() # Draw the graph on the canvas?

    def loadAudioFile(self):
        # load audio file
        filename = tk.filedialog.askopenfilename(title = "Open file",filetypes = (("wav files","*.wav"),)) # select audio file
        if filename == '': # if no file has been selected
            return

        wav = wave.open(filename, 'r')
        nchannels, sampwidth, framerate, nframes, _, _ = wav.getparams()
        self.audioData, self.audiofs = sf.read(filename, dtype='float32')
        
        # if it is a stereo audio, show a warning and mix both chanels to create a single mono audio
        if nchannels > 1:
            tk.messagebox.showwarning(title="Stereo file", message="This file is in stereo mode. It will be converted into a mono file.") # show warning
            ampMax = np.ndarray.max(abs(self.audioData)) # max amplitude
            self.audioData = np.sum(self.audioData, axis=1) # from stereo to mono
            self.audioData = self.audioData * ampMax / np.ndarray.max(abs(self.audioData)) # normalize and leave with the max amplitude

        self.canvas.draw(wav)
        
        # sig = np.frombuffer(wav.readframes(nframes), dtype=np.int16)
        # sig = sig[:]
        # plt.figure(1)

        # plot waveform
        # plot = plt.subplot(211)
        # plot.plot(sig)
        # plot.set_xlabel('Time (ms)')
        # plot.set_ylabel('Waveform')

        # plt.show()

    def playSound(self):
        sd.play(self.audioData, self.audiofs)