import tkinter as tk
import wave
import soundfile as sf
import sounddevice as sd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LoadApp(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.geometry('900x600')
        master.resizable(True, True)

        # creation of widgets
        self.loadButton = tk.Button(self, text="Load audio", command=lambda: self.loadAudioFile())
        self.playButton = tk.Button(self, text="Play audio", command=lambda: self.playSound())
        self.playButton.configure(state="disabled")
        #self.playButton.grid(row=1,column=8)

        # add the widgets to the frame
        self.loadButton.pack() 
        self.playButton.pack()

        # creation of graph for the waveform
        # fig = plt.figure()
        # fig.subplots_adjust(top=0.8)
        # ax1 = fig.add_subplot(211)
        # ax1.set_xlabel('Time')
        # ax1.set_ylabel('Waveform')
        # self.canvas = FigureCanvasTkAgg(fig, master) # Convert the Figure to a tkinter widget
        # self.canvas.get_tk_widget().pack() # Show the widget on the screen
        # #self.__new__canvas.draw() # Draw the graph on the canvas?

        """Prueba Eder"""
        # Create plot axis
        # Redefine subplot parameters
        matplotlib.rcParams["figure.subplot.top"] = 0.98 # Top margin: 98%
        matplotlib.rcParams["figure.subplot.bottom"] = 0.02 # Bottom margin: 2%
        matplotlib.rcParams["figure.subplot.hspace"] = 0.99 # Vertical space betweenplots: 99%

        # So the labels plot is smaler than the signal plots, at first 18 subplots are going to be created        
        self.fig, auxAx = plt.subplots(ncols=1,nrows=18)
        # From those 18 subplots, the 0 is going to be for label plot
        # The 1 is going to be deleted, so leave a gap between the label plot and the audio plot
        # The plots 2, 6, 10, 14 are for the signal plots. They are going to be expanded over their 4 following subplots
        gs = []
        gs.append(auxAx[2].get_gridspec())
        gs.append(auxAx[6].get_gridspec())
        gs.append(auxAx[10].get_gridspec())
        gs.append(auxAx[14].get_gridspec())
        # Delete all axes except the first one (label plot)
        for ax in auxAx[1:]:
            ax.remove()
        # Create expanded subplots, and add them to the ax variable of the app
        # All of them have the x data linked to auxAx[0], so all of them can zoom together
        self.ax = []
        self.ax.append(self.fig.add_subplot(gs[0][2:5])) # ax[0] -> Audio plot
        self.ax.append(self.fig.add_subplot(gs[1][6:9])) # ax[1] -> EMG signal 1
        self.ax.append(self.fig.add_subplot(gs[2][10:13])) # ax[2] -> EMG signal 2
        self.ax.append(self.fig.add_subplot(gs[3][14:17])) # ax[3] -> EMG signal 3
        self.ax.append(auxAx[0]) # ax[4] -> labelplot

        self.ax[0].set_title('Audio',fontsize="small")
        self.ax[1].set_title('EMG Signal 1',fontsize="small")
        self.ax[2].set_title('EMG Signal 2',fontsize="small")
        self.ax[3].set_title('EMG Signal 3',fontsize="small")

        self.fig.tight_layout() # Adjust the padding between and around subplots
                
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()
        """Fin prueba Eder"""

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

        """Prueba Eder"""
        audioData = np.load(filename)
        self.audioSyncSignal = audioData[:,1]
        self.audiot = np.arange(0.000,len(audioData)/self.audiofs,1/self.audiofs) # Time axe

        self.ax[0].clear()

        # Draw a rectangle that remarks the range where sync signal is active
        max_index = int(np.argmax(self.audioSyncSignal)) # The sync signal that goes in the audio has a maximum where the active zone starts
        min_index = int(np.argmin(self.audioSyncSignal)) # And a minimum where it ends
        rect = Rectangle((self.audiot[max_index],-1),self.audiot[min_index]-self.audiot[max_index],2, facecolor='#ccc')
        self.ax[0].add_patch(rect)

        # And plot the normalized audio data over the rectangle
        self.ax[0].plot(self.audiot,self.audioData)
        self.ax[0].set_xlim(0,np.max(self.audiot))
        #self.ax[4].set_xlim(0,np.max(self.audiot))

        self.ax[0].set_title("Audio",fontsize="small")
        self.ax[0].set_ylabel('Signal',fontsize="small")
        self.ax[0].set_xlabel('Time',fontsize="small")

        self.canvas.draw()
        """Fin prueba Eder"""
        
        #self.canvas.draw(wav)
        
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