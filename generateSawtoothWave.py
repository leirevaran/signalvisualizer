import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
from tkinter import ttk
from scipy import signal

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class SawtoothWave(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.cm = ControlMenu()
        self.fig, self.ax = plt.subplots()
        self.sawtoothMenu()

    def sawtoothMenu(self):
        stm = tk.Toplevel()
        stm.resizable(True, True)
        stm.title('Generate sawtooth wave')
        # tm.iconbitmap('icon.ico')
        stm.wm_transient(self) # Place the toplevel window at the top
        self.cm.windowGeometry(stm, 850, 475)

        # Adapt the window to different sizes
        for i in range(4):
            stm.columnconfigure(i, weight=1)

        for i in range(7):
            stm.rowconfigure(i, weight=1)

        # SCALES
        stm.var_dura = tk.IntVar(value=1)
        stm.var_offs = tk.DoubleVar(value=0)
        stm.var_ampl = tk.DoubleVar(value=0.5)
        stm.var_freq = tk.IntVar(value=2)
        stm.var_phas = tk.DoubleVar(value=0)
        stm.var_maxp = tk.DoubleVar(value=1)

        self.sca_dura = tk.Scale(stm, from_=0.01, to=30, variable=stm.var_dura, length=500, orient='horizontal', resolution=0.01)
        self.sca_offs = tk.Scale(stm, from_=-1, to=1, variable=stm.var_offs, length=500, orient='horizontal', resolution=0.01)
        self.sca_ampl = tk.Scale(stm, from_=0, to=1, variable=stm.var_ampl, length=500, orient='horizontal', resolution=0.01)
        self.sca_freq = tk.Scale(stm, from_=0, to=48000/2, variable=stm.var_freq, length=500, orient='horizontal')
        self.sca_phas = tk.Scale(stm, from_=-1, to=1, variable=stm.var_phas, length=500, orient='horizontal', resolution=0.01)
        self.sca_maxp = tk.Scale(stm, from_=0, to=1, variable=stm.var_maxp, length=500, orient='horizontal', resolution=0.01)
        
        self.sca_dura.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_offs.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_ampl.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_freq.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_phas.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_maxp.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        
        # ENTRYS
        stm.var_fs = tk.IntVar(value=48000)
        vcmd = (stm.register(self.cm.onValidateFloat), '%s', '%S')
        vcfs = (stm.register(self.onValidateFs), '%S')

        self.ent_dura = ttk.Entry(stm, textvariable=stm.var_dura, validate='key', validatecommand=vcmd)
        self.ent_offs = ttk.Entry(stm, textvariable=stm.var_offs, validate='key', validatecommand=vcmd)
        self.ent_ampl = ttk.Entry(stm, textvariable=stm.var_ampl, validate='key', validatecommand=vcmd)
        self.ent_freq = ttk.Entry(stm, textvariable=stm.var_freq, validate='key', validatecommand=vcmd)
        self.ent_phas = ttk.Entry(stm, textvariable=stm.var_phas, validate='key', validatecommand=vcmd)
        self.ent_maxp = ttk.Entry(stm, textvariable=stm.var_maxp, validate='key', validatecommand=vcmd)
        self.ent_fs = ttk.Entry(stm, textvariable=stm.var_fs, validate='key', validatecommand=vcfs)

        def fsEntry(event):
            fs = int(self.ent_fs.get())
            if fs > 48000:
                stm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=stm, title='Wrong sample frequency value', message=text)
            else: return True

        self.ent_fs.bind('<Return>', fsEntry)

        self.ent_dura.grid(column=4, row=0, sticky=tk.EW, padx=5, pady=5)
        self.ent_offs.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_ampl.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.ent_freq.grid(column=4, row=3, sticky=tk.EW, padx=5, pady=5)
        self.ent_phas.grid(column=4, row=4, sticky=tk.EW, padx=5, pady=5)
        self.ent_maxp.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)
        self.ent_fs.grid(column=4, row=6, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        lab_dura = ttk.Label(stm, text='Total duration (s)')
        lab_offs = ttk.Label(stm, text='Offset')
        lab_ampl = ttk.Label(stm, text='Amplitude')
        lab_freq = ttk.Label(stm, text='Frequency (Hz)')
        lab_phas = ttk.Label(stm, text='Phase ('+ unicodedata.lookup("GREEK SMALL LETTER PI") +' rad)')
        lab_maxp = ttk.Label(stm, text='Maximum position')
        lab_fs = ttk.Label(stm, text='Fs (Hz)')

        lab_dura.grid(column=0, row=0, sticky=tk.E)
        lab_offs.grid(column=0, row=1, sticky=tk.E)
        lab_ampl.grid(column=0, row=2, sticky=tk.E)
        lab_freq.grid(column=0, row=3, sticky=tk.E)
        lab_phas.grid(column=0, row=4, sticky=tk.E)
        lab_maxp.grid(column=0, row=5, sticky=tk.E)
        lab_fs.grid(column=3, row=6, sticky=tk.E)
        
        # BUTTONS
        def checkValues():
            self.fs = int(self.ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True:
                return
            self.generateSawtoothWave(stm)

        self.but_gene = ttk.Button(stm, text='Generate', command=lambda: checkValues())
        self.but_gene.grid(column=4, row=7, sticky=tk.EW, padx=5, pady=5)

        checkValues()

    # Called when inserting something in the entry of fs. Only lets the user enter numbers.
    def onValidateFs(self, S):
        if S.isdigit():
            return True
        else: return False

    def generateSawtoothWave(self, stm):
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        phase = float(self.ent_phas.get())
        maxpos = float(self.ent_maxp.get())
        duration = float(self.ent_dura.get())
        offset = float(self.ent_offs.get())
        samples = int(duration*self.fs)

        # Check if the frequency is smaller than self.fs/2
        self.cm.bigFrequency(frequency, self.fs)

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        sawtooth = amplitude * signal.sawtooth(2*np.pi*frequency*time + phase*np.pi, width=maxpos) + offset * np.ones(len(time))

        fig, ax = self.cm.generateWindow(self, self.fig, self.ax, self.fs, time, sawtooth, stm, 'Sawtooth wave')

        # Plot the pure tone
        limite = max(abs(sawtooth))*1.1
        ax.plot(time, sawtooth)
        fig.canvas.manager.set_window_title('Sawtooth signal')
        ax.set(xlim=[0, duration], ylim=[-limite, limite], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        ax.axhline(y=1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=1.0
        ax.axhline(y=-1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=-1.0
        ax.axhline(y=offset, color='blue', linewidth='1', label="offset") # draw an horizontal line in y=offset
        ax.legend(loc="upper right")

        plt.show()