import tkinter as tk
import tkinter.filedialog
import wave
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib import backend_bases
from matplotlib.widgets import Button, Cursor, SpanSelector
from matplotlib.backend_bases import MouseButton

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Start(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
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
        self.audiotime = np.arange(0, len(self.audio)/self.audiofs, 1/self.audiofs) # Time axe

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

        # Add widgets to the figure
        axplay = plt.axes([0.7, 0.01, 0.09, 0.05]) # [x axis, y axis, width, height]
        playButton = Button(axplay, 'Play')
        playButton.on_clicked(self.playSound)
        
        axstop = plt.axes([0.8, 0.01, 0.09, 0.05])
        stopButton = Button(axstop, 'Stop')
        stopButton.on_clicked(self.stopSound)

        # Select a fragment with the cursor
        cursor = Cursor(self.axFile, horizOn=False, useblit=True, color='black', linewidth=1)
        span = SpanSelector(self.axFile, self.selectFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='red'))
        
        plt.show() # show the figure

    def selectFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.audiotime, (xmin, xmax))
        self.plotFragment(ini, end)
        plt.close(self.figFile) # close the figure of the waveform

    def playSound(self, event):
        sd.play(self.audio, self.audiofs)

    def stopSound(self, event):
        sd.stop()

    def plotFragment(self, ini, end):
        # Variables of the segment of the waveform
        self.audioFrag = self.audio[ini:end+1]
        self.audiotimeFrag = np.arange(0, len(self.audioFrag)/self.audiofs, 1/self.audiofs)
        self.audioFragDuration = max(self.audiotimeFrag)
        self.audioFragLen = len(self.audioFrag)

        self.createControlMenu() # Open the control menu window
        self.plotFft() # Plot the Fast Fourier Transform (FFT) of the fragment

    # Plots the Fast Fourier Transform (FFT) of the fragment in the 'ax' axis
    def plotFft(self):
        # Plot the waveform and the spectrum of the audio segment
        self.figFragFft, self.axFragFft = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        self.figFragFft.canvas.manager.set_window_title('FT')

        fft = np.fft.fft(self.audioFrag) / self.audioFragLen # Normalize amplitude
        fft2 = fft[range(int(self.audioFragLen/2))] # Exclude sampling frequency
        values = np.arange(int(self.audioFragLen/2))
        frequencies = values / (self.audioFragLen/self.audiofs) # values / time period

        self.axFragFft[0].plot(self.audiotimeFrag, self.audioFrag)
        self.axFragFft[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        self.axFragFft[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
        self.axFragFft[1].plot(frequencies, 20*np.log10(abs(fft2)))
        self.axFragFft[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum of the Fourier Transform')

        # TO-DO: connect figFrag with w1Button in signalVisualizer

        self.figFragFft.show() # show the figure

    def createControlMenu(self):
        cm = tk.Toplevel()
        cm.geometry('720x420')
        cm.resizable(False, False)
        cm.title('Control menu')
        cm.iconbitmap('images/icon.ico')

        # METHODS
        # Called when changing the main option (FT, STFT, etc.)
        def displayOpts(choice):
            choice = cm.var_opts.get()
            if choice == 'FT':
                ent_size.config(state='disabled')
                ent_over.config(state='disabled')
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_wind.config(state='disabled')
                dd_nfft.config(state='disabled')
                dd_meth.config(state='disabled')
                dd_data.config(state='disabled')
                dd_filt.config(state='disabled')
                chk_form.config(state='disabled')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                but_fisi.configure(state='disabled')
            elif choice == 'STFT':
                ent_size.config(state='normal')
                ent_over.config(state='disabled')
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_wind.config(state='active')
                dd_nfft.config(state='active')
                dd_meth.config(state='disabled')
                dd_data.config(state='disabled')
                dd_filt.config(state='disabled')
                chk_form.config(state='disabled')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                but_fisi.configure(state='disabled')
            elif choice == 'Spectrogram':
                ent_size.config(state='normal')
                ent_over.config(state='normal')
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_wind.config(state='active')
                dd_nfft.config(state='active')
                dd_meth.config(state='disabled')
                dd_data.config(state='disabled')
                dd_filt.config(state='disabled')
                chk_form.config(state='active')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                but_fisi.configure(state='disabled')
            elif choice == 'STFT + Spect':
                ent_size.config(state='normal')
                ent_over.config(state='normal')
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_wind.config(state='active')
                dd_nfft.config(state='active')
                dd_meth.config(state='disabled')
                dd_data.config(state='disabled')
                dd_filt.config(state='disabled')
                chk_form.config(state='disabled')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                but_fisi.configure(state='disabled')
            elif choice == 'Short-Time-Energy' or choice == 'Spectral Centroid':
                ent_size.config(state='normal')
                ent_over.config(state='normal')
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_wind.config(state='active')
                dd_nfft.config(state='disabled')
                dd_meth.config(state='disabled')
                dd_data.config(state='disabled')
                dd_filt.config(state='disabled')
                chk_form.config(state='disabled')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                but_fisi.configure(state='disabled')
            elif choice == 'Pitch':
                ent_size.config(state='normal')
                ent_over.config(state='normal')
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_wind.config(state='disabled')
                dd_nfft.config(state='disabled')
                dd_meth.config(state='active')
                dd_data.config(state='active')
                dd_filt.config(state='disabled')
                chk_form.config(state='disabled')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                but_fisi.configure(state='disabled')
            elif choice == 'Filtering':
                ent_size.config(state='disabled')
                ent_over.config(state='disabled')
                ent_fund.config(state='normal')
                ent_cent.config(state='normal')
                ent_cut1.config(state='normal')
                ent_cut2.config(state='normal')
                dd_wind.config(state='disabled')
                dd_nfft.config(state='disabled')
                dd_meth.config(state='disabled')
                dd_data.config(state='disabled')
                dd_filt.config(state='active')
                chk_form.config(state='disabled')
                but_freq.configure(state='active')
                but_rese.configure(state='active')
                but_fisi.configure(state='active')

        # Called when inserting a value in the entry of the window size and pressing enter
        def windSizeFunction(wind_size):
            # Show an error and stop if the window size is greater than the duration of the signal
            wind_size = float(ent_size.get())
            if wind_size > self.audioFragDuration:
                text = "The chosen value for the window size can't be greater than the duration of the signal (" + str(self.audioFragDuration) + "s)."
                tk.messagebox.showerror(title="Window size too long", message=text) # show error

            # Change the values of nfft to be always greater than the window size
            wind_size_sample = wind_size * self.audiofs # window size in samples
            nfft = cm.var_nfft.get()
            if int(wind_size_sample) > nfft:
                for i in range(len(opt_nfft)):
                    if int(wind_size_sample) < opt_nfft[i]:
                        cm.var_nfft.set(opt_nfft[i])
                        break
                    else:
                        dd_nfft['menu'].delete(0) # delete that opt_nfft[i] option
        
        # Called when clicking the 'Formants' checkbox
        def showFormants():
            pass

        # Called when pressing the 'Plot' button
        def plotFigure():
            choice = cm.var_opts.get()
            
            # if choice == 'FT': # Fast Fourier Transform (FFT) using numpy
            #     if plt.fignum_exists(self.figFragFft.number): #TO-DO: si esta minimizada no funciona!!!
            #         self.figFragFft.show() # the figure showing the FFt already exists: show it
            #     else:
            #         self.plotFft() # the figure showing the FFt doesn't exist: create it again

            if choice == 'FT':
                if plt.fignum_exists(self.figFragFft.number):
                    plt.close(self.figFragFft.number) # close the figure of the FT
                self.plotFft() # create the figure of the FT (again)

            elif choice == 'STFT': # Short Time Fourier Transform (STFT) using numpy
                figFragStft, axFragStft = plt.subplots(2, figsize=(12,6))
                plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
                figFragStft.canvas.manager.set_window_title('STFT') # set title to the figure window

                # Values given by the user
                nfft = cm.var_nfft.get()
                wind_type = cm.var_wind.get()
                wind_size = float(ent_size.get()) # window size in seconds
                wind_size_sample = wind_size * self.audiofs # window size in samples
                wind_size_sample_int = int(wind_size_sample)

                # Apply the window type to the window
                if wind_type == 'Bartlett':
                    window = np.bartlett(wind_size_sample_int)
                elif wind_type == 'Blackman':
                    window = np.blackman(wind_size_sample_int)
                elif wind_type == 'Hamming':
                    window = np.hamming(wind_size_sample_int)
                elif wind_type == 'Hanning':
                    window = np.hanning(wind_size_sample_int)
                elif wind_type == 'Kaiser':
                    window = np.kaiser(wind_size_sample_int) # TO-DO: np.kaiser(wind_size_sample_int, float:shape parameter for window)

                def on_click(event):
                    if event.button is MouseButton.LEFT:
                        x, y = event.x, event.y
                        if event.inaxes == axFragStft[0]:
                            plt.axvline(x, ymin=1, ymax=1, color='red')
                            print('data coords %f %f' % (event.xdata, event.ydata))
                
                # TO-DO: mirar donde esta el cursor y crear un audioFrag mas pequeño para el analisis de la longitud de la ventana (wind_size)
                cursor = Cursor(axFragStft[0], horizOn=False, useblit=True, color='black', linewidth=1)
                # binding_id = plt.connect('motion_notify_event', on_click)
                plt.connect('button_press_event', on_click)
                
                # TO-DO: cursor en la mitad por defecto
                middleFrag = int(self.audioFragLen/2)

                ini = middleFrag - int(wind_size_sample/2)
                end = middleFrag + int(wind_size_sample/2)
                if ini < 1:
                    ini = 0
                if end > self.audioFragLen:
                    end = self.audioFragLen-1

                audioFragWind = self.audioFrag[ini:end] # si queremos incluir el punto 'end'-> [ini:end+1]
                # TO-DO: pintar el segmento de audioFragWind en gris
                audioFragWind2 = audioFragWind * window
                stft = np.fft.fft(audioFragWind2, nfft)

                values = np.arange(nfft) # np.arange(int(nfft/2))
                frequencies = values * self.audiofs / nfft

                axFragStft[0].plot(self.audiotimeFrag, self.audioFrag)
                axFragStft[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
                axFragStft[0].set(xlim=[0, self.audioFragDuration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
                axFragStft[1].plot(frequencies, 20*np.log10(abs(stft)))
                axFragStft[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum of the Short Time Fourier Transform')

                plt.show() # show the figure

            elif choice == 'Spectrogram':
                figFragSpect, axFragSpect = plt.subplots(2, figsize=(12,6))
                plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
                figFragSpect.canvas.manager.set_window_title('STFT') # set title to the figure window

                # Values given by the user
                nfft = cm.var_nfft.get()
                wind_type = cm.var_wind.get()
                wind_size = float(ent_size.get()) # window size in seconds
                wind_size_sample = wind_size * self.audiofs # window size in samples
                wind_size_sample_int = int(wind_size_sample)
                overlap = int(ent_over.get()) # int or float?
                formants = cm.var_form.get() # returns 1 if activated, 0 if not

                # Apply the window type to the window
                if wind_type == 'Bartlett':
                    window = np.bartlett(wind_size_sample_int)
                elif wind_type == 'Blackman':
                    window = np.blackman(wind_size_sample_int)
                elif wind_type == 'Hamming':
                    window = np.hamming(wind_size_sample_int)
                elif wind_type == 'Hanning':
                    window = np.hanning(wind_size_sample_int)
                elif wind_type == 'Kaiser':
                    window = np.kaiser(wind_size_sample_int) # TO-DO: np.kaiser(wind_size_sample_int, float:shape parameter for window)

        # LABELS
        # Labels of OptionMenus
        lab_opts = tk.Label(cm, text='Choose an option', bd=6, font=('TkDefaultFont', 10, 'bold'))
        lab_wind = tk.Label(cm, text='Window')
        lab_nfft = tk.Label(cm, text='nfft')
        lab_meth = tk.Label(cm, text='Method')
        lab_data = tk.Label(cm, text='Data operations')

        # Labels of entrys
        lab_size = tk.Label(cm, text='Window length (s)')
        lab_over = tk.Label(cm, text='Overlap (s)')
        lab_fund = tk.Label(cm, text='Fund. freq. multiplication')
        lab_cent = tk.Label(cm, text='Center frequency')
        lab_cut1 = tk.Label(cm, text='Fcut1')
        lab_cut2 = tk.Label(cm, text='Fcut2')
        lab_fshz = tk.Label(cm, text='fs (Hz)')

        lab_ptch = tk.Label(cm, text='Pitch', bd=6, font=('TkDefaultFont', 10))
        lab_filt = tk.Label(cm, text='Filtering', bd=6, font=('TkDefaultFont', 10))
        
        # positioning Labels
        lab_opts.grid(column=0, row=0, sticky=tk.E, columnspan=2)
        lab_wind.grid(column=0, row=1, sticky=tk.E)
        lab_nfft.grid(column=0, row=3, sticky=tk.E)
        lab_meth.grid(column=0, row=7, sticky=tk.E)
        lab_data.grid(column=0, row=8, sticky=tk.E)

        lab_size.grid(column=0, row=2, sticky=tk.E)
        lab_over.grid(column=0, row=4, sticky=tk.E)
        lab_fund.grid(column=2, row=2, sticky=tk.E)
        lab_cent.grid(column=2, row=3, sticky=tk.E)
        lab_cut1.grid(column=2, row=4, sticky=tk.E)
        lab_cut2.grid(column=2, row=5, sticky=tk.E)
        lab_fshz.grid(column=0, row=10, sticky=tk.E)

        lab_ptch.grid(column=1, row=6)
        lab_filt.grid(column=3, row=1)

        # ENTRYS
        cm.var_size = tk.DoubleVar(value=0.09)
        cm.var_over = tk.IntVar(value=0)
        cm.var_fund = tk.IntVar()
        cm.lab_cent = tk.IntVar()
        cm.lab_cut1 = tk.IntVar()
        cm.lab_cut2 = tk.IntVar()

        ent_size = tk.Entry(cm, textvariable=cm.var_size, state='disabled')
        ent_over = tk.Entry(cm, textvariable=cm.var_over, state='disabled')
        ent_fund = tk.Entry(cm, textvariable=cm.var_fund, state='disabled')
        ent_cent = tk.Entry(cm, textvariable=cm.lab_cent, state='disabled')
        ent_cut1 = tk.Entry(cm, textvariable=cm.lab_cut1, state='disabled')
        ent_cut2 = tk.Entry(cm, textvariable=cm.lab_cut2, state='disabled')

        # calling functions after entering a value and pressing enter
        ent_size.bind('<Return>', windSizeFunction)

        # positioning Entrys
        ent_size.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_over.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_fund.grid(column=3, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_cent.grid(column=3, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_cut1.grid(column=3, row=4, sticky=tk.EW, padx=5, pady=5)
        ent_cut2.grid(column=3, row=5, sticky=tk.EW, padx=5, pady=5)

        # CHECKBOX
        cm.var_form = tk.StringVar(value=0)
        chk_form = tk.Checkbutton(cm, text='Formants', command=showFormants, variable=cm.var_form, state='disabled')
        chk_form.grid(column=1, row=5, sticky=tk.W)

        # TEXT
        txt_fs = tk.Text(cm, height=1, width=10)
        txt_fs.insert('0.0', self.audiofs)
        txt_fs.config(state='disabled')
        txt_fs.grid(column=1, row=10, sticky=tk.W)

        # BUTTONS
        but_freq = tk.Button(cm, text='Filter Frequency Response')
        but_rese = tk.Button(cm, text='Reset Signal')
        but_fisi = tk.Button(cm, text='Filter Signal')
        but_plot = tk.Button(cm, text='Plot', command=plotFigure, font=('TkDefaultFont', 10, 'bold'))

        but_freq.configure(state='disabled')
        but_rese.configure(state='disabled')
        but_fisi.configure(state='disabled')

        but_freq.grid(column=3, row=7, sticky=tk.EW, padx=5)
        but_rese.grid(column=3, row=8, sticky=tk.EW, padx=5)
        but_fisi.grid(column=3, row=9, sticky=tk.EW, padx=5)
        but_plot.grid(column=2, row=10, padx=5, pady=5, ipadx=10)

        # OPTION MENUS
        options = ['FT','STFT', 'Spectrogram','STFT + Spect', 'Short-Time-Energy', 'Pitch', 'Spectral Centroid', 'Filtering']
        opt_wind = ['Bartlett','Blackman', 'Hamming','Hanning', 'Kaiser']
        opt_nfft = [2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608]
        opt_meth = ['Cepstrum','Autocorrelation']
        opt_data = ['None','Median Filtering', 'Low Energy Suppresion']
        opt_filt = ['Butterworth','Elliptic', 'Chebyshev', 'FIR least-squares']

        cm.var_opts = tk.StringVar()
        cm.var_wind = tk.StringVar()
        cm.var_nfft = tk.IntVar()
        cm.var_meth = tk.StringVar()
        cm.var_data = tk.StringVar()
        cm.var_filt = tk.StringVar()

        cm.var_opts.set(options[0])
        cm.var_wind.set(opt_wind[0])
        cm.var_nfft.set(opt_nfft[0])
        cm.var_meth.set(opt_meth[0])
        cm.var_data.set(opt_data[0])
        cm.var_filt.set(opt_filt[0])

        # creating OptionMenus
        dd_opts = tk.OptionMenu(cm, cm.var_opts, *options, command=displayOpts)
        dd_wind = tk.OptionMenu(cm, cm.var_wind, *opt_wind)
        dd_nfft = tk.OptionMenu(cm, cm.var_nfft, *opt_nfft)
        dd_meth = tk.OptionMenu(cm, cm.var_meth, *opt_meth)
        dd_data = tk.OptionMenu(cm, cm.var_data, *opt_data)
        dd_filt = tk.OptionMenu(cm, cm.var_filt, *opt_filt)

        # size of the OptionMenus
        dd_opts.config(width=15)
        dd_wind.config(width=18, state='disabled')
        dd_nfft.config(width=18, state='disabled')
        dd_meth.config(width=18, state='disabled')
        dd_data.config(width=18, state='disabled')
        dd_filt.config(width=18, state='disabled')

        # positioning OptionMenus
        dd_opts.grid(column=2, row=0, sticky=tk.W, padx=5, columnspan=2)
        dd_wind.grid(column=1, row=1, sticky=tk.W, padx=5)
        dd_nfft.grid(column=1, row=3, sticky=tk.W, padx=5)
        dd_meth.grid(column=1, row=7, sticky=tk.W, padx=5)
        dd_data.grid(column=1, row=8, sticky=tk.W, padx=5)
        dd_filt.grid(column=3, row=6, sticky=tk.W, padx=5)

if __name__ == "__main__":
    app = Start()
    app.iconbitmap('images/icon.ico')
    app.mainloop()