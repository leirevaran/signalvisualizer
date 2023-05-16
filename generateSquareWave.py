import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
from tkinter import ttk
from scipy import signal

from controlMenu import ControlMenu
from help import HelpMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class SquareWave(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.cm = ControlMenu()
        self.fig, self.ax = plt.subplots()
        self.squareMenu()

    def squareMenu(self):
        sm = tk.Toplevel()
        sm.resizable(True, True)
        sm.title('Generate square wave')
        # tm.iconbitmap('icon.ico')
        sm.wm_transient(self) # Place the toplevel window at the top
        self.cm.windowGeometry(sm, 850, 500)
        hm = HelpMenu()

        # Adapt the window to different sizes
        for i in range(4):
            sm.columnconfigure(i, weight=1)

        for i in range(7):
            sm.rowconfigure(i, weight=1)

        # Read the default values of the atributes from a csv file
        list = self.cm.readFromCsv()
        duration = list[2][2]
        amplitude = list[2][4]
        self.fs = list[2][6]
        offset = list[2][8]
        frequency = list[2][10]
        phase = list[2][12]
        cycle = list[2][14]

        # SCALES
        sm.var_dura = tk.IntVar(value=duration)
        sm.var_offs = tk.DoubleVar(value=offset)
        sm.var_ampl = tk.DoubleVar(value=amplitude)
        sm.var_freq = tk.IntVar(value=frequency)
        sm.var_phas = tk.DoubleVar(value=phase)
        sm.var_cycl = tk.IntVar(value=cycle)

        self.sca_dura = tk.Scale(sm, from_=0.01, to=30, variable=sm.var_dura, length=500, orient='horizontal', resolution=0.01)
        self.sca_offs = tk.Scale(sm, from_=-1, to=1, variable=sm.var_offs, length=500, orient='horizontal', resolution=0.01)
        self.sca_ampl = tk.Scale(sm, from_=0, to=1, variable=sm.var_ampl, length=500, orient='horizontal', resolution=0.01)
        self.sca_freq = tk.Scale(sm, from_=0, to=48000/2, variable=sm.var_freq, length=500, orient='horizontal')
        self.sca_phas = tk.Scale(sm, from_=-1, to=1, variable=sm.var_phas, length=500, orient='horizontal', resolution=0.01)
        self.sca_cycl = tk.Scale(sm, from_=10, to=90, variable=sm.var_cycl, length=500, orient='horizontal')
        
        self.sca_dura.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_offs.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_ampl.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_freq.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_phas.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_cycl.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        sm.var_fs = tk.IntVar(value=self.fs)
        vcmd = (sm.register(self.cm.onValidate), '%S', '%s', '%d')
        vcfs = (sm.register(self.onValidateFs), '%S')

        self.ent_dura = ttk.Entry(sm, textvariable=sm.var_dura, validate='key', validatecommand=vcmd)
        self.ent_offs = ttk.Entry(sm, textvariable=sm.var_offs, validate='key', validatecommand=vcmd)
        self.ent_ampl = ttk.Entry(sm, textvariable=sm.var_ampl, validate='key', validatecommand=vcmd)
        self.ent_freq = ttk.Entry(sm, textvariable=sm.var_freq, validate='key', validatecommand=vcmd)
        self.ent_phas = ttk.Entry(sm, textvariable=sm.var_phas, validate='key', validatecommand=vcmd)
        self.ent_cycl = ttk.Entry(sm, textvariable=sm.var_cycl, validate='key', validatecommand=vcmd)
        self.ent_fs = ttk.Entry(sm, textvariable=sm.var_fs, validate='key', validatecommand=vcfs)

        def fsEntry(event):
            fs = int(self.ent_fs.get())
            if fs > 48000:
                sm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=sm, title='Wrong sample frequency value', message=text)
            else: return True

        self.ent_fs.bind('<Return>', fsEntry)

        self.ent_dura.grid(column=4, row=0, sticky=tk.EW, padx=5, pady=5)
        self.ent_offs.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_ampl.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.ent_freq.grid(column=4, row=3, sticky=tk.EW, padx=5, pady=5)
        self.ent_phas.grid(column=4, row=4, sticky=tk.EW, padx=5, pady=5)
        self.ent_cycl.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)
        self.ent_fs.grid(column=4, row=6, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        lab_dura = ttk.Label(sm, text='Total duration (s)')
        lab_offs = ttk.Label(sm, text='Offset')
        lab_ampl = ttk.Label(sm, text='Amplitude')
        lab_freq = ttk.Label(sm, text='Frequency (Hz)')
        lab_phas = ttk.Label(sm, text='Phase ('+ unicodedata.lookup("GREEK SMALL LETTER PI") +' rad)')
        lab_cycl = ttk.Label(sm, text='Active cycle (%)')
        lab_fs = ttk.Label(sm, text='Fs (Hz)')

        lab_dura.grid(column=0, row=0, sticky=tk.E)
        lab_offs.grid(column=0, row=1, sticky=tk.E)
        lab_ampl.grid(column=0, row=2, sticky=tk.E)
        lab_freq.grid(column=0, row=3, sticky=tk.E)
        lab_phas.grid(column=0, row=4, sticky=tk.E)
        lab_cycl.grid(column=0, row=5, sticky=tk.E)
        lab_fs.grid(column=3, row=6, sticky=tk.E)
        
        # BUTTONS
        def checkValues(but):
            self.fs = int(self.ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True:
                return
            if but == 1: self.generateSquareWave(sm)
            elif but == 2: self.saveDefaultValues(list)

        self.but_gene = ttk.Button(sm, command=lambda: checkValues(1), text='Generate')
        self.but_save = ttk.Button(sm, command=lambda: checkValues(2), text='Save values as default')
        self.but_help = ttk.Button(sm, command=lambda: hm.createHelpMenu(self, 3), text='🛈', width=2)

        self.but_gene.grid(column=4, row=7, sticky=tk.EW, padx=5, pady=5)
        self.but_save.grid(column=3, row=7, sticky=tk.EW, padx=5, pady=5)
        self.but_help.grid(column=0, row=7, sticky=tk.W, padx=5, pady=5)

        checkValues(1)

    # Called when inserting something in the entry of fs. Only lets the user enter numbers.
    def onValidateFs(self, S):
        if S.isdigit():
            return True
        return False

    def saveDefaultValues(self, list):
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        phase = float(self.ent_phas.get())
        cycle = float(self.ent_cycl.get())
        duration = float(self.ent_dura.get())
        offset = float(self.ent_offs.get())

        new_list = [['NOISE','\t duration', list[0][2],'\t amplitude', list[0][4],'\t fs', list[0][6],'\t noise type', list[0][8]],
                ['PURE TONE','\t duration', list[1][2],'\t amplitude', list[1][4],'\t fs', list[1][6],'\t offset', list[1][8],'\t frequency', list[1][10],'\t phase',  list[1][12]],
                ['SQUARE WAVE','\t duration', duration,'\t amplitude', amplitude,'\t fs', self.fs,'\t offset', offset,'\t frequency', frequency,'\t phase', phase,'\t active cycle', cycle],
                ['SAWTOOTH WAVE','\t duration', list[3][2],'\t amplitude', list[3][4],'\t fs', list[3][6],'\t offset', list[3][8],'\t frequency', list[3][10],'\t phase', list[3][12],'\t max position', list[3][14]],
                ['FREE ADD OF PT','\t duration', list[4][2],'\t octave', list[4][4],'\t freq1', list[4][6],'\t freq2', list[4][8],'\t freq3', list[4][10],'\t freq4', list[4][12],'\t freq5', list[4][14],'\t freq6', list[4][16],'\t amp1', list[4][18],'\t amp2', list[4][20],'\t amp3', list[4][22],'\t amp4', list[4][24],'\t amp5', list[4][26],'\t amp6', list[4][28]],
                ['SPECTROGRAM','\t colormap', list[5][2]]]
        self.cm.saveDefaultAsCsv(new_list)

    def generateSquareWave(self, sm):
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        phase = float(self.ent_phas.get())
        cycle = float(self.ent_cycl.get())
        duration = float(self.ent_dura.get())
        offset = float(self.ent_offs.get())
        samples = int(duration*self.fs)

        # Check if the frequency is smaller than self.fs/2
        self.cm.bigFrequency(frequency, self.fs)

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        square = amplitude * (signal.square(2*np.pi*frequency*time + phase*np.pi, duty=cycle/100) / 2) + offset * np.ones(len(time))

        fig, ax = self.cm.generateWindow(self, self.fig, self.ax, self.fs, time, square, sm, 'Square signal')
        
        # Plot the square wave
        limite = max(abs(square))*1.1
        ax.plot(time, square)
        fig.canvas.manager.set_window_title('Square wave')
        ax.set(xlim=[0, duration], ylim=[-limite, limite], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        ax.axhline(y=1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=1.0
        ax.axhline(y=-1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=-1.0
        ax.axhline(y=offset, color='blue', linewidth='1', label="offset") # draw an horizontal line in y=offset
        ax.legend(loc="upper right")

        plt.show()