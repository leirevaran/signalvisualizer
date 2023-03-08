import tkinter as tk
import colorednoise as cn
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import SpanSelector

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Noise(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.noiseMenu()

    def noiseMenu(self):
        nm = tk.Toplevel()
        nm.geometry('815x200')
        nm.resizable(True, True)
        nm.title('Generate noise')
        nm.iconbitmap('icon.ico')
        nm.wm_transient(self) # Place the toplevel window at the top
        self.ax = plt.axes()
        self.fs = 48000 # sample frequency

        # SCALERS
        nm.var_ampl = tk.DoubleVar(value=1)
        nm.var_dura = tk.DoubleVar(value=1)
        self.sca_ampl = tk.Scale(nm, from_=0, to=1, variable=nm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, resolution=0.01)
        self.sca_dura = tk.Scale(nm, from_=0.01, to=30, variable=nm.var_dura, length=500, orient='horizontal', resolution=0.01)
        self.sca_ampl.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_dura.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        self.ent_ampl = ttk.Entry(nm, textvariable=nm.var_ampl, validate='key')
        self.ent_dura = ttk.Entry(nm, textvariable=nm.var_dura, validate='key')
        self.ent_ampl.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_dura.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        
        # LABELS
        lab_type = tk.Label(nm, text='Noise type')
        lab_ampl = tk.Label(nm, text='Max. amplitude')
        lab_dura = tk.Label(nm, text='Total duration (s)')
        lab_type.grid(column=0, row=0, sticky=tk.E)
        lab_ampl.grid(column=0, row=1, sticky=tk.E)
        lab_dura.grid(column=0, row=2, sticky=tk.E)
        
        # BUTTONS
        self.but_load = ttk.Button(nm, text='Load', command=lambda: self.loadNoise(), state='disabled')
        self.but_gene = ttk.Button(nm, text='Generate', command=lambda: self.generateNoise(nm))
        self.but_load.grid(column=3, row=4, sticky=tk.EW, padx=5)
        self.but_gene.grid(column=4, row=4, sticky=tk.EW, padx=5)

        # OPTION MENUS
        nm.options = ('White noise','Pink noise', 'Brown noise')
        nm.var_opts = tk.StringVar()
        self.dd_opts = ttk.OptionMenu(nm, nm.var_opts, nm.options[0], *nm.options)
        self.dd_opts.config(width=11)
        self.dd_opts.grid(column=1, row=0, sticky=tk.W, padx=5)

    def loadNoise(self):
        noisetime = np.arange(0, len(self.noise3)/self.fs, 1/self.fs)
        noiseDuration = max(noisetime)
        noiseLen = len(self.noise3)

        cm = ControlMenu()
        cm.createControlMenu(self, self.choice, self.fs, self.noise3, noisetime, noiseDuration, noiseLen)

    def generateNoise(self, nm):
        self.but_load.config(state='active')
        self.ax.clear()
        self.choice = nm.var_opts.get()
        amplitude = float(self.sca_ampl.get())
        duration = self.sca_dura.get()
        samples = int(duration*self.fs)

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)

        if self.choice == 'White noise':
            beta = 0
        elif self.choice == 'Pink noise':
            beta = 1
        elif self.choice == 'Brown noise':
            beta = 2

        noise = cn.powerlaw_psd_gaussian(beta, samples)
        # noise2 = noise*np.sqrt(power) # con control de potencia (power = amplitude)
        self.noise3 = amplitude * noise / max(abs(noise))

        # # para calcular la potencia
        # L2 = [x**2 for x in noise]
        # suma = sum(L2)/np.size(noise)

        def listenFragment(xmin, xmax):
            ini, end = np.searchsorted(time, (xmin, xmax))
            audio = self.noise3[ini:end+1]
            sd.play(audio, self.fs)

        plt.plot(time, self.noise3)
        self.ax = plt.gca() # gca = get current axes
        fig = plt.gcf() # gca = get current figure
        fig.canvas.manager.set_window_title(self.choice)
        plt.xlim(0, duration)
        plt.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title(str(self.choice))
        self.span = SpanSelector(self.ax, listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)
        plt.show()