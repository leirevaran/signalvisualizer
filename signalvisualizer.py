import tkinter as tk
import tkinter.filedialog
import wave
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Cursor, SpanSelector
from matplotlib import backend_bases

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
        #self.maste.icontbitmap("images/icon.ico")

        #self.createWindowButtons()

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
        
        # Plot the audio file
        self.figWf, self.ax = plt.subplots(figsize=(12,5))
        self.ax.plot(self.audiotime, self.audio)
        self.ax.axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        self.ax.set(xlim=[0, max(self.audiotime)], xlabel='Time (s)', ylabel='Waveform', title='Load an audio file')

        # Add widgets to the figure
        axplay = plt.axes([0.7, 0.01, 0.09, 0.05]) # [x axis, y axis, width, height]
        playButton = Button(axplay, 'Play')
        playButton.on_clicked(self.playSound)
        
        axstop = plt.axes([0.8, 0.01, 0.09, 0.05])
        stopButton = Button(axstop, 'Stop')
        stopButton.on_clicked(self.stopSound)

        # Select a fragment with the cursor
        cursor = Cursor(self.ax, horizOn=False, useblit=True, color='black', linewidth=1)
        span = SpanSelector(self.ax, self.selectFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='red'))
        
        plt.show() # show the figure

    def selectFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.audiotime, (xmin, xmax))
        self.plotFragment(ini, end)
        plt.close(self.figWf) # close the figure of the waveform

    def playSound(self, event):
        sd.play(self.audio, self.audiofs)

    def stopSound(self, event):
        sd.stop()

    def plotFragment(self, ini, end):
        # Variables of the segment of the waveform
        audioFrag = self.audio[ini:end+1]
        audiotimeFrag = np.arange(0, len(audioFrag)/self.audiofs, 1/self.audiofs)

        # Plot the waveform and the spectrum of the audio segment
        figFrag, axFrag = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title

        # Open the control menu frame
        self.createControlMenu()

        # Fast Fourier Transform (FFT) using numpy
        fft = np.fft.fft(audioFrag) /len(audioFrag) # Normalize amplitude
        fft2 = fft[range(int(len(audioFrag)/2))] # Exclude sampling frequency
        tpCount = len(audioFrag)
        values = np.arange(int(tpCount/2))
        timePeriod = tpCount/self.audiofs
        frequencies = values/timePeriod

        axFrag[0].plot(audiotimeFrag, audioFrag)
        axFrag[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        axFrag[0].set(xlim=[0, max(audiotimeFrag)], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
        axFrag[1].plot(frequencies, 20*np.log10(abs(fft2)))
        axFrag[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum of the Fourier Transform')


        # Short Time Fourier Transform (STFT) using numpy
        # tw = 0.09
        # # mirar donde tiene el usuario el cursor y crear un audioFrag mas pequeño para el analisis de la longitud de la ventana (tw)
        # n = tw * self.audiofs
        # print('n:')
        # print(n)
        # window = np.hamming(int(n))
        # print('longitud de audioFrag:')
        # print(len(audioFrag))
        # audioFragW = audioFrag * window
        # nfft = 2048

        # if nfft > n:
        #     stft = np.fft.fft(audioFragW, nfft)

        # values = np.arange(int(nfft/2))
        # timePeriod = n/self.audiofs
        # frequencies = values * self.audiofs / nfft

        # axFrag[0].plot(audiotimeFrag, audioFrag)
        # axFrag[0].axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        # axFrag[0].set(xlim=[0, max(audiotimeFrag)], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')
        # axFrag[1].plot(frequencies, 20*np.log10(abs(stft)))
        # axFrag[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Spectrum of the Short Time Fourier Transform')
        
        
        # connect figFrag with w1Button in signalVisualizer

        plt.show() # show the figure

    def createControlMenu(self):
        controlmenu = tk.Toplevel()
        controlmenu.geometry('710x420')
        controlmenu.title('Control menu')

        # LABELS
        # Labels of OptionMenus
        lab_opts = tk.Label(controlmenu, text='Choose an option', bd=6, font=('TkDefaultFont', 10, 'bold'))
        lab_wind = tk.Label(controlmenu, text='Window')
        lab_nfft = tk.Label(controlmenu, text='nfft')
        lab_meth = tk.Label(controlmenu, text='Method')
        lab_data = tk.Label(controlmenu, text='Data operations')

        # Labels of entrys
        lab_size = tk.Label(controlmenu, text='Window length (s)')
        lab_over = tk.Label(controlmenu, text='Overlap (s)')
        lab_fund = tk.Label(controlmenu, text='Fund. freq. multiplication')
        lab_cent = tk.Label(controlmenu, text='Center frequency')
        lab_cut1 = tk.Label(controlmenu, text='Fcut1')
        lab_cut2 = tk.Label(controlmenu, text='Fcut2')
        lab_fshz = tk.Label(controlmenu, text='fs (Hz)')

        lab_ptch = tk.Label(controlmenu, text='Pitch', bd=6, font=('TkDefaultFont', 10))
        lab_filt = tk.Label(controlmenu, text='Filtering', bd=6, font=('TkDefaultFont', 10))
        
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
        controlmenu.var_size = tk.StringVar(value='0.09')
        controlmenu.var_over = tk.StringVar(value='0')
        controlmenu.var_fund = tk.StringVar()
        controlmenu.lab_cent = tk.StringVar()
        controlmenu.lab_cut1 = tk.StringVar()
        controlmenu.lab_cut2 = tk.StringVar()

        ent_size = tk.Entry(controlmenu, textvariable=controlmenu.var_size, state='disabled')
        ent_over = tk.Entry(controlmenu, textvariable=controlmenu.var_over, state='disabled')
        ent_fund = tk.Entry(controlmenu, textvariable=controlmenu.var_fund, state='disabled')
        ent_cent = tk.Entry(controlmenu, textvariable=controlmenu.lab_cent, state='disabled')
        ent_cut1 = tk.Entry(controlmenu, textvariable=controlmenu.lab_cut1, state='disabled')
        ent_cut2 = tk.Entry(controlmenu, textvariable=controlmenu.lab_cut2, state='disabled')

        # positioning Entrys
        ent_size.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_over.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_fund.grid(column=3, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_cent.grid(column=3, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_cut1.grid(column=3, row=4, sticky=tk.EW, padx=5, pady=5)
        ent_cut2.grid(column=3, row=5, sticky=tk.EW, padx=5, pady=5)

        # CHECKBOX
        controlmenu.var_form = tk.StringVar(value=0)
        chk_form = tk.Checkbutton(controlmenu, text='Formants', command=self.showFormants, variable=controlmenu.var_form, state='disabled')
        chk_form.grid(column=1, row=5, sticky=tk.W)

        # TEXT
        txt_fs = tk.Text(controlmenu, height=1, width=10)
        fs = self.audiofs
        txt_fs.insert('0.0', fs)
        txt_fs.config(state='disabled')
        txt_fs.grid(column=1, row=10, sticky=tk.W)

        # BUTTONS
        but_freq = tk.Button(controlmenu, text='Filter Frequency Response')
        but_rese = tk.Button(controlmenu, text='Reset Signal')
        but_fisi = tk.Button(controlmenu, text='Filter Signal')
        but_plot = tk.Button(controlmenu, text='Plot', command=self.plotFigure, font=('TkDefaultFont', 10, 'bold'))

        but_freq.configure(state='disabled')
        but_rese.configure(state='disabled')
        but_fisi.configure(state='disabled')

        but_freq.grid(column=3, row=7, sticky=tk.EW, padx=5)
        but_rese.grid(column=3, row=8, sticky=tk.EW, padx=5)
        but_fisi.grid(column=3, row=9, sticky=tk.EW, padx=5)
        but_plot.grid(column=2, row=10, padx=5, pady=5, ipadx=10)

        # OPTION MENUS
        options = ['FT','STFT', 'Spectrogram','STFT + Spect', 'Short-Time-Energy', 'Pitch', 'Spectral Centroid', 'Filtering']
        opt_wind = ['Rectangular','Hanning', 'Hamming','Gaussian', 'Triangular', 'Chebyshev', 'Taylor', 'Bartlett', 'Kaiser']
        opt_nfft = ['2048','4096', '8192','16384', '32768', '65536', '131072', '262144', '524288', '1048576', '2097152', '4194304', '8388608']
        opt_meth = ['Cepstrum','Autocorrelation']
        opt_data = ['None','Median Filtering', 'Low Energy Suppresion']
        opt_filt = ['Butterworth','Elliptic', 'Chebyshev', 'FIR least-squares']

        controlmenu.var_opts = tk.StringVar()
        controlmenu.var_wind = tk.StringVar()
        controlmenu.var_nfft = tk.StringVar()
        controlmenu.var_meth = tk.StringVar()
        controlmenu.var_data = tk.StringVar()
        controlmenu.var_filt = tk.StringVar()

        controlmenu.var_opts.set(options[0])
        controlmenu.var_wind.set(opt_wind[0])
        controlmenu.var_nfft.set(opt_nfft[0])
        controlmenu.var_meth.set(opt_meth[0])
        controlmenu.var_data.set(opt_data[0])
        controlmenu.var_filt.set(opt_filt[0])

        def display_opts(choice):
            choice = controlmenu.var_opts.get()
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

        # creating OptionMenus
        dd_opts = tk.OptionMenu(controlmenu, controlmenu.var_opts, *options, command=display_opts)
        dd_wind = tk.OptionMenu(controlmenu, controlmenu.var_wind, *opt_wind)
        dd_nfft = tk.OptionMenu(controlmenu, controlmenu.var_nfft, *opt_nfft)
        dd_meth = tk.OptionMenu(controlmenu, controlmenu.var_meth, *opt_meth)
        dd_data = tk.OptionMenu(controlmenu, controlmenu.var_data, *opt_data)
        dd_filt = tk.OptionMenu(controlmenu, controlmenu.var_filt, *opt_filt)

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

    def showFormants(self):
        pass

    def plotFigure(self):
        pass
        #fig, self.ax = plt.subplots(figsize=(12,5))
        #self.ax.plot(self.audiotime, self.audio)
    

if __name__ == "__main__":
    app = Start()
    app.mainloop()