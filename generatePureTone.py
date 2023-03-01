import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
from tkinter import ttk
from scipy import signal

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class PureTone(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.toneMenu()

    def toneMenu(self):
        tm = tk.Toplevel()
        tm.geometry('815x425')
        tm.resizable(True, True)
        tm.title('Generate pure tone')
        tm.iconbitmap('images/icon.ico')
        tm.wm_transient(self) # Place the toplevel window at the top
        self.ax = plt.axes()
        self.fs = 48000 # sample frequency

        # SCALERS
        tm.var_dura = tk.IntVar(value=1)
        tm.var_offs = tk.DoubleVar(value=0)
        tm.var_ampl = tk.DoubleVar(value=0.5)
        tm.var_freq = tk.IntVar(value=2)
        tm.var_phas = tk.DoubleVar(value=0)

        def updateExpression(event):
            sign = str(self.ent_offs.get()+' + '+str(self.ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(self.ent_freq.get())+'t + '+str(self.ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
            lab_sign.configure(text=sign)

        self.sca_dura = tk.Scale(tm, from_=1, to=30, variable=tm.var_dura, length=500, orient='horizontal')
        self.sca_offs = tk.Scale(tm, from_=-2, to=2, variable=tm.var_offs, length=500, orient='horizontal', tickinterval=1, command=updateExpression, resolution=0.01)
        self.sca_ampl = tk.Scale(tm, from_=0, to=1, variable=tm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, command=updateExpression, resolution=0.01)
        self.sca_freq = tk.Scale(tm, from_=0, to=20000, variable=tm.var_freq, length=500, orient='horizontal', tickinterval=10000, command=updateExpression)
        self.sca_phas = tk.Scale(tm, from_=-1, to=1, variable=tm.var_phas, length=500, orient='horizontal', tickinterval=1, command=updateExpression, resolution=0.01)
        
        self.sca_dura.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_offs.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_ampl.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_freq.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_phas.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        self.ent_dura = ttk.Entry(tm, textvariable=tm.var_dura, validate='key')
        self.ent_offs = ttk.Entry(tm, textvariable=tm.var_offs, validate='key')
        self.ent_ampl = ttk.Entry(tm, textvariable=tm.var_ampl, validate='key')
        self.ent_freq = ttk.Entry(tm, textvariable=tm.var_freq, validate='key')
        self.ent_phas = ttk.Entry(tm, textvariable=tm.var_phas, validate='key')

        self.ent_offs.bind('<Return>', updateExpression)
        self.ent_ampl.bind('<Return>', updateExpression)
        self.ent_freq.bind('<Return>', updateExpression)
        self.ent_phas.bind('<Return>', updateExpression)

        self.ent_dura.grid(column=4, row=0, sticky=tk.EW, padx=5, pady=5)
        self.ent_offs.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_ampl.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.ent_freq.grid(column=4, row=3, sticky=tk.EW, padx=5, pady=5)
        self.ent_phas.grid(column=4, row=4, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        sign = str(self.ent_offs.get()+' + '+str(self.ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(self.ent_freq.get())+'t + '+str(self.ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
        lab_dura = tk.Label(tm, text='Total duration (s)')
        lab_offs = tk.Label(tm, text='Offset')
        lab_ampl = tk.Label(tm, text='Amplitude (dB)')
        lab_freq = tk.Label(tm, text='Frequency (Hz)')
        lab_phas = tk.Label(tm, text='Phase ('+ unicodedata.lookup("GREEK SMALL LETTER PI") +' rad)')
        lab_expr = tk.Label(tm, text='Expression')
        lab_sign = tk.Label(tm, text=sign, font=('TkDefaultFont', 12))

        lab_dura.grid(column=0, row=0, sticky=tk.E)
        lab_offs.grid(column=0, row=1, sticky=tk.E)
        lab_ampl.grid(column=0, row=2, sticky=tk.E)
        lab_freq.grid(column=0, row=3, sticky=tk.E)
        lab_phas.grid(column=0, row=4, sticky=tk.E)
        lab_expr.grid(column=0, row=5, sticky=tk.E)
        lab_sign.grid(column=1, row=5, sticky=tk.EW, columnspan=3)
        
        # BUTTONS
        self.but_gene = ttk.Button(tm, text='Generate', command=lambda: self.generatePureTone(lab_sign))
        self.but_gene.grid(column=4, row=5, sticky=tk.EW, padx=5)

    def generatePureTone(self, lab_sign):
        self.ax.clear()
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        phase = float(self.ent_phas.get())
        duration = float(self.ent_dura.get())
        offset = float(self.ent_offs.get())

        # update expression
        sign = str(self.ent_offs.get()+' + '+str(self.ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(self.ent_freq.get())+'t + '+str(self.ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
        lab_sign.configure(text=sign)

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