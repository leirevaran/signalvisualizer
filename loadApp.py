from re import X
import tkinter as tk
import wave
import soundfile as sf
import sounddevice as sd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LoadApp(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        master.geometry('900x600')
        master.resizable(True, True)
        self.master.title("Load audio file")

        self.pack()
        self.create_widgets()
    
    def create_widgets(self):
        # Create plot axis
        self.fig = plt.figure(figsize=(2, 2))
        auxAx = self.fig.add_subplot(111)
        
        # Create expanded subplots, and add them to the ax variable of the app
        self.ax = []
        self.ax.append(auxAx)

        self.canvas = FigureCanvasTkAgg(self.fig, self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.X)

        # Labels
        self.loadLabel = tk.Label(self, text="Load audio file")
        self.loadLabel.pack()

        # Buttons
        self.loadButton = tk.Button(self, text="Load audio", command=lambda: self.loadAudioFile())
        #self.loadButton.grid(row=2,column=0)
        self.loadButton.pack()
        
        self.playButton = tk.Button(self, text="Play audio", command=lambda: self.playSound())
        self.playButton.configure(state="disabled")
        #self.playButton.grid(row=2,column=9)
        self.playButton.pack()

    def loadAudioFile(self):
        # Load audio file
        filename = tk.filedialog.askopenfilename(title = "Open file",filetypes = (("wav files","*.wav"),)) # select audio file
        if filename == '': # if no file has been selected
            return

        # Variables of the wav file
        wav = wave.open(filename, 'r')
        nchannels, sampwidth, framerate, nframes, _, _ = wav.getparams()
        self.audioData, self.audiofs = sf.read(filename, dtype='float32')
        self.audiot = np.arange(0.000,len(self.audioData)/self.audiofs,1/self.audiofs) # Time axe
        
        # Convert from stereo to mono
        if nchannels > 1:
            tk.messagebox.showwarning(title="Stereo file", message="This file is in stereo mode. It will be converted into a mono file.") # show warning
            ampMax = np.ndarray.max(abs(self.audioData)) # max amplitude
            self.audioData = np.sum(self.audioData, axis=1) # from stereo to mono
            self.audioData = self.audioData * ampMax / np.ndarray.max(abs(self.audioData)) # normalize and leave with the max amplitude

        # Plot the waveform of the file in the existing axes
        self.ax[0].clear()

        self.ax[0].plot(self.audiot,self.audioData)
        self.ax[0].set_xlim(0,np.max(self.audiot))

        self.ax[0].set_title("Audio",fontsize="small")
        self.ax[0].set_ylabel('Waveform',fontsize="small")
        self.ax[0].set_xlabel('Time (s)',fontsize="small")

        self.canvas.draw()

        # Active the audio-related buttons of the interface
        self.playButton.configure(state="active")

        self.durationLabel = tk.Label(self, text="Duration (s): ")
        self.durationText = tk.Text(self, height = 1, width = 10)
        self.durationText.insert(tk.END, self.audiot[len(self.audiot)-1])
        self.durationLabel.pack()
        self.durationText.pack()

        self.fsLabel = tk.Label(self, text="Fs (Hz): ")
        self.fsText = tk.Text(self, height = 1, width = 10)
        self.fsText.insert(tk.END, self.audiofs)
        self.fsLabel.pack()
        self.fsText.pack()

    def playSound(self):
        sd.play(self.audioData, self.audiofs)