import tkinter as tk
import colorednoise as cn
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk

from controlMenu import ControlMenu
from help import HelpMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Noise(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.cm = ControlMenu()
        self.fig, self.ax = plt.subplots()
        self.file = 'csv/generateNoise.csv'
        self.noiseMenu()

    def noiseMenu(self):
        nm = tk.Toplevel()
        nm.resizable(True, True)
        nm.title('Generate noise')
        # nm.iconbitmap('icon.ico')
        nm.wm_transient(self) # Place the toplevel window at the top
        self.cm.windowGeometry(nm, 850, 250)
        hm = HelpMenu()

        # Adapt the window to different sizes
        for i in range(4):
            nm.columnconfigure(i, weight=1)

        for i in range(4):
            nm.rowconfigure(i, weight=1)

        # Read the default values of the atributes from a csv file
        list = self.cm.readFromCsv(self.file)
        choice = list[0]
        amplitude = list[1]
        duration = list[2]
        self.fs = list[3]

        # SCALERS
        nm.var_ampl = tk.DoubleVar(value=amplitude)
        nm.var_dura = tk.DoubleVar(value=duration)
        self.sca_ampl = tk.Scale(nm, from_=0, to=1, variable=nm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, resolution=0.01)
        self.sca_dura = tk.Scale(nm, from_=0.01, to=30, variable=nm.var_dura, length=500, orient='horizontal', resolution=0.01)
        self.sca_ampl.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_dura.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        nm.var_fs = tk.IntVar(value=self.fs)
        vcmd = (nm.register(self.cm.onValidateFloat), '%s', '%S')
        vcfs = (nm.register(self.onValidateFs), '%S')
        
        self.ent_ampl = ttk.Entry(nm, textvariable=nm.var_ampl, validate='key', validatecommand=vcmd)
        self.ent_dura = ttk.Entry(nm, textvariable=nm.var_dura, validate='key', validatecommand=vcmd)
        self.ent_fs = ttk.Entry(nm, textvariable=nm.var_fs, validate='key', validatecommand=vcfs)
        
        def fsEntry(event):
            fs = int(self.ent_fs.get())
            if fs > 48000:
                nm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=nm, title='Wrong sample frequency value', message=text)
            else: return True

        self.ent_fs.bind('<Return>', fsEntry)
        
        self.ent_ampl.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_dura.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.ent_fs.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)
        
        # LABELS
        lab_type = ttk.Label(nm, text='Noise type')
        lab_ampl = ttk.Label(nm, text='Max. amplitude')
        lab_dura = ttk.Label(nm, text='Total duration (s)')
        lab_fs = ttk.Label(nm, text='Fs (Hz)')
        lab_type.grid(column=0, row=0, sticky=tk.E)
        lab_ampl.grid(column=0, row=1, sticky=tk.E)
        lab_dura.grid(column=0, row=2, sticky=tk.E)
        lab_fs.grid(column=0, row=4, sticky=tk.E)
        
        # BUTTONS
        def checkValues(but):
            self.fs = int(self.ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True:
                return
            if but == 1: self.generateNoise(nm)
            elif but == 2: self.saveDefaultValues(nm)

        self.but_gene = ttk.Button(nm, command=lambda: checkValues(1), text='Generate')
        self.but_save = ttk.Button(nm, command=lambda: checkValues(2), text='Save values as default')
        self.but_help = ttk.Button(nm, command=lambda: hm.createHelpMenu(self, 5), text='🛈', width=2)

        self.but_gene.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)
        self.but_save.grid(column=3, row=5, sticky=tk.EW, padx=5, pady=5)
        self.but_help.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)

        # OPTION MENUS
        nm.options = ('White noise','Pink noise', 'Brown noise')
        nm.var_opts = tk.StringVar()
        self.dd_opts = ttk.OptionMenu(nm, nm.var_opts, choice, *nm.options)
        self.dd_opts.config(width=11)
        self.dd_opts.grid(column=1, row=0, sticky=tk.W, padx=5)

        checkValues(1)

    # Called when inserting something in the entry of fs. Only lets the user enter numbers.
    def onValidateFs(self, S):
        if S.isdigit():
            return True
        else: return False

    def saveDefaultValues(self, nm):
        choice = nm.var_opts.get()
        amplitude = float(self.sca_ampl.get())
        duration = self.sca_dura.get()

        list = [choice, amplitude, duration, self.fs]
        self.cm.saveDefaultAsCsv(self.file, list)

    def generateNoise(self, nm):
        choice = nm.var_opts.get()
        amplitude = float(self.sca_ampl.get())
        duration = self.sca_dura.get()
        samples = int(duration*self.fs)

        if choice == 'White noise':
            beta = 0
        elif choice == 'Pink noise':
            beta = 1
        elif choice == 'Brown noise':
            beta = 2

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        noiseGaussian = cn.powerlaw_psd_gaussian(beta, samples)
        noise = amplitude * noiseGaussian / max(abs(noiseGaussian))

        # noisePower = noise*np.sqrt(power) # con control de potencia (power = amplitude)
        # # Para calcular la potencia
        # L2 = [x**2 for x in noise]
        # suma = sum(L2)/np.size(noise)

        fig, ax = self.cm.generateWindow(self, self.fig, self.ax, self.fs, time, noise, nm, choice)

        # Plot the noise
        ax.plot(time, noise)
        fig.canvas.manager.set_window_title(choice)
        ax.set(xlim=[0, duration], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0

        plt.show()