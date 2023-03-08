import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
from tkinter import ttk
from scipy import signal

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class FreeAdditionPureTones(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.freeAddMenu()

    def freeAddMenu(self):
        fam = tk.Toplevel()
        fam.geometry('750x500')
        fam.resizable(True, True)
        fam.title('Free addition of pure tones')
        fam.iconbitmap('icon.ico')
        fam.wm_transient(self) # Place the toplevel window at the top
        self.ax = plt.axes()
        self.fs = 48000 # sample frequency

        # SCALERS
        fam.var_amp1 = tk.DoubleVar(value=0.5)
        fam.var_amp2 = tk.DoubleVar(value=0)
        fam.var_amp3 = tk.DoubleVar(value=0)
        fam.var_amp4 = tk.DoubleVar(value=0)
        fam.var_amp5 = tk.DoubleVar(value=0)
        fam.var_amp6 = tk.DoubleVar(value=0)
        fam.var_dura = tk.IntVar(value=1)

        self.sca_amp1 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp1, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp2 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp2, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp3 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp3, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp4 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp4, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp5 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp5, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp6 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp6, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_dura = tk.Scale(fam, from_=1, to=30, variable=fam.var_dura, length=500, orient='horizontal')
        
        self.sca_amp1.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp2.grid(column=2, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp3.grid(column=3, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp4.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp5.grid(column=5, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp6.grid(column=6, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_dura.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=5)

        # ENTRYS
        fam.var_frq1 = tk.DoubleVar(value=2)
        fam.var_frq2 = tk.DoubleVar(value=0)
        fam.var_frq3 = tk.DoubleVar(value=0)
        fam.var_frq4 = tk.DoubleVar(value=0)
        fam.var_frq5 = tk.DoubleVar(value=0)
        fam.var_frq6 = tk.DoubleVar(value=0)

        self.ent_frq1 = ttk.Entry(fam, textvariable=fam.var_frq1, validate='key', width=10)
        self.ent_frq2 = ttk.Entry(fam, textvariable=fam.var_frq2, validate='key', width=10)
        self.ent_frq3 = ttk.Entry(fam, textvariable=fam.var_frq3, validate='key', width=10)
        self.ent_frq4 = ttk.Entry(fam, textvariable=fam.var_frq4, validate='key', width=10)
        self.ent_frq5 = ttk.Entry(fam, textvariable=fam.var_frq5, validate='key', width=10)
        self.ent_frq6 = ttk.Entry(fam, textvariable=fam.var_frq6, validate='key', width=10)
        self.ent_dura = ttk.Entry(fam, textvariable=fam.var_dura, validate='key', width=10)

        self.ent_frq1.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq2.grid(column=2, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq3.grid(column=3, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq4.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq5.grid(column=5, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq6.grid(column=6, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_dura.grid(column=6, row=3, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        lab_ton1 = tk.Label(fam, text='1')
        lab_ton2 = tk.Label(fam, text='2')
        lab_ton3 = tk.Label(fam, text='3')
        lab_ton4 = tk.Label(fam, text='4')
        lab_ton5 = tk.Label(fam, text='5')
        lab_ton6 = tk.Label(fam, text='6')
        lab_freq = ttk.Label(fam, text='Frequency (Hz)')
        lab_ampl = tk.Label(fam, text='Amplitude')
        lab_dura = tk.Label(fam, text='Total duration (s)')
        lab_octv = tk.Label(fam, text='Octave')

        lab_ton1.grid(column=1, row=0, sticky=tk.EW)
        lab_ton2.grid(column=2, row=0, sticky=tk.EW)
        lab_ton3.grid(column=3, row=0, sticky=tk.EW)
        lab_ton4.grid(column=4, row=0, sticky=tk.EW)
        lab_ton5.grid(column=5, row=0, sticky=tk.EW)
        lab_ton6.grid(column=6, row=0, sticky=tk.EW)
        lab_freq.grid(column=0, row=1, sticky=tk.E)
        lab_ampl.grid(column=0, row=2, sticky=tk.E)
        lab_dura.grid(column=0, row=3, sticky=tk.E)
        lab_octv.grid(column=0, row=4, sticky=tk.E)
        
        # BUTTONS
        self.but_gene = ttk.Button(fam, text='Generate', command=lambda: self.generatePureTone())
        self.but_gene.grid(column=6, row=6, sticky=tk.EW, padx=5)

    def generatePureTone(self):
        self.ax.clear()
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        phase = float(self.ent_phas.get())
        duration = float(self.ent_dura.get())
        offset = float(self.ent_offs.get())

        time = np.linspace(start=0, stop=duration, num=self.fs, endpoint=False)
        sig = amplitude * (np.cos(2*np.pi * frequency*time + phase*np.pi)) + offset

        plt.plot(time, sig)
        self.ax = plt.gca() # gca = get current axes
        plt.xlim(0, duration)
        plt.ylim(min(sig), max(sig))
        plt.axhline(y=0, color='black', linewidth='1', linestyle='--') # draw an horizontal line in y=0.0
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('Generate pure tone')
        plt.show()