import tkinter as tk
import colorednoise as cn
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk

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
        nm.iconbitmap('images/icon.ico')
        nm.wm_transient(self) # Place the toplevel window at the top
        self.ax = plt.axes()
        self.fs = 48000 # sample frequency

        # SCALERS
        nm.var_ampl = tk.DoubleVar(value=1)
        nm.var_dura = tk.DoubleVar(value=1)
        self.sca_ampl = tk.Scale(nm, from_=0, to=1, variable=nm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, resolution=0.01)
        self.sca_dura = tk.Scale(nm, from_=1, to=30, variable=nm.var_dura, length=500, orient='horizontal')
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
        self.but_load = ttk.Button(nm, text='Load', command=lambda: self.controller.initialize_frame('Load'))
        self.but_gene = ttk.Button(nm, text='Generate', command=lambda: self.generateNoise(nm))
        self.but_load.grid(column=3, row=4, sticky=tk.EW, padx=5)
        self.but_gene.grid(column=4, row=4, sticky=tk.EW, padx=5)

        # OPTION MENUS
        nm.options = ('White noise','Pink noise', 'Brown noise')
        nm.var_opts = tk.StringVar()
        self.dd_opts = ttk.OptionMenu(nm, nm.var_opts, nm.options[0], *nm.options)
        self.dd_opts.config(width=11)
        self.dd_opts.grid(column=1, row=0, sticky=tk.W, padx=5)

    # def newSample(self, nm):
    #     pass

    def generateNoise(self, nm):
        self.ax.clear()
        choice = nm.var_opts.get()
        amplitude = float(self.sca_ampl.get())
        duration = self.sca_dura.get()
        samples = duration*self.fs

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)

        if choice == 'White noise':
            beta = 0
        elif choice == 'Pink noise':
            beta = 1
        elif choice == 'Brown noise':
            beta = 2

        noise = cn.powerlaw_psd_gaussian(beta, samples)
        # noise2 = noise*np.sqrt(power) # con control de potencia (power = amplitude)
        noise3 = amplitude * noise / max(abs(noise))

        # # para calcular la potencia
        # L2 = [x**2 for x in noise]
        # suma = sum(L2)/np.size(noise)

        plt.plot(time, noise3)
        self.ax = plt.gca() # gca = get current axes
        plt.xlim(0, duration)
        plt.axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title(str(choice))
        plt.show()