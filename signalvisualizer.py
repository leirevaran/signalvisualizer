import tkinter as tk
import tkinter.filedialog
import wave
import math
import librosa
import parselmouth
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib import backend_bases
from matplotlib.widgets import Button, Cursor, SpanSelector, MultiCursor
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import Rectangle
from scipy.io.wavfile import write

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Start(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames on top of each other, 
        # then the one we want visible will be raised above the others
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames["SignalVisualizer"] = SignalVisualizer(master=self.container, controller=self)
        self.frames["SignalVisualizer"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("SignalVisualizer")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

        menubar = frame.createMenuBar(self)
        self.configure(menu=menubar)

class SignalVisualizer(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.controller.geometry('710x420') # size of the window
        self.controller.title("Signal Visualizer")
        #self.createWindowButtons()

        # Delete two options of the toolbar of the figures. This must be done before the figures are created
        backend_bases.NavigationToolbar2.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to  previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
        )

    def createMenuBar(self, root):
        # the menu bar will be at the top of the window
        menubar = tk.Menu(root)
        
        # creation of the options in the menu bar
        signalmenu = tk.Menu(menubar, tearoff=0) # tearoff=0 to avoid useless lines
        signalmenu.add_command(label="Info")
        signalmenu.add_command(label="Exit", command=root.quit)

        generatemenu = tk.Menu(menubar, tearoff=0)
        generatemenu.add_command(label="Pure tone")
        generatemenu.add_command(label="Free addition of pure tones")
        generatemenu.add_command(label="Noise")

        knownmenu = tk.Menu(generatemenu, tearoff=0)
        knownmenu.add_command(label="Square wave")
        knownmenu.add_command(label="Sawtooth wave")
        knownmenu.add_command(label="Rosenberg pulse")

        inputmenu = tk.Menu(menubar, tearoff=0)
        inputmenu.add_command(label="Load", command=lambda: self.loadAudioFile())
        inputmenu.add_command(label="Record")

        optionsmenu = tk.Menu(menubar, tearoff=0)
        optionsmenu.add_command(label="General")
        optionsmenu.add_command(label="Signal")
        optionsmenu.add_command(label="Spectrogram")

        # adding the options created to the menu bar
        menubar.add_cascade(label="Signal Visualizer", menu=signalmenu)
        menubar.add_cascade(label="Generate", menu=generatemenu)
        generatemenu.add_cascade(label="Known periodic signals", menu=knownmenu)
        menubar.add_cascade(label="Input", menu=inputmenu)
        menubar.add_cascade(label="Options", menu=optionsmenu)

        return menubar

    # def createWindowButtons(self):
    #     w1Button = tk.Button(self, text="Window1", command=lambda: self.controller.show_frame('LoadApp')) # with lambda, the action is only made when the button is pressed
    #     w1Button.configure(state="disabled")
    #     w1Button.grid()

    def loadAudioFile(self):
        # Load audio file
        filename = tk.filedialog.askopenfilename(title = "Open file",filetypes = (("wav files","*.wav"),)) # select audio file
        if filename == '': # if no file has been selected
            return

        # Variables of the wav file
        wav = wave.open(filename, 'r')
        self.audio, self.audiofs = sf.read(filename, dtype='float32')
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
        self.figFile.canvas.manager.set_window_title('Audio file') # set title to the figure window
        self.axFile.axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        self.axFile.set(xlim=[0, max(self.audiotime)], xlabel='Time (s)', ylabel='Waveform', title='Load an audio file')

        # Add play and stop buttons to the figure
        def playSound(event):
            sd.play(self.audio, self.audiofs)

        def stopSound(event):
            sd.stop()

        axPlay = plt.axes([0.8, 0.01, 0.09, 0.05]) # [x axis, y axis, width, height]
        playBtn = Button(axPlay, '', image=plt.imread('images/play.png'))
        playBtn.on_clicked(playSound)

        axStop = plt.axes([0.84, 0.01, 0.09, 0.05])
        stopBtn = Button(axStop, '', image=plt.imread('images/stop.png'))
        stopBtn.on_clicked(stopSound)
        
        # Select a fragment with the cursor
        cursor = Cursor(self.axFile, horizOn=False, useblit=True, color='black', linewidth=1)
        span = SpanSelector(self.axFile, self.selectFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='red'))
        
        plt.show() # show the figure

    def selectFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.audiotime, (xmin, xmax))
        self.plotFragment(ini, end)
        plt.close(self.figFile) # close the figure of the waveform

    def plotFragment(self, ini, end):
        # Variables of the segment of the waveform
        self.audioFrag = self.audio[ini:end+1]
        self.audiotimeFrag = np.arange(0, len(self.audioFrag)/self.audiofs, 1/self.audiofs)
        self.audioFragDuration = max(self.audiotimeFrag)
        self.audioFragLen = len(self.audioFrag)

        self.plotFT() # Plot the Fast Fourier Transform (FFT) of the fragment
        self.createControlMenu() # Open the control menu window

    # Plots the waveform and the spectrum of the Fast Fourier Transform (FFT) of the fragment
    def plotFT(self):
        self.figFragFT, self.axFragFT = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        self.figFragFT.canvas.manager.set_window_title('FT')

        fft = np.fft.fft(self.audioFrag) / self.audioFragLen # Normalize amplitude
        fft2 = fft[range(int(self.audioFragLen/2))] # Exclude sampling frequency
        values = np.arange(int(self.audioFragLen/2))
        frequencies = values / (self.audioFragLen/self.audiofs) # values / time period

        self.axFragFT[0].plot(self.audiotimeFrag, self.audioFrag)
        self.axFragFT[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        self.axFragFT[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
        self.axFragFT[1].plot(frequencies, 20*np.log10(abs(fft2)))
        self.axFragFT[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum of the Fourier Transform')

        # TO-DO: connect figFrag with w1Button in signalVisualizer

        self.figFragFT.show() # show the figure

    def createControlMenu(self):
        cm = tk.Toplevel()
        cm.geometry('726x472')
        cm.resizable(False, False)
        cm.title('Control menu')
        cm.iconbitmap('images/icon.ico')

        # METHODS
        # Updates the OptionMenu 'om' with the option list 'opt' and variable 'var' passed as a parameter
        def updateOptionMenu(om, var, opt):
            menu = om["menu"]
            menu.delete(0, "end")
            for o in opt:
                menu.add_command(label=o, command=lambda value=o: var.set(value))
            var.set(opt[0])

        # Called when changing the main option (FT, STFT, etc.) for disabling or activating widgets
        def displayOptions(choice):
            choice = cm.var_opts.get()
            # Reset widgets
            opt_nfft = [2**11, 2**12, 2**13, 2**14, 2**15, 2**16, 2**17, 2**18, 2**19, 2**20, 2**21, 2**22, 2**23]
            updateOptionMenu(dd_nfft, cm.var_nfft, opt_nfft)
            cm.var_size.set('0.09')
            cm.var_over.set('0')
            cm.var_minf.set('0')
            cm.var_maxf.set(self.audiofs/2)
            cm.var_fund.set('0')
            cm.var_cent.set('0')
            cm.var_cut1.set('0')
            cm.var_cut2.set('0')

            if choice == 'FT' or choice == 'Filtering' or choice == 'STFT': 
                ent_over.config(state='disabled')
            else: ent_over.config(state='normal')

            if choice == 'FT' or choice == 'Filtering': 
                ent_size.config(state='disabled')
            else: ent_size.config(state='normal')

            if choice == 'Filtering':
                ent_fund.config(state='normal')
                ent_cent.config(state='normal')
                ent_cut1.config(state='normal')
                ent_cut2.config(state='normal')
                dd_filt.config(state='active')
                but_freq.configure(state='active')
                but_rese.configure(state='active')
                but_fisi.configure(state='active')
            else:
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_filt.config(state='disabled')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                but_fisi.configure(state='disabled')

            if choice == 'Pitch':
                dd_meth.config(state='active')
                but_adse.config(state='active')
            else:
                dd_meth.config(state='disabled')
                but_adse.config(state='disabled')

            if choice == 'Spectrogram': 
                chk_form.config(state='active')
            else: chk_form.config(state='disabled')

            if choice == 'Spectrogram' or choice == 'STFT + Spect' or choice == 'Spectral Centroid' or choice == 'Filtering':
                ent_minf.config(state='normal')
                ent_maxf.config(state='normal')
            else:
                ent_minf.config(state='disabled')
                ent_maxf.config(state='disabled')

            if choice == 'STFT' or choice == 'Spectrogram' or choice == 'STFT + Spect' or choice == 'Spectral Centroid':
                dd_wind.config(state='active')
            else: dd_wind.config(state='disabled')

            if choice == 'STFT' or choice == 'Spectrogram' or choice == 'STFT + Spect':
                dd_nfft.config(state='active')
            else: dd_nfft.config(state='disabled')

        # Called when inserting a value in the entry of the window length and pressing enter
        def windowLengthEntry(event):
            # Show an error and stop if the inserted window size is incorrect
            windSize = float(ent_size.get())
            overlap = float(ent_over.get())
            if windSize > self.audioFragDuration or windSize == 0:
                # Reset widgets
                cm.var_size.set('0.09')
                cm.opt_nfft = [2**11, 2**12, 2**13, 2**14, 2**15, 2**16, 2**17, 2**18, 2**19, 2**20, 2**21, 2**22, 2**23]
                updateOptionMenu(dd_nfft, cm.var_nfft, cm.opt_nfft)
                if windSize > self.audioFragDuration: # The window size can't be greater than the duration of the signal
                    text = "The window size can't be greater than the duration of the signal (" + str(self.audioFragDuration) + "s)."
                    tk.messagebox.showerror(parent=cm, title="Window size too long", message=text) # show error
                elif windSize == 0: # The window size must be a positive number
                    tk.messagebox.showerror(parent=cm, title="Wrong window size value", message="The chosen value for the window size must be a positive number.") # show error
            elif overlap >= windSize: # The window size must always be greater than the overlap
                text2 = "The window size must always be greater than the overlap (" + str(overlap) + "s)."
                tk.messagebox.showerror(parent=cm, title="Wrong overlap value", message=text2) # show error
                cm.var_over.set('0')
            # Change the values of nfft to be always greater than the window size
            else: 
                windSizeSamp = windSize * self.audiofs # window size in samples
                nfft = cm.opt_nfft[0] # the smallest value of the nfft list
                if nfft < windSizeSamp: # Deletes smallest values of the nfft list and adds greater ones
                    last = int(math.log2(cm.opt_nfft[len(cm.opt_nfft)-1])) + 1
                    first = int(math.log2(nfft))
                    while 2**first < windSizeSamp:
                        for a in range(len(cm.opt_nfft)-1):
                            cm.opt_nfft[a] = cm.opt_nfft[a+1]
                        cm.opt_nfft[len(cm.opt_nfft)-1] = 2**last
                        last += 1
                        first += 1
                    updateOptionMenu(dd_nfft, cm.var_nfft, cm.opt_nfft)
                else: # Adds smaller values to the nfft list if possible
                    first = int(math.log2(nfft)) - 1
                    while 2**first > windSizeSamp:
                        for a in range(len(cm.opt_nfft)-1, 0, -1):
                            cm.opt_nfft[a] = cm.opt_nfft[a-1]
                        cm.opt_nfft[0] = 2**first
                        first -= 1
                    updateOptionMenu(dd_nfft, cm.var_nfft, cm.opt_nfft)
            
        def overlapEntry(event):
            # Show an error and stop if the inserted overlap is incorrect
            overlap = float(ent_over.get())
            windSize = float(ent_size.get())
            if overlap > self.audioFragDuration or overlap >= windSize:
                cm.var_over.set('0') # Reset widget
                if overlap > self.audioFragDuration: # The overlap can't be greater than the duration of the signal
                    text = "The overlap can't be greater than the duration of the signal (" + str(self.audioFragDuration) + "s)."
                    tk.messagebox.showerror(parent=cm, title="Overlap too long", message=text) # show error
                elif overlap >= windSize: # The overlap must always be smaller than the window size
                    text2 = "The overlap must always be smaller than the window size (" + str(windSize) + "s)."
                    tk.messagebox.showerror(parent=cm, title="Wrong overlap value", message=text2) # show error

        def minfreqEntry(event):
            # The minimum frequency must be >= 0 and smaller than the maximum frequency
            minfreq = float(ent_minf.get())
            maxfreq = float(ent_maxf.get())
            if minfreq >= maxfreq:
                cm.var_minf.set('0') # Reset widget
                text = "The minimum frequency must be smaller than the maximum frequency (" + str(maxfreq) + "Hz)."
                tk.messagebox.showerror(parent=cm, title="Minimum frequency too big", message=text) # show error

        def maxfreqEntry(event):
            # The maximum frequency must be <= self.audiofs/2 and greater than the minimum frequency
            minfreq = float(ent_minf.get())
            maxfreq = float(ent_maxf.get())
            if maxfreq > self.audiofs/2 or maxfreq <= minfreq:
                cm.var_maxf.set(self.audiofs/2) # Reset widget
                if maxfreq > self.audiofs/2:
                    text = "The maximum frequency can't be greater than the half of the sample frequency (" + str(self.audiofs/2) + "Hz)."
                    tk.messagebox.showerror(parent=cm, title="Maximum frequency too big", message=text) # show error
                elif maxfreq <= minfreq:
                    text = "The maximum frequency must be greater than the minimum frequency (" + str(minfreq) + "Hz)."
                    tk.messagebox.showerror(parent=cm, title="Maximum frequency too small", message=text) # show error

            
        # Called when inserting something in an entry. Only lets the user enter numbers or '.'
        def onValidate(s, S):
            if S.isdigit() or (S == '.' and s.isdigit()): # Before '.' always a number
                return True
            else:
                return False

        # Called when clicking the 'Formants' checkbox
        def showFormants():
            pass

        # Called when pressing the 'Plot' button
        def plotFigure():
            # VALUES GIVEN BY THE USER
            choice = cm.var_opts.get()
            windType = cm.var_wind.get()
            windSize = float(ent_size.get()) # window size in seconds
            nfftUser = cm.var_nfft.get()
            overlap = float(ent_over.get()) # overlap in seconds
            # Spectrogram
            minfreq = cm.var_minf.get()
            maxfreq = cm.var_maxf.get()
            formants = cm.var_form.get() # returns 1 if activated, 0 if not
            # Pitch
            method = cm.var_meth.get()
            dataop = cm.var_data.get()
            # Filtering
            fundfreq = cm.var_fund.get()
            centfreq = cm.var_cent.get()
            fcut1 = cm.var_cut1.get()
            fcut2 = cm.var_cut2.get()

            windSizeSamp = windSize * self.audiofs # window size in samples
            windSizeSampInt = int(windSizeSamp)
            overlapSamp = overlap * self.audiofs # overlap in samples (float)

            # Apply the window type to the window
            if windType == 'Bartlett':
                window = np.bartlett(windSizeSampInt)
            elif windType == 'Blackman':
                window = np.blackman(windSizeSampInt)
            elif windType == 'Hamming':
                window = np.hamming(windSizeSampInt)
            elif windType == 'Hanning':
                window = np.hanning(windSizeSampInt)
            elif windType == 'Kaiser':
                window = np.kaiser(windSizeSampInt) # np.kaiser(windSizeSampInt, float:shape parameter for window)
            
            if choice == 'FT':
                if plt.fignum_exists(self.figFragFT.number):
                    plt.close(self.figFragFT.number) # close the figure of the FT
                self.plotFT() # create the figure of the FT (again)

            elif choice == 'STFT' or choice == 'STFT + Spect' or choice == 'Spectral Centroid':
                # The window is in the middle of the waveform by default
                midPoint_idx = int(self.audioFragLen/2) # index of the middle point in the waveform
                midPoint = self.audiotimeFrag[midPoint_idx] # value of the middle point

                # Define initial and end points of the window
                ini_idx = midPoint_idx - int(windSizeSamp/2) # index of the initial point
                end_idx = midPoint_idx + int(windSizeSamp/2) # index of the end point
                if ini_idx < 1: ini_idx = 0
                if end_idx > self.audioFragLen: end_idx = self.audioFragLen-1

                # Draw the window in the waveform as a rectangle
                ini = self.audiotimeFrag[ini_idx] # value of the initial point
                end = self.audiotimeFrag[end_idx] # value of the end point
                rectangle = Rectangle(xy=(ini,min(self.audioFrag)), width=end-ini, height=max(self.audioFrag), color='silver')

                audioFragWind = self.audioFrag[ini_idx:end_idx]
                audioFragWind2 = audioFragWind * window
                stft = np.fft.fft(audioFragWind2, nfftUser)
                stft2 = stft[range(int(nfftUser/2))]
                values = np.arange(int(nfftUser/2))
                frequencies = values * self.audiofs / nfftUser

                if choice == 'STFT':
                    figFragSTFT, axFragSTFT = plt.subplots(2, figsize=(12,6))
                    plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
                    figFragSTFT.canvas.manager.set_window_title('STFT') # set title to the figure window

                    midLine = axFragSTFT[0].axvline(x=midPoint, color='black', linewidth='1', fillstyle='full') # line in the middle
                    axFragSTFT[0].add_artist(rectangle) # draw the rectangle

                    axFragSTFT[0].plot(self.audiotimeFrag, self.audioFrag)
                    axFragSTFT[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                    axFragSTFT[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                    line1, = axFragSTFT[1].plot(frequencies, 20*np.log10(abs(stft2)))
                    axFragSTFT[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum of the Short Time Fourier Transform')

                    cursorSTFT = Cursor(axFragSTFT[0], horizOn=False, useblit=True, color='black', linewidth=1)

                elif choice == 'STFT + Spect':
                    figFragSTFTSpect, axFragSTFTSpect = plt.subplots(3, figsize=(12,6))
                    plt.subplots_adjust(hspace=.6) # to avoid overlapping between xlabel and title
                    figFragSTFTSpect.canvas.manager.set_window_title('STFT + Spectrogram') # set title to the figure window

                    midLineWavef = axFragSTFTSpect[0].axvline(x=midPoint, color='black', linewidth='1', fillstyle='full') # line in the middle (waveform)
                    midLineSpect = axFragSTFTSpect[2].axvline(x=midPoint, color='black', linewidth='1', fillstyle='full') # line in the middle (spectrogram)
                    axFragSTFTSpect[0].add_artist(rectangle) # draw the rectangle

                    axFragSTFTSpect[0].plot(self.audiotimeFrag, self.audioFrag)
                    axFragSTFTSpect[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                    axFragSTFTSpect[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                    line1, = axFragSTFTSpect[1].plot(frequencies, 20*np.log10(abs(stft2)))
                    axFragSTFTSpect[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum of the Short Time Fourier Transform')
                    axFragSTFTSpect[2].specgram(x=self.audioFrag, Fs=self.audiofs, window=window, pad_to=nfftUser, NFFT=windSizeSampInt, mode='magnitude', noverlap=overlapSamp, scale='dB')
                    axFragSTFTSpect[2].set(xlim=[0, self.audioFragDuration], ylim=[minfreq, maxfreq], xlabel='Time (s)', ylabel='Frequency (Hz)', title='Spectrogram')

                    cursorSTFTSpect = MultiCursor(figFragSTFTSpect.canvas, (axFragSTFTSpect[0], axFragSTFTSpect[2]), color='black', lw=1)

                else: # choice == Spectral Centroid
                    figFragSC, axFragSC = plt.subplots(3, figsize=(12,6))
                    plt.subplots_adjust(hspace=.6) # to avoid overlapping between xlabel and title
                    figFragSC.canvas.manager.set_window_title('Spectral Centroid') # set title to the figure window

                    midLineWavefSC = axFragSC[0].axvline(x=midPoint, color='black', linewidth='1', fillstyle='full') # line in the middle (waveform)
                    midLineSpectSC = axFragSC[2].axvline(x=midPoint, color='black', linewidth='1', fillstyle='full') # line in the middle (spectrogram)
                    axFragSC[0].add_artist(rectangle) # draw the rectangle

                    # TO-DO

                    axFragSC[0].plot(self.audiotimeFrag, self.audioFrag)
                    axFragSC[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                    axFragSC[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                    line1, = axFragSC[1].plot() # TO-DO
                    axFragSC[1].set(xlim=[0, max()], xlabel='Frequency (Hz)', ylabel='Power/Frequency (dB/Hz)', title='Power spectral density using fft')
                    axFragSC[2].specgram(x=self.audioFrag, Fs=self.audiofs, window=window, pad_to=nfftUser, NFFT=windSizeSampInt, mode='magnitude', noverlap=overlapSamp, scale='dB')
                    axFragSC[2].set(xlim=[0, self.audioFragDuration], ylim=[minfreq, maxfreq], xlabel='Time (s)', ylabel='Frequency (Hz)', title='Spectrogram')

                    cursorSC = MultiCursor(figFragSC.canvas, (axFragSC[0], axFragSC[2]), color='black', lw=1)

                # If the user changes the position of the window, recalculate the STFT
                def on_click(event):
                    # if the user does left click in the waveform
                    if event.button is MouseButton.LEFT and (choice == 'STFT' and event.inaxes == axFragSTFT[0]) or (choice == 'STFT + Spect' and event.inaxes == axFragSTFTSpect[0]) or (choice == 'Spectral Centroid' and event.inaxes == axFragSC[0]):
                        # Define the new initial and end points of the window
                        new_midPoint = event.xdata
                        new_midPoint_idx = midPoint_idx
                        for i in range(self.audioFragLen-1):
                            if self.audiotimeFrag[i] == new_midPoint or (self.audiotimeFrag[i] < new_midPoint and self.audiotimeFrag[i+1] > new_midPoint):
                                new_midPoint_idx = i
                                break
                        new_ini_idx = new_midPoint_idx - int(windSizeSamp/2)
                        new_end_idx = new_midPoint_idx + int(windSizeSamp/2)
                        if new_ini_idx < 1 or new_end_idx > self.audioFragLen: 
                            text = "At that point the window gets out of index."
                            tk.messagebox.showerror(parent=cm, title="Window out of index", message=text) # show error
                            return

                        new_audioFragWind = self.audioFrag[new_ini_idx:new_end_idx]
                        new_audioFragWind2 = new_audioFragWind * window
                        new_stft = np.fft.fft(new_audioFragWind2, nfftUser)
                        new_stft2 = new_stft[range(int(nfftUser/2))]
                        line1.set_ydata(20*np.log10(abs(new_stft2)))

                        # Move the window and rescale 'y' axis
                        if choice == 'STFT':
                            midLine.set_xdata(new_midPoint)
                            axFragSTFT[1].relim()
                            axFragSTFT[1].autoscale_view()
                        elif choice == 'STFT + Spect':
                            midLineWavef.set_xdata(new_midPoint)
                            midLineSpect.set_xdata(new_midPoint)
                            axFragSTFTSpect[1].relim()
                            axFragSTFTSpect[1].autoscale_view()
                        else: # choice == 'Spectral Centroid'
                            midLineWavefSC.set_xdata(new_midPoint)
                            midLineSpectSC.set_xdata(new_midPoint)
                            axFragSC[1].relim()
                            axFragSC[1].autoscale_view()
                        rectangle.set_x(self.audiotimeFrag[new_ini_idx])

                        plt.show() # update the figure
                    
                plt.connect('button_press_event', on_click) # when the mouse button is pressed, call on_click function
                plt.show() # show the figure

            elif choice == 'Spectrogram':
                figFragSpect, axFragSpect = plt.subplots(2, figsize=(12,6))
                plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
                figFragSpect.canvas.manager.set_window_title('Spectrogram') # set title to the figure window

                cursorSpect = MultiCursor(figFragSpect.canvas, (axFragSpect[0], axFragSpect[1]), color='black', lw=1)

                if formants == 1:
                    showFormants() # TO-DO

                axFragSpect[0].plot(self.audiotimeFrag, self.audioFrag)
                axFragSpect[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                axFragSpect[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                axFragSpect[1].specgram(x=self.audioFrag, Fs=self.audiofs, window=window, pad_to=nfftUser, NFFT=windSizeSampInt, mode='magnitude', noverlap=overlapSamp, scale='dB')
                axFragSpect[1].set(xlim=[0, self.audioFragDuration], ylim=[minfreq, maxfreq], xlabel='Time (s)', ylabel='Frequency (Hz)', title='Spectrogram')

                plt.show() # show the figure

            elif choice == 'Short-Time-Energy':
                figFragSTE, axFragSTE = plt.subplots(2, figsize=(12,6))
                plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
                figFragSTE.canvas.manager.set_window_title('Short-Time-Energy') # set title to the figure window

                rms = librosa.feature.rms(y=self.audioFrag, frame_length=windSizeSampInt, hop_length=int(windSizeSamp-overlapSamp), center=True)
                times = librosa.times_like(rms, sr=self.audiofs, hop_length=windSizeSamp-overlapSamp+1, n_fft=None)

                axFragSTE[0].plot(self.audiotimeFrag, self.audioFrag)
                axFragSTE[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                axFragSTE[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                axFragSTE[1].plot(times, 20*np.log10(rms[0]))
                axFragSTE[1].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude (dB)', title='Short Time Energy')

                plt.show() # show the figure

            elif choice == 'Pitch':
                figFragPitch, axFragPitch = plt.subplots(2, figsize=(12,6))
                plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
                figFragPitch.canvas.manager.set_window_title('Pitch') # set title to the figure window

                # Convert the numpy array containing the audio fragment into a wav file
                scaled = np.int16(self.audioFrag/np.max(np.abs(self.audioFrag)) * 32767) 
                write('test.wav', self.audiofs, scaled) # generates the test.wav file in the current folder
                
                # Calculate the pitch of the generated wav file using parselmouth
                snd = parselmouth.Sound('test.wav')
                pitch = snd.to_pitch(pitch_floor=75.0, pitch_ceiling=2500.0)
                print(pitch)
                pitch_values = pitch.selected_array['frequency'] # extract selected pitch contour
                pitch_values[pitch_values==0] = np.nan # replace unvoiced samples by NaN to not plot

                cursorPitch = MultiCursor(figFragPitch.canvas, (axFragPitch[0], axFragPitch[1]), color='black', lw=1)

                axFragPitch[0].plot(self.audiotimeFrag, self.audioFrag)
                axFragPitch[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                axFragPitch[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                axFragPitch[1].plot(pitch.xs(), pitch_values)
                axFragPitch[1].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Frequency (Hz)', title='Pitch measurement overtime')

                plt.show() # show the figure

            else: # choice == 'Filtering'
                figFragFilt, axFragFilt = plt.subplots(2, figsize=(12,6))
                plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
                figFragFilt.canvas.manager.set_window_title('Pitch') # set title to the figure window

                # TO-DO

                axFragFilt[0].plot(self.audiotimeFrag, self.audioFrag)
                axFragFilt[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                axFragFilt[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                axFragFilt[1].specgram(x=self.audioFrag, Fs=self.audiofs, window=window, pad_to=nfftUser, NFFT=windSizeSampInt, mode='magnitude', noverlap=overlapSamp, scale='dB')
                axFragFilt[1].set(xlim=[0, self.audioFragDuration], ylim=[minfreq, maxfreq], xlabel='Time (s)', ylabel='Frequency (Hz)', title='Spectrogram')

                plt.show() # show the figure

        # LABELS
        # Labels of OptionMenus
        lab_opts = tk.Label(cm, text='Choose an option', bd=6, font=('TkDefaultFont', 10, 'bold'))
        lab_wind = tk.Label(cm, text='Window')
        lab_nfft = tk.Label(cm, text='nfft')
        lab_meth = tk.Label(cm, text='Method')

        # Labels of entrys
        lab_size = tk.Label(cm, text='Window length (s)')
        lab_over = tk.Label(cm, text='Overlap (s)')
        lab_minf = tk.Label(cm, text='Min frequency (Hz)')
        lab_maxf = tk.Label(cm, text='Max frequency (Hz)')
        lab_fund = tk.Label(cm, text='Fund. freq. multiplication')
        lab_cent = tk.Label(cm, text='Center frequency')
        lab_cut1 = tk.Label(cm, text='Fcut1')
        lab_cut2 = tk.Label(cm, text='Fcut2')
        lab_fshz = tk.Label(cm, text='Fs: '+str(self.audiofs)+' Hz')

        lab_spec = tk.Label(cm, text='Spectrogram', bd=6, font=('TkDefaultFont', 10))
        lab_ptch = tk.Label(cm, text='Pitch', bd=6, font=('TkDefaultFont', 10))
        lab_filt = tk.Label(cm, text='Filtering', bd=6, font=('TkDefaultFont', 10))
        
        # positioning Labels
        lab_opts.grid(column=0, row=0, sticky=tk.E, columnspan=2)
        lab_wind.grid(column=0, row=1, sticky=tk.E)
        lab_nfft.grid(column=0, row=3, sticky=tk.E)
        lab_meth.grid(column=0, row=10, sticky=tk.E)

        lab_size.grid(column=0, row=2, sticky=tk.E)
        lab_over.grid(column=0, row=4, sticky=tk.E)
        lab_minf.grid(column=0, row=6, sticky=tk.E)
        lab_maxf.grid(column=0, row=7, sticky=tk.E)
        lab_fund.grid(column=2, row=2, sticky=tk.E)
        lab_cent.grid(column=2, row=3, sticky=tk.E)
        lab_cut1.grid(column=2, row=4, sticky=tk.E)
        lab_cut2.grid(column=2, row=5, sticky=tk.E)
        lab_fshz.grid(column=2, row=12, sticky=tk.EW)

        lab_spec.grid(column=1, row=5)
        lab_ptch.grid(column=1, row=9)
        lab_filt.grid(column=3, row=1)

        # ENTRYS
        cm.var_size = tk.DoubleVar(value=0.09)
        cm.var_over = tk.DoubleVar()
        cm.var_minf = tk.IntVar()
        cm.var_maxf = tk.IntVar(value=self.audiofs/2)
        cm.var_fund = tk.IntVar()
        cm.var_cent = tk.IntVar()
        cm.var_cut1 = tk.IntVar()
        cm.var_cut2 = tk.IntVar()

        vcmd = (cm.register(onValidate), '%s', '%S')
        
        ent_size = tk.Entry(cm, textvariable=cm.var_size, state='disabled', validate='key', validatecommand=vcmd)
        ent_over = tk.Entry(cm, textvariable=cm.var_over, state='disabled', validate='key', validatecommand=vcmd)
        ent_minf = tk.Entry(cm, textvariable=cm.var_minf, state='disabled', validate='key', validatecommand=vcmd)
        ent_maxf = tk.Entry(cm, textvariable=cm.var_maxf, state='disabled', validate='key', validatecommand=vcmd)
        ent_fund = tk.Entry(cm, textvariable=cm.var_fund, state='disabled', validate='key', validatecommand=vcmd)
        ent_cent = tk.Entry(cm, textvariable=cm.var_cent, state='disabled', validate='key', validatecommand=vcmd)
        ent_cut1 = tk.Entry(cm, textvariable=cm.var_cut1, state='disabled', validate='key', validatecommand=vcmd)
        ent_cut2 = tk.Entry(cm, textvariable=cm.var_cut2, state='disabled', validate='key', validatecommand=vcmd)

        # calling functions after entering a value and pressing enter
        ent_size.bind('<Return>', windowLengthEntry)
        ent_over.bind('<Return>', overlapEntry)
        ent_minf.bind('<Return>', minfreqEntry)
        ent_maxf.bind('<Return>', maxfreqEntry)

        # positioning Entrys
        ent_size.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_over.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_minf.grid(column=1, row=6, sticky=tk.EW, padx=5, pady=5)
        ent_maxf.grid(column=1, row=7, sticky=tk.EW, padx=5, pady=5)
        ent_fund.grid(column=3, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_cent.grid(column=3, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_cut1.grid(column=3, row=4, sticky=tk.EW, padx=5, pady=5)
        ent_cut2.grid(column=3, row=5, sticky=tk.EW, padx=5, pady=5)

        # CHECKBOX
        cm.var_form = tk.StringVar(value=0)
        chk_form = tk.Checkbutton(cm, text='Formants', command=showFormants, variable=cm.var_form, state='disabled')
        chk_form.grid(column=1, row=8, sticky=tk.W)

        # BUTTONS
        but_adse = tk.Button(cm, text='Advanced settings')
        but_freq = tk.Button(cm, text='Filter Frequency Response')
        but_rese = tk.Button(cm, text='Reset Signal')
        but_fisi = tk.Button(cm, text='Filter Signal')
        but_plot = tk.Button(cm, text='Plot', command=plotFigure, font=('TkDefaultFont', 10, 'bold'))

        but_adse.configure(state='disabled')
        but_freq.configure(state='disabled')
        but_rese.configure(state='disabled')
        but_fisi.configure(state='disabled')

        but_adse.grid(column=1, row=11, sticky=tk.EW, padx=5)
        but_freq.grid(column=3, row=7, sticky=tk.EW, padx=5)
        but_rese.grid(column=3, row=8, sticky=tk.EW, padx=5)
        but_fisi.grid(column=3, row=9, sticky=tk.EW, padx=5)
        but_plot.grid(column=3, row=12, sticky=tk.EW, padx=5)

        # OPTION MENUS
        cm.options = ['FT','STFT', 'Spectrogram','STFT + Spect', 'Short-Time-Energy', 'Pitch', 'Spectral Centroid', 'Filtering']
        cm.opt_wind = ['Bartlett','Blackman', 'Hamming','Hanning', 'Kaiser']
        cm.opt_nfft = [2**11, 2**12, 2**13, 2**14, 2**15, 2**16, 2**17, 2**18, 2**19, 2**20, 2**21, 2**22, 2**23]
        cm.opt_meth = ['Autocorrelation', 'Cross-correlation', 'Subharmonics', 'Spinet']
        cm.opt_filt = ['Butterworth','Elliptic', 'Chebyshev', 'FIR least-squares']

        cm.var_opts = tk.StringVar()
        cm.var_wind = tk.StringVar()
        cm.var_nfft = tk.IntVar()
        cm.var_meth = tk.StringVar()
        cm.var_data = tk.StringVar()
        cm.var_filt = tk.StringVar()

        cm.var_opts.set(cm.options[0])
        cm.var_wind.set(cm.opt_wind[0])
        cm.var_nfft.set(cm.opt_nfft[0])
        cm.var_meth.set(cm.opt_meth[0])
        cm.var_filt.set(cm.opt_filt[0])

        # creating OptionMenus
        dd_opts = tk.OptionMenu(cm, cm.var_opts, *cm.options, command=displayOptions)
        dd_wind = tk.OptionMenu(cm, cm.var_wind, *cm.opt_wind)
        dd_nfft = tk.OptionMenu(cm, cm.var_nfft, *cm.opt_nfft)
        dd_meth = tk.OptionMenu(cm, cm.var_meth, *cm.opt_meth)
        dd_filt = tk.OptionMenu(cm, cm.var_filt, *cm.opt_filt)

        # size of the OptionMenus
        dd_opts.config(width=15)
        dd_wind.config(width=18, state='disabled')
        dd_nfft.config(width=18, state='disabled')
        dd_meth.config(width=18, state='disabled')
        dd_filt.config(width=18, state='disabled')

        # positioning OptionMenus
        dd_opts.grid(column=2, row=0, sticky=tk.W, padx=5, columnspan=2)
        dd_wind.grid(column=1, row=1, sticky=tk.W, padx=5)
        dd_nfft.grid(column=1, row=3, sticky=tk.W, padx=5)
        dd_meth.grid(column=1, row=10, sticky=tk.W, padx=5)
        dd_filt.grid(column=3, row=6, sticky=tk.W, padx=5)

if __name__ == "__main__":
    app = Start()
    app.iconbitmap('images/icon.ico')
    app.mainloop()