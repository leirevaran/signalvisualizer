import tkinter as tk
import colorednoise as cn
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import SpanSelector, Button

from auxiliar import Auxiliar
from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Noise(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.aux = Auxiliar()
        self.cm = ControlMenu()
        self.fig, self.ax = plt.subplots()
        self.selectedAudio = np.empty(1)
        self.noiseMenu()

    def noiseMenu(self):
        nm = tk.Toplevel()
        nm.resizable(True, True)
        nm.title('Generate noise')
        nm.iconbitmap('icons/icon.ico')
        nm.lift() # Place the toplevel window at the top
        # self.aux.windowGeometry(nm, 850, 250)

        # Adapt the window to different sizes
        for i in range(4):
            nm.columnconfigure(i, weight=1)

        for i in range(4):
            nm.rowconfigure(i, weight=1)

        # If the 'generate' menu is closed, close also the generated figure
        def on_closing():
            nm.destroy()
            plt.close(self.fig)
        nm.protocol("WM_DELETE_WINDOW", on_closing)

        # Read the default values of the atributes from a csv file
        list = self.aux.readFromCsv()
        duration = list[0][2]
        amplitude = list[0][4]
        self.fs = list[0][6]
        choice = list[0][8]

        # SCALERS
        nm.var_ampl = tk.DoubleVar(value=amplitude)
        nm.var_dura = tk.DoubleVar(value=duration)
        sca_ampl = tk.Scale(nm, from_=0, to=1, variable=nm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, resolution=0.01)
        sca_dura = tk.Scale(nm, from_=0.01, to=30, variable=nm.var_dura, length=500, orient='horizontal', resolution=0.01)
        sca_ampl.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_dura.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        nm.var_fs = tk.IntVar(value=self.fs)
        vcmd = (nm.register(self.aux.onValidate), '%S', '%s', '%d')
        vcfs = (nm.register(self.aux.onValidateInt), '%S')
        
        ent_ampl = ttk.Entry(nm, textvariable=nm.var_ampl, validate='key', validatecommand=vcmd)
        ent_dura = ttk.Entry(nm, textvariable=nm.var_dura, validate='key', validatecommand=vcmd)
        ent_fs = ttk.Entry(nm, textvariable=nm.var_fs, validate='key', validatecommand=vcfs)
        
        def fsEntry(event):
            fs = int(ent_fs.get())
            if fs > 48000:
                nm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=nm, title='Wrong sample frequency value', message=text)
            else: return True

        ent_fs.bind('<Return>', fsEntry)
        
        ent_ampl.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        ent_dura.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_fs.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)
        
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
            self.fs = int(ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True:
                return
            if but == 1: self.plotNoise(nm)
            elif but == 2: self.saveDefaultValues(nm, list)

        but_gene = ttk.Button(nm, command=lambda: checkValues(1), text='Generate')
        but_save = ttk.Button(nm, command=lambda: checkValues(2), text='Save values as default')
        but_help = ttk.Button(nm, command=lambda: self.controller.help.createHelpMenu(5), text='🛈', width=2)

        but_gene.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)
        but_save.grid(column=3, row=5, sticky=tk.EW, padx=5, pady=5)
        but_help.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)

        # OPTION MENUS
        nm.options = ('White noise','Pink noise', 'Brown noise')
        nm.var_opts = tk.StringVar()
        dd_opts = ttk.OptionMenu(nm, nm.var_opts, choice, *nm.options)
        dd_opts.config(width=11)
        dd_opts.grid(column=1, row=0, sticky=tk.W, padx=5)

        checkValues(1)

    def saveDefaultValues(self, nm, list):
        choice = nm.var_opts.get()
        amplitude = nm.var_ampl.get()
        duration = nm.var_dura.get()

        new_list = [['NOISE','\t duration', duration,'\t amplitude', amplitude,'\t fs', self.fs,'\t noise type', choice],
                ['PURE TONE','\t duration', list[1][2],'\t amplitude', list[1][4],'\t fs', list[1][6],'\t offset', list[1][8],'\t frequency', list[1][10],'\t phase',  list[1][12]],
                ['SQUARE WAVE','\t duration', list[2][2],'\t amplitude', list[2][4],'\t fs', list[2][6],'\t offset', list[2][8],'\t frequency', list[2][10],'\t phase', list[2][12],'\t active cycle', list[2][14]],
                ['SAWTOOTH WAVE','\t duration', list[3][2],'\t amplitude', list[3][4],'\t fs', list[3][6],'\t offset', list[3][8],'\t frequency', list[3][10],'\t phase', list[3][12],'\t max position', list[3][14]],
                ['FREE ADD OF PT','\t duration', list[4][2],'\t octave', list[4][4],'\t freq1', list[4][6],'\t freq2', list[4][8],'\t freq3', list[4][10],'\t freq4', list[4][12],'\t freq5', list[4][14],'\t freq6', list[4][16],'\t amp1', list[4][18],'\t amp2', list[4][20],'\t amp3', list[4][22],'\t amp4', list[4][24],'\t amp5', list[4][26],'\t amp6', list[4][28]],
                ['SPECTROGRAM','\t colormap', list[5][2]]]
        self.aux.saveDefaultAsCsv(new_list)

    def plotNoise(self, nm):
        choice = nm.var_opts.get()
        amplitude = nm.var_ampl.get()
        duration = nm.var_dura.get()
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

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        fig, ax = self.fig, self.ax
        self.addLoadButton(fig, ax, self.fs, time, noise, duration, nm, choice)
        
        # Plot the noise
        ax.plot(time, noise)
        fig.canvas.manager.set_window_title(choice)
        ax.set(xlim=[0, duration], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0

        plt.show()

    def addLoadButton(self, fig, ax, fs, time, audio, duration, menu, name):
        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.selectedAudio.shape == (1,): 
                self.cm.createControlMenu(name, fs, audio, duration, self.controller)
            else:
                time = np.arange(0, len(self.selectedAudio)/fs, 1/fs) # time array of the audio
                durSelec = max(time) # duration of the selected fragment
                self.cm.createControlMenu(name, fs, self.selectedAudio, durSelec, self.controller)
            plt.close(fig)
            menu.destroy()

        # Adds a 'Load' button to the figure
        axload = fig.add_axes([0.8, 0.01, 0.09, 0.05]) # [left, bottom, width, height]
        but_load = Button(axload, 'Load')
        but_load.on_clicked(load)
        axload._but_load = but_load # reference to the Button (otherwise the button does nothing)

        def listenFrag(xmin, xmax):
            ini, end = np.searchsorted(time, (xmin, xmax))
            self.selectedAudio = audio[ini:end+1]
            sd.play(self.selectedAudio, fs)
            
        self.span = SpanSelector(ax, listenFrag, 'horizontal', useblit=True, interactive=True, drag_from_anywhere=True)
