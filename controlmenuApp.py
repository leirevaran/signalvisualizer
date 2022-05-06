import tkinter as tk
from tkinter import *
import matplotlib.pyplot as plt

class ControlMenuApp(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("Control menu")
        self.master['borderwidth'] = 10

        self.showControlMenu()
        
    def showControlMenu(self):
        # LABELS
        # Labels of OptionMenus
        lab_opts = Label(self.master, text='Choose an option')
        lab_wind = Label(self.master, text='Window')
        lab_nfft = Label(self.master, text='nfft')
        lab_meth = Label(self.master, text='Method')
        lab_data = Label(self.master, text='Data operations')

        # Labels of entrys
        lab_size = Label(self.master, text='Window size (s)')
        lab_over = Label(self.master, text='Overlap (s)')
        lab_fund = Label(self.master, text='Fund. freq. multiplication')
        lab_cent = Label(self.master, text='Center frequency')
        lab_cut1 = Label(self.master, text='Fcut1')
        lab_cut2 = Label(self.master, text='Fcut2')
        lab_fshz = Label(self.master, text='fs (Hz)')
        
        # positioning Labels
        lab_opts.grid(column=0, row=0, sticky=tk.E)
        lab_wind.grid(column=0, row=1, sticky=tk.E)
        lab_nfft.grid(column=0, row=3, sticky=tk.E)
        lab_meth.grid(column=0, row=5, sticky=tk.E)
        lab_data.grid(column=0, row=6, sticky=tk.E)

        lab_size.grid(column=0, row=2, sticky=tk.E)
        lab_over.grid(column=0, row=4, sticky=tk.E)
        lab_fund.grid(column=2, row=0, sticky=tk.E)
        lab_cent.grid(column=2, row=1, sticky=tk.E)
        lab_cut1.grid(column=2, row=2, sticky=tk.E)
        lab_cut2.grid(column=2, row=3, sticky=tk.E)
        lab_fshz.grid(column=0, row=8, sticky=tk.E)

        # ENTRYS
        self.var_size = StringVar(value='0.09')
        self.var_over = StringVar(value='0')
        self.var_fund = StringVar()
        self.lab_cent = StringVar()
        self.lab_cut1 = StringVar()
        self.lab_cut2 = StringVar()

        ent_size = Entry(self.master, textvariable=self.var_size)
        ent_over = Entry(self.master, textvariable=self.var_over)
        ent_fund = Entry(self.master, textvariable=self.var_fund)
        ent_cent = Entry(self.master, textvariable=self.lab_cent)
        ent_cut1 = Entry(self.master, textvariable=self.lab_cut1)
        ent_cut2 = Entry(self.master, textvariable=self.lab_cut2)

        # positioning Entrys
        ent_size.grid(column=1, row=2, sticky=tk.EW, columnspan=1)
        ent_over.grid(column=1, row=4, sticky=tk.EW, columnspan=1)
        ent_fund.grid(column=3, row=0, sticky=tk.EW)
        ent_cent.grid(column=3, row=1, sticky=tk.EW)
        ent_cut1.grid(column=3, row=2, sticky=tk.EW)
        ent_cut2.grid(column=3, row=3, sticky=tk.EW)

        # CHECKBOX
        self.var_form = StringVar(value=0)
        chk_form = Checkbutton(self.master, text='Formants', command=self.showFormants, variable=self.var_form)
        chk_form.grid(column=1, row=7, sticky=tk.W)

        # TEXT
        txt_fs = Text(self.master, height=1, width=10)
        fs = '16000' # TO-DO: loadApp.self.audiofs
        txt_fs.insert('0.0', fs)
        txt_fs.grid(column=1, row=8, sticky=tk.W)

        # BUTTONS
        but_freq = Button(self.master, text='Filter Frequency Response')
        but_rese = Button(self.master, text='Reset Signal')
        but_fisi = Button(self.master, text='Filter Signal')
        but_plot = Button(self.master, text='Plot', command=self.plotFigure)

        but_freq.grid(column=3, row=5, sticky=tk.EW)
        but_rese.grid(column=3, row=6, sticky=tk.EW)
        but_fisi.grid(column=3, row=7, sticky=tk.EW)
        but_plot.grid(column=3, row=8, sticky=tk.EW)

        # OPTION MENUS
        options = ['FT','STFT', 'Spectrogram','STFT + Spect', 'Short-Time-Energy', 'Pitch', 'Spectral Centroid', 'Filtering']
        opt_wind = ['Rectangular','Hanning', 'Hamming','Gaussian', 'Triangular', 'Chebyshev', 'Taylor', 'Bartlett', 'Kaiser']
        opt_nfft = ['2048','4096', '8192','16384', '32768', '65536', '131072', '262144', '524288', '1048576', '2097152', '4194304', '8388608']
        opt_meth = ['Cepstrum','Autocorrelation']
        opt_data = ['None','Median Filtering', 'Low Energy Suppresion']
        opt_filt = ['Butterworth','Elliptic', 'Chebyshev', 'FIR least-squares']

        self.var_opts = StringVar()
        self.var_wind = StringVar()
        self.var_nfft = StringVar()
        self.var_meth = StringVar()
        self.var_data = StringVar()
        self.var_filt = StringVar()

        self.var_opts.set(options[0])
        self.var_wind.set(opt_wind[0])
        self.var_nfft.set(opt_nfft[0])
        self.var_meth.set(opt_meth[0])
        self.var_data.set(opt_data[0])
        self.var_filt.set(opt_filt[0])

        # creating OptionMenus
        dd_opts = OptionMenu(self.master, self.var_opts, *options) # command=...
        dd_wind = OptionMenu(self.master, self.var_wind, *opt_wind)
        dd_nfft = OptionMenu(self.master, self.var_nfft, *opt_nfft)
        dd_meth = OptionMenu(self.master, self.var_meth, *opt_meth)
        dd_data = OptionMenu(self.master, self.var_data, *opt_data)
        dd_filt = OptionMenu(self.master, self.var_filt, *opt_filt)

        # size of the OptionMenus
        dd_opts.config(width=18)
        dd_wind.config(width=18)
        dd_nfft.config(width=18)
        dd_meth.config(width=18)
        dd_data.config(width=18)
        dd_filt.config(width=18)

        # positioning OptionMenus
        dd_opts.grid(column=1, row=0, sticky=tk.W)
        dd_wind.grid(column=1, row=1, sticky=tk.W)
        dd_nfft.grid(column=1, row=3, sticky=tk.W)
        dd_meth.grid(column=1, row=5, sticky=tk.W)
        dd_data.grid(column=1, row=6, sticky=tk.W)
        dd_filt.grid(column=3, row=4, sticky=tk.W)

    def showFormants(self):
        pass

    def plotFigure(self):
        pass
        #fig, self.ax = plt.subplots(figsize=(12,5))
        #self.ax.plot(self.audiotime, self.audio)