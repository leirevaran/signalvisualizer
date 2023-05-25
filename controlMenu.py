import tkinter as tk
import math
import librosa, librosa.display 
import parselmouth
import numpy as np
import sounddevice as sd
import matplotlib as mpl
import matplotlib.pyplot as plt
from tkinter import ttk
from scipy import signal
from matplotlib.widgets import Cursor, SpanSelector, MultiCursor
from matplotlib.backend_bases import MouseButton, MouseEvent
from matplotlib.patches import Rectangle
from scipy.io.wavfile import write

from auxiliar import Auxiliar
from pitchAdvancedSettings import AdvancedSettings

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class ControlMenu():

    def createControlMenu(self, root, fileName, fs, audioFrag):
        self.fileName = fileName
        self.audio = audioFrag # audio array of the fragment
        self.fs = fs # sample frequency of the audio (Hz)
        self.time = np.arange(0, len(self.audio)/self.fs, 1/self.fs) # time array of the audio
        self.duration = max(self.time) # duration of the audio (s)
        self.lenAudio = len(self.audio) # length of the audio array

        self.aux = Auxiliar()
        self.adse = AdvancedSettings()

        cm = tk.Toplevel()
        self.plotFT(cm) # show the figure of the FT
        cm.resizable(True, True)
        cm.title(self.fileName)
        cm.iconbitmap('icons/icon.ico')
        cm.wm_transient(root) # Place the toplevel window at the top
        # self.aux.windowGeometry(cm, 750, 575)

        # Adapt the window to different sizes
        for i in range(3):
            cm.columnconfigure(i, weight=1)

        for i in range(14):
            cm.rowconfigure(i, weight=1)

        # If the 'Control menu' window is closed, close also all the generated figures
        def on_closing():
            cm.destroy()
            plt.close('all') # closes all matplotlib figures
        cm.protocol("WM_DELETE_WINDOW", on_closing)

        # LABELS
        # Labels of OptionMenus
        lab_opts = tk.Label(cm, text='Choose an option', bd=6, font=('TkDefaultFont', 10, 'bold'))
        lab_wind = tk.Label(cm, text='Window')
        lab_nfft = tk.Label(cm, text='nfft')
        lab_meth = tk.Label(cm, text='Method')
        lab_type = tk.Label(cm, text='Filter type')

        # Labels of Entrys
        lab_size = tk.Label(cm, text='Window length (s)')
        lab_over = tk.Label(cm, text='Overlap (s)')
        lab_minf = tk.Label(cm, text='Min frequency (Hz)')
        lab_maxf = tk.Label(cm, text='Max frequency (Hz)')
        lab_minp = tk.Label(cm, text='Pitch floor (Hz)')
        lab_maxp = tk.Label(cm, text='Pitch ceiling (Hz)')
        lab_fund = tk.Label(cm, text='Fund. freq. multiplication')
        lab_cent = tk.Label(cm, text='Center frequency')
        lab_cut1 = tk.Label(cm, text='Fcut1')
        lab_cut2 = tk.Label(cm, text='Fcut2')
        lab_beta = tk.Label(cm, text='Beta')
        lab_fshz = tk.Label(cm, text='Fs: '+str(self.fs)+' Hz')

        lab_spec = tk.Label(cm, text='Spectrogram', bd=6, font=('TkDefaultFont', 10))
        lab_ptch = tk.Label(cm, text='Pitch', bd=6, font=('TkDefaultFont', 10))
        lab_filt = tk.Label(cm, text='Filtering', bd=6, font=('TkDefaultFont', 10))
        lab_sten = tk.Label(cm, text='Short-Time-Energy', bd=6, font=('TkDefaultFont', 10))

        # Labels of Radiobuttons
        lab_draw = tk.Label(cm, text='Drawing style')
        
        # positioning Labels
        lab_opts.grid(column=0, row=0, sticky=tk.E, columnspan=2)
        lab_wind.grid(column=0, row=1, sticky=tk.E)
        lab_nfft.grid(column=0, row=3, sticky=tk.E)
        lab_meth.grid(column=0, row=10, sticky=tk.E)
        lab_type.grid(column=2, row=2, sticky=tk.E)

        lab_size.grid(column=0, row=2, sticky=tk.E)
        lab_over.grid(column=0, row=4, sticky=tk.E)
        lab_minf.grid(column=0, row=6, sticky=tk.E)
        lab_maxf.grid(column=0, row=7, sticky=tk.E)
        lab_draw.grid(column=0, row=8, sticky=tk.E)
        lab_minp.grid(column=0, row=11, sticky=tk.E)
        lab_maxp.grid(column=0, row=12, sticky=tk.E)
        lab_fund.grid(column=2, row=3, sticky=tk.E)
        lab_cent.grid(column=2, row=4, sticky=tk.E)
        lab_cut1.grid(column=2, row=5, sticky=tk.E)
        lab_cut2.grid(column=2, row=6, sticky=tk.E)
        lab_beta.grid(column=2, row=11, sticky=tk.E)
        lab_fshz.grid(column=3, row=13, sticky=tk.EW)

        lab_spec.grid(column=1, row=5)
        lab_ptch.grid(column=1, row=9)
        lab_filt.grid(column=3, row=1)
        lab_sten.grid(column=3, row=10)

        # ENTRYS
        cm.var_size = tk.DoubleVar(value=0.03)
        cm.var_over = tk.DoubleVar(value=0.01)
        cm.var_minf = tk.IntVar()
        cm.var_maxf = tk.IntVar(value=self.fs/2)
        cm.var_minp = tk.DoubleVar(value=75.0)
        cm.var_maxp = tk.DoubleVar(value=600.0)
        cm.var_fund = tk.IntVar(value=1)
        cm.var_cent = tk.IntVar(value=400)
        cm.var_cut1 = tk.IntVar(value=200)
        cm.var_cut2 = tk.IntVar(value=600)
        cm.var_beta = tk.IntVar()

        vcmd = (cm.register(self.aux.onValidate), '%S', '%s', '%d')
        
        ent_size = ttk.Entry(cm, textvariable=cm.var_size, state='disabled', validate='key', validatecommand=vcmd)
        ent_over = ttk.Entry(cm, textvariable=cm.var_over, state='disabled', validate='key', validatecommand=vcmd)
        ent_minf = ttk.Entry(cm, textvariable=cm.var_minf, state='disabled', validate='key', validatecommand=vcmd)
        ent_maxf = ttk.Entry(cm, textvariable=cm.var_maxf, state='disabled', validate='key', validatecommand=vcmd)
        ent_minp = ttk.Entry(cm, textvariable=cm.var_minp, state='disabled', validate='key', validatecommand=vcmd)
        ent_maxp = ttk.Entry(cm, textvariable=cm.var_maxp, state='disabled', validate='key', validatecommand=vcmd)
        ent_fund = ttk.Entry(cm, textvariable=cm.var_fund, state='disabled', validate='key', validatecommand=vcmd)
        ent_cent = ttk.Entry(cm, textvariable=cm.var_cent, state='disabled', validate='key', validatecommand=vcmd)
        ent_cut1 = ttk.Entry(cm, textvariable=cm.var_cut1, state='disabled', validate='key', validatecommand=vcmd)
        ent_cut2 = ttk.Entry(cm, textvariable=cm.var_cut2, state='disabled', validate='key', validatecommand=vcmd)
        ent_beta = ttk.Entry(cm, textvariable=cm.var_beta, state='disabled', validate='key', validatecommand=vcmd)

        # Called when inserting a value in the entry of the window length and pressing enter
        def windowLengthEntry(event):
            # Show an error and stop if the inserted window size is incorrect
            windSize = cm.var_size.get()
            overlap = cm.var_over.get()
            if windSize > self.duration or windSize == 0:
                # Reset widgets
                cm.var_size.set(0.03)
                cm.opt_nfft = [2**9, 2**10, 2**11, 2**12, 2**13, 2**14, 2**15, 2**16, 2**17, 2**18, 2**19]
                self.updateOptionMenu(cm, dd_nfft)
                if windSize > self.duration: # The window size can't be greater than the duration of the signal
                    text = "The window size can't be greater than the duration of the signal (" + str(round(self.duration, 2)) + "s)."
                    tk.messagebox.showerror(parent=cm, title="Window size too long", message=text) # show error
                elif windSize == 0: # The window size must be a positive number
                    tk.messagebox.showerror(parent=cm, title="Wrong window size value", message="The chosen value for the window size must be a positive number.") # show error
            elif windSize < overlap: # The window size must always be greater than the overlap
                cm.var_size.set(overlap+0.01)
                text2 = "The window size must always be greater than the overlap (" + str(overlap) + "s)."
                tk.messagebox.showerror(parent=cm, title="Wrong overlap value", message=text2) # show error
            # Change the values of nfft to be always greater than the window size
            else: 
                windSizeSamp = windSize * self.fs # window size in samples
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
                    self.updateOptionMenu(cm, dd_nfft)
                else: # Adds smaller values to the nfft list if possible
                    first = int(math.log2(nfft)) - 1
                    while 2**first > windSizeSamp:
                        for a in range(len(cm.opt_nfft)-1, 0, -1):
                            cm.opt_nfft[a] = cm.opt_nfft[a-1]
                        cm.opt_nfft[0] = 2**first
                        self.updateOptionMenu(cm, dd_nfft)
                        first -= 1
                return True
            
        def overlapEntry(event):
            # Show an error and stop if the inserted overlap is incorrect
            overlap = cm.var_over.get()
            windSize = cm.var_size.get()
            if overlap > self.duration or overlap >= windSize:
                cm.var_over.set('0.01') # Reset widget
                if overlap > self.duration: # The overlap can't be greater than the duration of the signal
                    text = "The overlap can't be greater than the duration of the signal (" + str(round(self.duration, 2)) + "s)."
                    tk.messagebox.showerror(parent=cm, title="Overlap too long", message=text) # show error
                elif overlap >= windSize: # The overlap must always be smaller than the window size
                    text2 = "The overlap must always be smaller than the window size (" + str(windSize) + "s)."
                    tk.messagebox.showerror(parent=cm, title="Wrong overlap value", message=text2) # show error
            else: return True

        def minfreqEntry(event):
            # The minimum frequency must be >= 0 and smaller than the maximum frequency
            minfreq = cm.var_minf.get()
            maxfreq = cm.var_maxf.get()
            if minfreq >= maxfreq:
                cm.var_minf.set('0') # Reset widget
                text = "The minimum frequency must be smaller than the maximum frequency (" + str(maxfreq) + "Hz)."
                tk.messagebox.showerror(parent=cm, title="Minimum frequency too big", message=text) # show error
            else: return True

        def maxfreqEntry(event):
            # The maximum frequency must be <= self.fs/2 and greater than the minimum frequency
            minfreq = cm.var_minf.get()
            maxfreq = cm.var_maxf.get()
            if maxfreq > self.fs/2 or maxfreq <= minfreq:
                cm.var_maxf.set(self.fs/2) # Reset widget
                if maxfreq > self.fs/2:
                    text = "The maximum frequency can't be greater than the half of the sample frequency (" + str(self.fs/2) + "Hz)."
                    tk.messagebox.showerror(parent=cm, title="Maximum frequency too big", message=text) # show error
                elif maxfreq <= minfreq:
                    text = "The maximum frequency must be greater than the minimum frequency (" + str(minfreq) + "Hz)."
                    tk.messagebox.showerror(parent=cm, title="Maximum frequency too small", message=text) # show error
            else: return True

        def minpitchEntry(event):
            minPitch = cm.var_minp.get()
            maxPitch = cm.var_maxp.get()
            if minPitch >= maxPitch:
                cm.var_minp.set('75.0') # Reset widget
                cm.var_maxp.set('600.0') # Reset widget
                text = "The minimum pitch must be smaller than the maximum pitch (" + str(maxPitch) + "Hz)."
                tk.messagebox.showerror(parent=cm, title="Pitch floor too big", message=text) # show error
            else: return True

        def maxpitchEntry(event):
            minPitch = cm.var_minp.get()
            maxPitch = cm.var_maxp.get()
            if maxPitch <= minPitch:
                cm.var_minp.set('75.0') # Reset widget
                cm.var_maxp.set('600.0') # Reset widget
                text = "The maximum pitch must be greater than the minimum pitch (" + str(minPitch) + "Hz)."
                tk.messagebox.showerror(parent=cm, title="Pitch ceiling too small", message=text) # show error
            else: return True

        def fundfreqEntry(event):
            fundfreq = cm.var_fund.get()
            if fundfreq < 1:
                cm.var_fund.set('1')
                text = "The minimum value of the fundamental frequency response is 1."
                tk.messagebox.showerror(parent=cm, title="Fundamental frequency response too small", message=text) # show error
            elif fundfreq > (self.fs/2): # max fundfreq = (self.fs/2)-(max(anchura de banda)/2) (?)
                cm.var_fund.set(self.fs/2)
                text = "The maximum frequency can't be greater than the half of the sample frequency (" + str(self.fs/2) + "Hz)."
                tk.messagebox.showerror(parent=cm, title="Fundamental frequency response too big", message=text) # show error
            else: return True
        
        def centerEntry(event):
            center = cm.var_cent.get()
            fcut1 = cm.var_cut1.get()
            fcut2 = cm.var_cut2.get()
            if center <= fcut1 or center >= fcut2:
                cm.var_cent.set(int((fcut1+fcut2)/2))
                text = "The center frequency must be a value between fcut1 (" + str(fcut1) + ") and fcut2 (" + str(fcut2) + ")."
                tk.messagebox.showerror(parent=cm, title="Wrong center frequency value", message=text) # show error
            else: return True
        
        def fcut1Entry(event):
            center = cm.var_cent.get()
            fcut1 = cm.var_cut1.get()
            fcut2 = cm.var_cut2.get()
            if fcut1 >= fcut2 or fcut1 >= center:
                c1 = fcut2-center
                c1 = center-c1
                cm.var_cut1.set(c1)
                text = "Fcut1 must be a smaller value than center (" + str(center) + ") and fcut2 (" + str(fcut2) + ")."
                tk.messagebox.showerror(parent=cm, title="Wrong fcut1 value", message=text) # show error
            else: return True
        
        def fcut2Entry(event):
            center = cm.var_cent.get()
            fcut1 = cm.var_cut1.get()
            fcut2 = cm.var_cut2.get()
            if fcut2 <= fcut1 or fcut2 <= center:
                c2 = center-fcut1
                c2 = center+c2
                cm.var_cut1.set(c2)
                text = "Fcut2 must be a greater value than center (" + str(center) + ") and fcut1 (" + str(fcut1) + ")."
                tk.messagebox.showerror(parent=cm, title="Wrong fcut2 value", message=text) # show error
            else: return True

        def betaEntry(event):
            beta = cm.var_beta.get()
            if beta < 0 or beta > 14:
                cm.var_beta.set('0') # Reset widget
                text = "The value of beta must be a number between 0 and 14."
                tk.messagebox.showerror(parent=cm, title="Incorrect value of beta", message=text) # show error
            else: return True

        # calling functions after entering a value and pressing enter
        ent_size.bind('<Return>', windowLengthEntry)
        ent_over.bind('<Return>', overlapEntry)
        ent_minf.bind('<Return>', minfreqEntry)
        ent_maxf.bind('<Return>', maxfreqEntry)
        ent_minp.bind('<Return>', minpitchEntry)
        ent_maxp.bind('<Return>', maxpitchEntry)
        ent_fund.bind('<Return>', fundfreqEntry)
        ent_cent.bind('<Return>', centerEntry)
        ent_cut1.bind('<Return>', fcut1Entry)
        ent_cut2.bind('<Return>', fcut2Entry)
        ent_beta.bind('<Return>', betaEntry)

        # positioning Entrys
        ent_size.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_over.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        ent_minf.grid(column=1, row=6, sticky=tk.EW, padx=5, pady=5)
        ent_maxf.grid(column=1, row=7, sticky=tk.EW, padx=5, pady=5)
        ent_minp.grid(column=1, row=11, sticky=tk.EW, padx=5, pady=5)
        ent_maxp.grid(column=1, row=12, sticky=tk.EW, padx=5, pady=5)
        ent_fund.grid(column=3, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_cent.grid(column=3, row=4, sticky=tk.EW, padx=5, pady=5)
        ent_cut1.grid(column=3, row=5, sticky=tk.EW, padx=5, pady=5)
        ent_cut2.grid(column=3, row=6, sticky=tk.EW, padx=5, pady=5)
        ent_beta.grid(column=3, row=11, sticky=tk.EW, padx=5, pady=5)

        # RADIOBUTTONS
        cm.var_draw = tk.IntVar(value=1)
            
        rdb_lin = tk.Radiobutton(cm, text='linear', variable=cm.var_draw, value=1, state='disabled')
        rdb_mel = tk.Radiobutton(cm, text='mel', variable=cm.var_draw, value=2, state='disabled')
           
        rdb_lin.grid(column=1, row=8, sticky=tk.W)
        rdb_mel.grid(column=1, row=8, sticky=tk.NS)

        # BUTTONS
        # Checks if all the values inserted by the user are correct
        def checkValues():
            choice = cm.var_opts.get()
            windSize = cm.var_size.get() # window size in seconds
            overlap = cm.var_over.get() # overlap in seconds
            minfreq = cm.var_minf.get()
            maxfreq = cm.var_maxf.get()
            beta = cm.var_beta.get()
            minpitch = cm.var_minp.get()
            maxpitch = cm.var_maxp.get()
            fundfreq = cm.var_fund.get()
            center = cm.var_cent.get()
            fcut1 = cm.var_cut1.get()
            fcut2 = cm.var_cut2.get()

            if choice == 'STFT' or choice == 'STFT + Spect' or choice == 'Spectral Centroid' or choice == 'Spectrogram' or choice == 'Filtering' or choice == 'Short-Time-Energy':
                if choice == 'Short-Time-Energy' and betaEntry(beta)!=True:
                    return
                if minfreqEntry(minfreq)!=True or maxfreqEntry(maxfreq)!=True:
                    return
                if choice == 'Filtering' and (fundfreqEntry(fundfreq)!=True or centerEntry(center)!=True or fcut1Entry(fcut1)!=True or fcut2Entry(fcut2)!=True):
                    return
                if choice != 'Filtering' and windowLengthEntry(windSize) != True:
                    return
                if (choice == 'STFT + Spect' or choice == 'Spectral Centroid' or choice == 'Short-Time-Energy' or choice == 'Spectrogram') and overlapEntry(overlap) != True:
                    return
            elif choice == 'Pitch' and (minpitchEntry(minpitch) != True or maxpitchEntry(maxpitch) != True):
                return
            
            self.plotFigure(cm, choice, windSize, overlap, minfreq, maxfreq, beta)

        but_adse = ttk.Button(cm, state='disabled', command=lambda: self.adse.advancedSettings(), text='Advanced settings')
        but_freq = ttk.Button(cm, state='disabled', command=lambda: self.plotFiltFreqResponse(cm), text='Filter Frequency Response')
        but_rese = ttk.Button(cm, state='disabled', text='Reset Signal')
        # but_fisi = ttk.Button(cm, state='disabled', text='Filter Signal')
        but_plot = ttk.Button(cm, command=lambda: checkValues(), text='Plot')
        but_help = ttk.Button(cm, command=lambda: self.controller.help.createHelpMenu(cm, 8), text='🛈', width=2)

        # positioning Buttons
        but_adse.grid(column=1, row=13, sticky=tk.EW, padx=5, pady=5)
        but_freq.grid(column=3, row=8, sticky=tk.EW, padx=5, pady=5)
        but_rese.grid(column=3, row=9, sticky=tk.EW, padx=5, pady=5)
        # but_fisi.grid(column=3, row=9, sticky=tk.EW, padx=5, pady=5)
        but_plot.grid(column=3, row=14, sticky=tk.EW, padx=5, pady=5)
        but_help.grid(column=2, row=14, sticky=tk.E, padx=5, pady=5)

        # OPTION MENUS
        cm.options = ('FT','STFT', 'Spectrogram','STFT + Spect', 'Short-Time-Energy', 'Pitch', 'Spectral Centroid', 'Filtering')
        cm.opt_wind = ('Bartlett','Blackman', 'Hamming','Hanning', 'Kaiser')
        cm.opt_nfft = [2**9, 2**10, 2**11, 2**12, 2**13, 2**14, 2**15, 2**16, 2**17, 2**18, 2**19]
        cm.opt_meth = ('Autocorrelation', 'Cross-correlation', 'Subharmonics', 'Spinet')
        cm.opt_pass = ('Lowpass','Highpass', 'Bandpass', 'Bandstop')
        cm.opt_filt = ('Butterworth','Elliptic', 'Chebyshev I', 'Chebyshev II', 'FIR least-squares')

        cm.var_opts = tk.StringVar()
        cm.var_wind = tk.StringVar()
        cm.var_nfft = tk.IntVar()
        cm.var_meth = tk.StringVar()
        cm.var_filt = tk.StringVar()
        cm.var_pass = tk.StringVar()

        # Called when changing the main option (FT, STFT, etc.) for disabling or activating widgets
        def displayOptions(choice):
            if choice == 'FT' or choice == 'STFT' or choice == 'Pitch' or choice == 'Filtering': 
                ent_over.config(state='disabled')
            else: ent_over.config(state='normal')

            if choice == 'FT' or choice == 'Pitch' or choice == 'Filtering': 
                ent_size.config(state='disabled')
            else: ent_size.config(state='normal')

            if choice == 'Filtering':
                ent_fund.config(state='normal')
                ent_cent.config(state='normal')
                ent_cut1.config(state='normal')
                ent_cut2.config(state='normal')
                dd_filt.config(state='active')
                dd_pass.config(state='active')
                but_freq.configure(state='active')
                but_rese.configure(state='active')
                # but_fisi.configure(state='active')
            else:
                ent_fund.config(state='disabled')
                ent_cent.config(state='disabled')
                ent_cut1.config(state='disabled')
                ent_cut2.config(state='disabled')
                dd_filt.config(state='disabled')
                dd_pass.config(state='disabled')
                but_freq.configure(state='disabled')
                but_rese.configure(state='disabled')
                # but_fisi.configure(state='disabled')

            if choice == 'Pitch':
                self.adse.createVariables() # create the variables of advanced settings
                dd_meth.config(state='active')
                ent_minp.config(state='normal')
                ent_maxp.config(state='normal')
                but_adse.config(state='active')
            else:
                dd_meth.config(state='disabled')
                ent_minp.config(state='disabled')
                ent_maxp.config(state='disabled')
                but_adse.config(state='disabled')

            if choice == 'Spectrogram' or choice == 'STFT + Spect' or choice == 'Spectral Centroid': 
                rdb_lin.config(state='active')
                rdb_mel.config(state='active')
            else: 
                rdb_lin.config(state='disabled')
                rdb_mel.config(state='disabled')

            if choice == 'Spectrogram' or choice == 'STFT + Spect' or choice == 'Spectral Centroid' or choice == 'Filtering':
                ent_minf.config(state='normal')
                ent_maxf.config(state='normal')
            else:
                ent_minf.config(state='disabled')
                ent_maxf.config(state='disabled')

            if choice == 'STFT' or choice == 'Spectrogram' or choice == 'STFT + Spect' or choice == 'Spectral Centroid' or choice == 'Short-Time-Energy':
                dd_wind.config(state='active')
            else: dd_wind.config(state='disabled')

            if choice == 'STFT' or choice == 'Spectrogram' or choice == 'STFT + Spect' or choice == 'Spectral Centroid':
                dd_nfft.config(state='active')
            else: dd_nfft.config(state='disabled')

            if choice == 'Short-Time-Energy':
                ent_beta.config(state='normal')
            else: ent_beta.config(state='disabled')

        # creating option menus
        dd_opts = ttk.OptionMenu(cm, cm.var_opts, cm.options[0], *cm.options, command=displayOptions)
        dd_wind = ttk.OptionMenu(cm, cm.var_wind, cm.opt_wind[0], *cm.opt_wind)
        dd_nfft = ttk.OptionMenu(cm, cm.var_nfft, cm.opt_nfft[0], *cm.opt_nfft)
        dd_meth = ttk.OptionMenu(cm, cm.var_meth, cm.opt_meth[0], *cm.opt_meth)
        dd_pass = ttk.OptionMenu(cm, cm.var_pass, cm.opt_pass[0], *cm.opt_pass)
        dd_filt = ttk.OptionMenu(cm, cm.var_filt, cm.opt_filt[0], *cm.opt_filt)

        # size of the OptionMenus
        dd_opts.config(width=16)
        dd_wind.config(width=18, state='disabled')
        dd_nfft.config(width=18, state='disabled')
        dd_meth.config(width=18, state='disabled')
        dd_pass.config(width=18, state='disabled')
        dd_filt.config(width=18, state='disabled')

        # positioning OptionMenus
        dd_opts.grid(column=2, row=0, sticky=tk.EW, padx=5)
        dd_wind.grid(column=1, row=1, sticky=tk.EW, padx=5)
        dd_nfft.grid(column=1, row=3, sticky=tk.EW, padx=5)
        dd_meth.grid(column=1, row=10, sticky=tk.EW, padx=5)
        dd_pass.grid(column=3, row=2, sticky=tk.EW, padx=5)
        dd_filt.grid(column=3, row=7, sticky=tk.EW, padx=5)


    ###########
    # METHODS #
    ###########

    # Updates the OptionMenu 'om' with the option list 'opt' and variable 'var' passed as a parameter
    def updateOptionMenu(self, cm, dd_nfft):
        menu = dd_nfft["menu"]
        menu.delete(0, "end")
        for o in cm.opt_nfft:
            menu.add_command(label=o, command=lambda value=o: cm.var_nfft.set(value))
        cm.var_nfft.set(cm.opt_nfft[0])

    def yticks(self, minfreq, maxfreq):
        freq = maxfreq-minfreq
        if freq <=100: 
            plt.yticks(np.arange(minfreq,maxfreq,20))
        elif freq <=1000:
            plt.yticks(np.arange(minfreq,maxfreq,100))
        else:
            x = freq//1000
            y = x//8
            plt.yticks(np.arange(minfreq,maxfreq,1000*(y+1)))

    def colorBar(self, fig, x, img):
        fig.subplots_adjust(right=0.9) # leave space for the color bar
        sub_ax = plt.axes([0.91, 0.12, 0.02, x]) # add a small custom axis (left, bottom, width, height)
        fig.colorbar(img, cax=sub_ax, format='%+2.0f dB') # %4.2e, {x:.2e}

    def createSpanSelector(self, ax):
        # Plays the audio of the selected fragment of the fragment
        def listenFragFrag(xmin, xmax):
            ini, end = np.searchsorted(self.time, (xmin, xmax))
            selectedAudio = self.audio[ini:end+1]
            sd.play(selectedAudio, self.fs)
            
        span = SpanSelector(ax, listenFragFrag, 'horizontal', useblit=True, interactive=True, drag_from_anywhere=True)
        return span
    

    #####################
    # CALCULATE METHODS #
    #####################

    def calculateWaveform(self, ax):
        ax.plot(self.time, self.audio)
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        ax.set(xlim=[0, self.duration], xlabel='Time (s)', ylabel='Amplitude', title='Waveform')

    
    def calculateSTFT(self, audioFragWindow, nfft):
        stft = np.fft.fft(audioFragWindow, nfft)
        return stft[range(int(nfft/2))]
    
    
    def calculateSpectrogram(self, cm, audio, ax, window, windSizeSampInt, hopSize, cmap):
        nfftUser = cm.var_nfft.get()
        draw = cm.var_draw.get()
        minfreq = cm.var_minf.get()
        maxfreq = cm.var_maxf.get()

        # Calculate the linear/mel spectrogram
        if draw == 1: # linear
            linear = librosa.stft(audio, n_fft=nfftUser, hop_length=hopSize, win_length=windSizeSampInt, window=window, center=True, dtype=None, pad_mode='constant')
            linear_dB = librosa.amplitude_to_db(np.abs(linear), ref=np.max)
            img = librosa.display.specshow(linear_dB, x_axis='time', y_axis='linear', sr=self.fs, fmin=minfreq, fmax=maxfreq, ax=ax, hop_length=hopSize, cmap=cmap)
            ax.set(xlim=[0, self.duration], ylim=[minfreq, maxfreq], title='Linear spectrogram')
        else: # mel
            mel = librosa.feature.melspectrogram(y=audio, sr=self.fs, win_length=windSizeSampInt, n_fft=nfftUser, window=window, fmin=minfreq, fmax=maxfreq, hop_length=hopSize)
            mel_dB = librosa.power_to_db(mel)
            img = librosa.display.specshow(mel_dB, x_axis='time', y_axis='mel', sr=self.fs, fmin=minfreq, fmax=maxfreq, ax=ax, hop_length=hopSize, cmap=cmap)
            ax.set(xlim=[0, self.duration], ylim=[minfreq, maxfreq], title='Mel-frequency spectrogram')
        self.yticks(minfreq, maxfreq) # represent the numbers of y axis
        
        return img
    
    
    def calculateSC(self, audioFragWindow):
        magnitudes = np.abs(np.fft.rfft(audioFragWindow)) # magnitudes of positive frequencies
        length = len(audioFragWindow)
        freqs = np.abs(np.fft.fftfreq(length, 1.0/self.fs)[:length//2+1]) # positive frequencies
        return np.sum(magnitudes*freqs)/np.sum(magnitudes) # return weighted mean
    
    
    def calculateSTE(self, sig, win, windSizeSampInt):
        window1 = signal.get_window(win, windSizeSampInt)
        window = window1 / len(window1)
        return signal.convolve(sig**2, window**2, mode='same')
    
    
    def calculatePitch(self, method, minpitch, maxpitch, maxCandidates):
        # Convert the numpy array containing the audio fragment into a wav file
        write('wav/frag.wav', self.fs, self.audio) # generates a wav file in the current folder

        silenceTh, voiceTh, octaveCost, octJumpCost, vcdUnvcdCost, accurate = self.adse.getAutocorrelationVars()
        if accurate == 1: accurate_bool = True
        else: accurate_bool = False

        # Calculate the pitch of the generated wav file using parselmouth
        snd = parselmouth.Sound('wav/frag.wav')
        if method == 'Autocorrelation':
            pitch = snd.to_pitch_ac(pitch_floor=minpitch,
                                    max_number_of_candidates=maxCandidates,
                                    very_accurate=accurate_bool,
                                    silence_threshold=silenceTh,
                                    voicing_threshold=voiceTh,
                                    octave_cost=octaveCost,
                                    octave_jump_cost=octJumpCost,
                                    voiced_unvoiced_cost=vcdUnvcdCost,
                                    pitch_ceiling=maxpitch)
        elif method == 'Cross-correlation':
            pitch = snd.to_pitch_cc(pitch_floor=minpitch, 
                                    max_number_of_candidates=maxCandidates,
                                    very_accurate=accurate_bool,
                                    silence_threshold=silenceTh,
                                    voicing_threshold=voiceTh,
                                    octave_cost=octaveCost,
                                    octave_jump_cost=octJumpCost,
                                    voiced_unvoiced_cost=vcdUnvcdCost,
                                    pitch_ceiling=maxpitch)
        elif method == 'Subharmonics':
            maxFreqComp, maxSubharm, compFactor, pointsPerOct = self.adse.getSubharmonicsVars()
            pitch = snd.to_pitch_shs(minimum_pitch=minpitch, 
                                    max_number_of_candidates=maxCandidates,
                                    maximum_frequency_component=maxFreqComp,
                                    max_number_of_subharmonics=maxSubharm,
                                    compression_factor=compFactor,
                                    ceiling=maxpitch,
                                    number_of_points_per_octave=pointsPerOct)
        elif method == 'Spinet':
            windLen, minFiltFreq, maxFiltFreq, numFilters = self.adse.getSpinetVars()
            pitch = snd.to_pitch_spinet(window_length=windLen,
                                        minimum_filter_frequency=minFiltFreq,
                                        maximum_filter_frequency=maxFiltFreq,
                                        number_of_filters=numFilters,
                                        ceiling=maxpitch,
                                        max_number_of_candidates=maxCandidates)
        pitch_values = pitch.selected_array['frequency'] # extract selected pitch contour
        pitch_values[pitch_values==0] = np.nan # replace unvoiced samples by NaN to not plot

        return pitch, pitch_values
    

    ################
    # PLOT METHODS #
    ################
    
    # Plots the waveform and the Fast Fourier Transform (FFT) of the fragment
    def plotFT(self, cm):
        self.figFragFT, axFragFT = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        self.figFragFT.canvas.manager.set_window_title(self.fileName+'-FT')

        fft = np.fft.fft(self.audio) / self.lenAudio # Normalize amplitude
        fft2 = fft[range(int(self.lenAudio/2))] # Exclude sampling frequency
        values = np.arange(int(self.lenAudio/2))
        frequencies = values / (self.lenAudio/self.fs) # values / time period

        # 'self.time' and 'self.audio' need to have the same first dimension
        if len(self.time) < len(self.audio):
            self.audio = self.audio[:-1].copy() # delete last element of the numpy array
        elif len(self.time) > len(self.audio):
            self.time = self.time[:-1].copy() # delete last element of the numpy array

        self.calculateWaveform(axFragFT[0])
        axFragFT[1].plot(frequencies, 20*np.log10(abs(fft2)))
        axFragFT[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Fourier Transform')

        self.aux.saveasWavCsv(cm, self.figFragFT, self.time, self.audio, 0.5, self.fs) # save waveform as csv
        self.aux.saveasCsv(self.figFragFT, frequencies, 20*np.log10(abs(fft2)), 0.05, 'FT') # save FT as csv

        # TO-DO: connect figFrag with w1Button in signalVisualizer

        self.span = self.createSpanSelector(axFragFT[0]) # Select a fragment with the cursor and play the audio of that fragment
        self.figFragFT.show() # show the figure

    

    def plotSTFT(self, cm, stft, frequencies, title):
        figFragSTFT, axFragSTFT = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        figFragSTFT.canvas.manager.set_window_title(str(self.fileName)+'-STFT-'+title) # set title to the figure window

        self.calculateWaveform(axFragSTFT[0])
        line1, = axFragSTFT[1].plot(frequencies, 20*np.log10(abs(stft)))
        axFragSTFT[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Short Time Fourier Transform')

        self.aux.saveasWavCsv(cm, figFragSTFT, self.time, self.audio, 0.5, self.fs) # save waveform as csv
        self.aux.saveasCsv(figFragSTFT, frequencies, 20*np.log10(abs(stft)), 0.05, 'STFT') # save FT as csv
        
        self.cursor = Cursor(axFragSTFT[0], horizOn=False, useblit=True, color='black', linewidth=1)
        self.span = self.createSpanSelector(axFragSTFT[0]) # Select a fragment with the cursor and play the audio of that fragment

        return axFragSTFT, line1
    


    def plotSpectrogram(self, cm, window, windSizeSampInt, hopSize, cmap, title):
        figFragSpect, axFragSpect = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        figFragSpect.canvas.manager.set_window_title(str(self.fileName)+'-Spectrogram-'+title) # set title to the figure window

        # Calculate the linear/mel spectrogram
        img = self.calculateSpectrogram(cm, self.audio, axFragSpect[1], window, windSizeSampInt, hopSize, cmap)
        self.colorBar(figFragSpect, 0.3, img)

        self.calculateWaveform(axFragSpect[0])
        self.aux.saveasWavCsv(cm, figFragSpect, self.time, self.audio, 0.5, self.fs) # save waveform as csv

        self.multicursor = MultiCursor(figFragSpect.canvas, (axFragSpect[0], axFragSpect[1]), color='black', lw=1)
        self.span = self.createSpanSelector(axFragSpect[0]) # Select a fragment with the cursor and play the audio of that fragment
        plt.show() # show the figure



    def plotSTFTspect(self, cm, stft, frequencies, window, windSizeSampInt, hopSize, cmap, title):
        figFragSTFTSpect, axFragSTFTSpect = plt.subplots(3, figsize=(12,6))
        plt.subplots_adjust(hspace=.6) # to avoid overlapping between xlabel and title
        figFragSTFTSpect.canvas.manager.set_window_title(str(self.fileName)+'-STFT+Spectrogram-'+title) # set title to the figure window

        # Calculate the linear/mel spectrogram
        img = self.calculateSpectrogram(cm, self.audio, axFragSTFTSpect[2], window, windSizeSampInt, hopSize, cmap)
        self.colorBar(figFragSTFTSpect, 0.17, img)

        self.calculateWaveform(axFragSTFTSpect[0])
        line1, = axFragSTFTSpect[1].plot(frequencies, 20*np.log10(abs(stft)))
        axFragSTFTSpect[1].set(xlim=[0, max(frequencies)], xlabel='Frequency (Hz)', ylabel='Amplitude (dB)', title='Short Time Fourier Transform')

        self.aux.saveasWavCsv(cm, figFragSTFTSpect, self.time, self.audio, 0.65, self.fs) # save waveform as csv
        self.aux.saveasCsv(figFragSTFTSpect, frequencies, 20*np.log10(abs(stft)), 0.35, 'STFT') # save STFT as csv
        
        self.multicursor = MultiCursor(figFragSTFTSpect.canvas, (axFragSTFTSpect[0], axFragSTFTSpect[2]), color='black', lw=1)
        self.span = self.createSpanSelector(axFragSTFTSpect[0]) # Select a fragment with the cursor and play the audio of that fragment

        return axFragSTFTSpect, line1



    def plotSC(self, cm, audioFragWind2, window, windSizeSampInt, nfftUser, overlapSamp, hopSize, cmap, title):
        figFragSC, axFragSC = plt.subplots(3, figsize=(12,6))
        plt.subplots_adjust(hspace=.6) # to avoid overlapping between xlabel and title
        figFragSC.canvas.manager.set_window_title(str(self.fileName)+'-SpectralCentroid-'+title) # set title to the figure window

        # Calculate the spectral centroid in the FFT as a vertical line
        spectralC = self.calculateSC(audioFragWind2)
        scValue = str(round(spectralC, 2)) # take only two decimals

        # Calculate the spectral centroid in the log power linear/mel spectrogram
        sc = librosa.feature.spectral_centroid(y=self.audio, sr=self.fs, n_fft=nfftUser, hop_length=hopSize, window=window, win_length=windSizeSampInt)
        times = librosa.times_like(sc, sr=self.fs, hop_length=hopSize, n_fft=nfftUser)
        
        # Calculate the linear/mel spectrogram
        img = self.calculateSpectrogram(cm, self.audio, axFragSC[2], window, windSizeSampInt, hopSize, cmap)
        self.colorBar(figFragSC, 0.17, img)

        self.calculateWaveform(axFragSC[0])
        _, freqs = axFragSC[1].psd(audioFragWind2, NFFT=windSizeSampInt, pad_to=nfftUser, Fs=self.fs, window=window, noverlap=overlapSamp)
        axFragSC[1].axvline(x=spectralC, color='r', linewidth='1') # draw a vertical line in x=value of the spectral centroid
        axFragSC[1].set(xlim=[0, max(freqs)], xlabel='Frequency (Hz)', ylabel='Power spectral density (dB/Hz)', title='Power spectral density using fft, spectral centroid value is '+ scValue)
        line1, = axFragSC[2].plot(times, sc.T, color='w') # draw the white line
        axFragSC[2].set(xlim=[0, self.duration], title='log Power spectrogram')

        self.aux.saveasWavCsv(cm, figFragSC, self.time, self.audio, 0.65, self.fs) # save waveform as csv
        self.aux.saveasCsv(figFragSC, times, sc.T, 0.05, 'SC') # save the white line as csv
        
        self.multicursor = MultiCursor(figFragSC.canvas, (axFragSC[0], axFragSC[2]), color='black', lw=1)
        self.span = self.createSpanSelector(axFragSC[0]) # Select a fragment with the cursor and play the audio of that fragment

        return axFragSC, line1
    


    def plotSTE(self, cm, windType1, windSizeSampInt, title):
        figFragSTE, axFragSTE = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        figFragSTE.canvas.manager.set_window_title(str(self.fileName)+'-STE-'+title) # set title to the figure window

        # Calculate the Short-Time-Energy
        signal = np.array(self.audio, dtype=float)
        time = np.arange(len(signal)) * (1.0/self.fs)
        ste = self.calculateSTE(signal, windType1, windSizeSampInt)

        self.calculateWaveform(axFragSTE[0])
        axFragSTE[1].plot(time, ste)
        axFragSTE[1].set(xlim=[0, self.duration], xlabel='Time (s)', ylabel='Amplitude (dB)', title='Short Time Energy')

        self.aux.saveasWavCsv(cm, figFragSTE, self.time, self.audio, 0.5, self.fs) # save waveform as csv
        self.aux.saveasCsv(figFragSTE, time, ste, 0.05, 'STE') # save STE as csv

        self.span = self.createSpanSelector(axFragSTE[0]) # Select a fragment with the cursor and play the audio of that fragment
        plt.show() # show the figure



    def plotPitch(self, cm):
        method = cm.var_meth.get()
        minpitch = cm.var_minp.get()
        maxpitch = cm.var_maxp.get()
        maxCandidates, drawStyle = self.adse.getVariables()
        
        figFragPitch, axFragPitch = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        figFragPitch.canvas.manager.set_window_title('Pitch-Method_'+ str(method) +'-PitchFloor_'+ str(minpitch) + 'Hz-PitchCeiling_'+ str(maxpitch) + 'Hz') # set title to the figure window

        pitch, pitch_values = self.calculatePitch(method, minpitch, maxpitch, maxCandidates)

        self.multicursor = MultiCursor(figFragPitch.canvas, (axFragPitch[0], axFragPitch[1]), color='black', lw=1)

        if drawStyle == 1: draw = '-'
        else: draw = 'o'

        self.calculateWaveform(axFragPitch[0])
        axFragPitch[1].plot(pitch.xs(), pitch_values, draw)
        axFragPitch[1].set(xlim=[0, self.duration], xlabel='Time (s)', ylabel='Frequency (Hz)', title='Pitch measurement overtime')

        self.aux.saveasWavCsv(cm, figFragPitch, self.time, self.audio, 0.5, self.fs) # save waveform as csv
        self.aux.saveasCsv(figFragPitch, pitch.xs(), pitch_values, 0.05, 'Pitch') # save Pitch as csv        

        self.span = self.createSpanSelector(axFragPitch[0]) # Select a fragment with the cursor and play the audio of that fragment
        plt.show() # show the figure



    def designFilter(self, fundfreq, center, fcut1, fcut2, filter, type):
        # Design filter
        norm_pass = fundfreq/(self.fs/2)
        norm_stop = 1.5*norm_pass

        if filter == 'Butterworth':
            N, Wn = signal.buttord(wp=1000, ws=1200, gpass=3, gstop=40, fs=self.fs)
            b, a = signal.butter(24, Wn=2000, btype='lowpass', fs=self.fs)
        elif filter == 'Elliptic':
            N, Wn = signal.ellipord(wp=1000, ws=1001, gpass=3, gstop=40, fs=self.fs)
            b, a = signal.ellip(N, 3, 40, Wn, btype=type, fs=self.fs)
        elif filter == 'Chebyshev I':
            N, Wn = signal.cheb1ord(wp=norm_pass, ws=norm_stop, gpass=fcut1, gstop=fcut2, fs=self.fs)
            b, a = signal.cheby1(N, 5, Wn, btype=type, fs=self.fs)
        elif filter == 'Chebyshev II':
            N, Wn = signal.cheb2ord(wp=norm_pass, ws=norm_stop, gpass=fcut1, gstop=fcut2, fs=self.fs)
            b, a = signal.cheby2(N, 40, Wn, btype=type, fs=self.fs)
        # elif filter == 'FIR least-squares':
        #     coeffs = signal.firls(fs=self.audiofs)

        filteredSignal = signal.lfilter(b, a, self.audio)

        return filteredSignal

    def plotFiltering(self, cm, window, windSizeSampInt, hopSize, cmap):
        fundfreq = cm.var_fund.get()
        center = cm.var_cent.get()
        fcut1 = cm.var_cut1.get()
        fcut2 = cm.var_cut2.get()
        filter = cm.var_filt.get() # butterworth, elliptic...
        type = cm.var_pass.get() # lowpass, bandpass...

        figFragFilt, axFragFilt = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        figFragFilt.canvas.manager.set_window_title('Filtering') # set title to the figure window
        figFragFilt.canvas.manager.set_window_title('Filtering-FundFreqMult_'+ str(fundfreq) +'-Center_'+ str(center) + '-Fcut1_'+ str(fcut1) + 'Hz-Fcut2_'+ str(fcut2) + 'Hz' + '-Filter_'+ str(filter)) # set title to the figure window

        filteredSignal = self.designFilter(fundfreq, center, fcut1, fcut2, filter, type)

        # Calculate the linear/mel spectrogram
        img = self.calculateSpectrogram(cm, filteredSignal, axFragFilt[1], window, windSizeSampInt, hopSize, cmap)
        self.colorBar(figFragFilt, 0.3, img)

        self.calculateWaveform(axFragFilt[0])
        self.aux.saveasWavCsv(cm, figFragFilt, self.time, self.audio, 0.5, self.fs) # save waveform as csv

        self.span = self.createSpanSelector(axFragFilt[0]) # Select a fragment with the cursor and play the audio of that fragment
        plt.show() # show the figure

    def plotFiltFreqResponse(self, fundfreq, center, fcut1, fcut2):
        figFragFFR, axFragFFR = plt.subplots(2, figsize=(12,6))
        plt.subplots_adjust(hspace=.4) # to avoid overlapping between xlabel and title
        figFragFFR.canvas.manager.set_window_title('Filter frequency response') # set title to the figure window

        _, b, a = self.designFilter(fundfreq, center, fcut1, fcut2)

        # Calculate the filter frequency response
        # w, h = signal.freqz(b, a)
        h = signal.TransferFunction(b, a)
        w, mag, phase = signal.bode(h)

        axFragFFR[0].semilogx(w, mag) # Magnitude plot
        axFragFFR[0].set(xlabel='Frequency (Hz)', ylabel='Magnitude (dB)', title='Frequency Response, Magnitude')
        # axFragFFR[1].plot(w, np.abs(h))
        axFragFFR[1].semilogx(w, phase) # Phase plot
        axFragFFR[1].set(xlabel='Frequency (Hz)', ylabel='Phase (radians)', title='Frequency Response, Phase')

        plt.show() # show the figure



    # Called when pressing the 'Plot' button
    def plotFigure(self, cm, choice, windSize, overlap, minfreq, maxfreq, beta):
        list = self.aux.readFromCsv()
        cmap = mpl.colormaps[list[5][2]]
        # Values given by the user (that were not created in checkValues())
        windType = cm.var_wind.get()
        nfftUser = cm.var_nfft.get()
        draw = cm.var_draw.get()

        windSizeSamp = windSize * self.fs # window size in samples
        windSizeSampInt = int(windSizeSamp)
        overlapSamp = int(overlap * self.fs) # overlap in samples (int)
        hopSize = windSizeSampInt-overlapSamp

        title1 = 'Window_'+ str(windType) +'_'+ str(windSize) +'s-Nfft_'+ str(nfftUser) +'-Overlap_'+ str(overlap) +'s'
        titleSpec = '-MinFreq_'+ str(minfreq) + 'Hz-MaxFreq_'+ str(maxfreq) + 'Hz'
        titleSTFT = 'Window_'+ str(windType) +'_'+ str(windSize) +'s-Nfft_'+ str(nfftUser)
        titleSTE = 'Window_'+ str(windType) +'_'+ str(windSize) +'s-Overlap_'+ str(overlap) +'s-Beta_'+ str(beta)

        # Apply the window type to the window
        if windType == 'Bartlett':
            window = np.bartlett(windSizeSampInt)
            windType1 = 'bartlett' # used in STE
        elif windType == 'Blackman':
            window = np.blackman(windSizeSampInt)
            windType1 = 'blackman' # used in STE
        elif windType == 'Hamming':
            window = np.hamming(windSizeSampInt)
            windType1 = 'hamming' # used in STE
        elif windType == 'Hanning':
            window = np.hanning(windSizeSampInt)
            windType1 = 'hann' # used in STE
        elif windType == 'Kaiser':
            window = np.kaiser(windSizeSampInt, beta) # np.kaiser(windSizeSampInt, float:shape parameter for window)
            windType1 = ('kaiser', beta) # used in STE

        if choice == 'FT':
            if plt.fignum_exists(self.figFragFT.number):
                plt.close(self.figFragFT.number) # close the figure of the FT
            self.plotFT(cm) # create the figure of the FT (again)

        elif choice == 'STFT' or choice == 'STFT + Spect' or choice == 'Spectral Centroid':
            # The window is in the middle of the waveform by default
            midPoint_idx = int(self.lenAudio/2) # index of the middle point in the waveform
            midPoint = self.time[midPoint_idx] # value of the middle point

            # Define initial and end points of the window
            ini_idx = midPoint_idx - int(windSizeSamp/2) # index of the initial point
            end_idx = midPoint_idx + int(windSizeSamp/2) # index of the end point
            if ini_idx < 0: ini_idx = 0
            if end_idx > self.lenAudio-1: end_idx = self.lenAudio-1
            ini = self.time[ini_idx] # value of the initial point
            end = self.time[end_idx] # value of the end point

            audioFragWind = self.audio[ini_idx:end_idx+1]
            lenWindow = len(window)
            if lenWindow < len(audioFragWind):
                audioFragWind = audioFragWind[:-1].copy() # delete last element of the numpy array
            elif lenWindow > len(audioFragWind):
                window = window[:-1].copy() # delete last element of the numpy array
            audioFragWind2 = audioFragWind * window

            # Calculate the STFT
            stft = self.calculateSTFT(audioFragWind2, nfftUser)
            values = np.arange(int(nfftUser/2))
            frequencies = values * self.fs / nfftUser

            if choice == 'STFT':
                axFragSTFT, line1 = self.plotSTFT(cm, stft, frequencies, titleSTFT)
                ax0 = axFragSTFT[0]
            elif choice == 'STFT + Spect':
                axFragSTFTSpect, line1 = self.plotSTFTspect(cm, stft, frequencies, window, windSizeSampInt, hopSize, cmap, title1+titleSpec)
                midLineSpect = axFragSTFTSpect[2].axvline(x=midPoint, color='black', linewidth='0.5', fillstyle='full') # line in the middle (spectrogram)
                ax0 = axFragSTFTSpect[0]
            elif choice == 'Spectral Centroid':
                axFragSC, line1 = self.plotSC(cm, audioFragWind2, window, windSizeSampInt, nfftUser, overlapSamp, hopSize, cmap, title1+titleSpec)
                midLineSpectSC = axFragSC[2].axvline(x=midPoint, color='black', linewidth='0.5', fillstyle='full') # line in the middle (spectrogram)
                ax0 = axFragSC[0]

            # Draw the rectangle
            bottom, top = ax0.get_ylim()
            rectangle = Rectangle(xy=(ini,bottom), width=end-ini, height=top-bottom, alpha=0.5, color='silver', zorder=2)
            ax0.add_artist(rectangle) # draw the rectangle
            midLine = ax0.axvline(x=midPoint, color='black', linewidth='0.5', fillstyle='full', zorder=2) # line in the middle

            def get_window():
                return window

            # If the user changes the position of the window, recalculate the STFT/FFT
            def on_click(event):
                window = get_window()
                # if the user does left click in the waveform
                if event.button is MouseButton.LEFT and (choice == 'STFT' and event.inaxes == axFragSTFT[0]) or (choice == 'STFT + Spect' and event.inaxes == axFragSTFTSpect[0]) or (choice == 'Spectral Centroid' and event.inaxes == axFragSC[0]):
                     # Define the new initial and end points of the window
                    new_midPoint = event.xdata
                    new_midPoint_idx = midPoint_idx
                    for i in range(self.lenAudio):
                        if self.time[i] == new_midPoint or (self.time[i] < new_midPoint and self.time[i+1] > new_midPoint):
                            new_midPoint_idx = i
                            break
                    new_ini_idx = new_midPoint_idx - int(windSizeSamp/2)
                    new_end_idx = new_midPoint_idx + int(windSizeSamp/2)
                    if new_ini_idx < 1 or new_end_idx > self.lenAudio: 
                        text = "At that point the window gets out of index."
                        tk.messagebox.showerror(parent=cm, title="Window out of index", message=text) # show error
                        return
                    
                    new_audioFragWind = self.audio[new_ini_idx:new_end_idx+1]
                    if lenWindow < len(new_audioFragWind):
                        new_audioFragWind = new_audioFragWind[:-1].copy() # delete last element of the numpy array
                    elif lenWindow > len(new_audioFragWind):
                        window = window[:-1].copy() # delete last element of the numpy array
                    new_audioFragWind2 = new_audioFragWind * window

                    if choice == 'Spectral Centroid':
                        # recalculate FFT
                        axFragSC[1].clear()
                        new_spectralC = self.calculateSC(new_audioFragWind2)
                        new_scValue = str(round(new_spectralC, 2)) # take only two decimals
                        _, new_freqs = axFragSC[1].psd(new_audioFragWind2, NFFT=windSizeSampInt, pad_to=nfftUser, Fs=self.fs, window=window, noverlap=overlapSamp)
                        axFragSC[1].axvline(x=new_spectralC, color='r', linewidth='1') # draw a vertical line in x=value of the spectral centroid
                        axFragSC[1].set(xlim=[0, max(new_freqs)], xlabel='Frequency (Hz)', ylabel='Power spectral density (dB/Hz)', title='Power spectral density using fft, spectral centroid value is '+ new_scValue)
                    else: # recalculate STFT
                        new_stft = self.calculateSTFT(new_audioFragWind2, nfftUser)
                        new_values = np.arange(int(nfftUser/2))
                        new_frequencies = new_values * self.fs / nfftUser
                        line1.set_xdata(new_frequencies)
                        line1.set_ydata(20*np.log10(abs(new_stft)))

                    # Move the window and rescale 'y' axis
                    midLine.set_xdata(new_midPoint)
                    if choice == 'STFT':
                        ax1 =  axFragSTFT[1]
                    elif choice == 'STFT + Spect':
                        ax1 =  axFragSTFTSpect[1]
                        midLineSpect.set_xdata(new_midPoint)
                    elif choice == 'Spectral Centroid':
                        ax1 =  axFragSC[1]
                        midLineSpectSC.set_xdata(new_midPoint)
                    ax1.relim()
                    ax1.autoscale_view()
                    new_ini = self.time[new_ini_idx]
                    rectangle.set_x(new_ini)

                    plt.show() # update the figure
                
            plt.connect('button_press_event', on_click) # when the mouse button is pressed, call on_click function
            plt.show() # show the figure

        elif choice == 'Spectrogram':
            self.plotSpectrogram(cm, window, windSizeSampInt, hopSize, cmap, title1+titleSpec)
        elif choice == 'Short-Time-Energy':
            self.plotSTE(cm, windType1, windSizeSampInt, titleSTE)
        elif choice == 'Pitch':
            self.plotPitch(cm)
        elif choice == 'Filtering':
            self.plotFiltering(cm, window, windSizeSampInt, hopSize, cmap)