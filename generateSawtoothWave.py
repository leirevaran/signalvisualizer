import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import unicodedata
from tkinter import ttk
from scipy import signal
from matplotlib.widgets import SpanSelector, Button, RadioButtons

from controlMenu import ControlMenu
from auxiliar import Auxiliar

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class SawtoothWave(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.cm = ControlMenu()
        self.aux = Auxiliar()
        self.fig, self.ax = plt.subplots()
        self.selectedAudio = np.empty(1)
        self.sawtoothMenu()

    def sawtoothMenu(self):
        stm = tk.Toplevel()
        stm.resizable(True, True)
        stm.title('Generate sawtooth wave')
        stm.iconbitmap('icons/icon.ico')
        stm.wm_transient(self) # Place the toplevel window at the top
        # self.cm.windowGeometry(stm, 850, 475)

        # Adapt the window to different sizes
        for i in range(4):
            stm.columnconfigure(i, weight=1)

        for i in range(7):
            stm.rowconfigure(i, weight=1)

        # If the 'generate' menu is closed, close also the generated figure
        def on_closing():
            stm.destroy()
            plt.close(self.fig)
        stm.protocol("WM_DELETE_WINDOW", on_closing)

        # Read the default values of the atributes from a csv file
        list = self.aux.readFromCsv()
        duration = list[3][2]
        amplitude = list[3][4]
        self.fs = list[3][6]
        offset = list[3][8]
        frequency = list[3][10]
        phase = list[3][12]
        maxpos = list[3][14]

        # SCALES
        stm.var_dura = tk.DoubleVar(value=duration)
        stm.var_offs = tk.DoubleVar(value=offset)
        stm.var_ampl = tk.DoubleVar(value=amplitude)
        stm.var_freq = tk.IntVar(value=frequency)
        stm.var_phas = tk.DoubleVar(value=phase)
        stm.var_maxp = tk.DoubleVar(value=maxpos)

        sca_dura = tk.Scale(stm, from_=0.01, to=30, variable=stm.var_dura, length=500, orient='horizontal', resolution=0.01)
        sca_offs = tk.Scale(stm, from_=-1, to=1, variable=stm.var_offs, length=500, orient='horizontal', resolution=0.01)
        sca_ampl = tk.Scale(stm, from_=0, to=1, variable=stm.var_ampl, length=500, orient='horizontal', resolution=0.01)
        sca_freq = tk.Scale(stm, from_=0, to=48000/2, variable=stm.var_freq, length=500, orient='horizontal')
        sca_phas = tk.Scale(stm, from_=-1, to=1, variable=stm.var_phas, length=500, orient='horizontal', resolution=0.01)
        sca_maxp = tk.Scale(stm, from_=0, to=1, variable=stm.var_maxp, length=500, orient='horizontal', resolution=0.01)
        
        sca_dura.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_offs.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_ampl.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_freq.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_phas.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_maxp.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        
        # ENTRYS
        stm.var_fs = tk.IntVar(value=self.fs)
        vcmd = (stm.register(self.aux.onValidate), '%S', '%s', '%d')
        vcfs = (stm.register(self.aux.onValidateInt), '%S')

        ent_dura = ttk.Entry(stm, textvariable=stm.var_dura, validate='key', validatecommand=vcmd)
        ent_offs = ttk.Entry(stm, textvariable=stm.var_offs, validate='key', validatecommand=vcmd)
        ent_ampl = ttk.Entry(stm, textvariable=stm.var_ampl, validate='key', validatecommand=vcmd)
        ent_freq = ttk.Entry(stm, textvariable=stm.var_freq, validate='key', validatecommand=vcmd)
        ent_phas = ttk.Entry(stm, textvariable=stm.var_phas, validate='key', validatecommand=vcmd)
        ent_maxp = ttk.Entry(stm, textvariable=stm.var_maxp, validate='key', validatecommand=vcmd)
        ent_fs = ttk.Entry(stm, textvariable=stm.var_fs, validate='key', validatecommand=vcfs)

        def fsEntry(event):
            fs = int(ent_fs.get())
            if fs > 48000:
                stm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=stm, title='Wrong sample frequency value', message=text)
            else: return True

        ent_fs.bind('<Return>', fsEntry)

        ent_dura.grid(column=4, row=0, sticky=tk.EW, padx=5, pady=5)
        ent_offs.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        ent_ampl.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_freq.grid(column=4, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_phas.grid(column=4, row=4, sticky=tk.EW, padx=5, pady=5)
        ent_maxp.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)
        ent_fs.grid(column=4, row=6, sticky=tk.EW, padx=5, pady=5)

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
        def checkValues(but):
            self.fs = int(ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True:
                return
            if but == 1: self.plotSawtoothWave(stm)
            elif but == 2: self.saveDefaultValues(stm, list)

        but_gene = ttk.Button(stm, command=lambda: checkValues(1), text='Generate')
        but_save = ttk.Button(stm, command=lambda: checkValues(2), text='Save values as default')
        but_help = ttk.Button(stm, command=lambda: self.controller.help.createHelpMenu(self, 4), text='🛈', width=2)

        but_gene.grid(column=4, row=7, sticky=tk.EW, padx=5, pady=5)
        but_save.grid(column=3, row=7, sticky=tk.EW, padx=5, pady=5)
        but_help.grid(column=0, row=7, sticky=tk.W, padx=5, pady=5)

        checkValues(1)

    def saveDefaultValues(self, stm, list):
        amplitude = stm.var_ampl.get()
        frequency = stm.var_freq.get()
        phase = stm.var_phas.get()
        maxpos = stm.var_maxp.get()
        duration = stm.var_dura.get()
        offset = stm.var_offs.get()

        new_list = [['NOISE','\t duration', list[0][2],'\t amplitude', list[0][4],'\t fs', list[0][6],'\t noise type', list[0][8]],
                ['PURE TONE','\t duration', list[1][2],'\t amplitude', list[1][4],'\t fs', list[1][6],'\t offset', list[1][8],'\t frequency', list[1][10],'\t phase',  list[1][12]],
                ['SQUARE WAVE','\t duration', list[2][2],'\t amplitude', list[2][4],'\t fs', list[2][6],'\t offset', list[2][8],'\t frequency', list[2][10],'\t phase', list[2][12],'\t active cycle', list[2][14]],
                ['SAWTOOTH WAVE','\t duration', duration,'\t amplitude', amplitude,'\t fs', self.fs,'\t offset', offset,'\t frequency', frequency,'\t phase', phase,'\t max position', maxpos],
                ['FREE ADD OF PT','\t duration', list[4][2],'\t octave', list[4][4],'\t freq1', list[4][6],'\t freq2', list[4][8],'\t freq3', list[4][10],'\t freq4', list[4][12],'\t freq5', list[4][14],'\t freq6', list[4][16],'\t amp1', list[4][18],'\t amp2', list[4][20],'\t amp3', list[4][22],'\t amp4', list[4][24],'\t amp5', list[4][26],'\t amp6', list[4][28]],
                ['SPECTROGRAM','\t colormap', list[5][2]]]
        self.aux.saveDefaultAsCsv(new_list)

    def plotSawtoothWave(self, stm):
        amplitude = stm.var_ampl.get()
        frequency = stm.var_freq.get()
        phase = stm.var_phas.get()
        maxpos = stm.var_maxp.get()
        duration = stm.var_dura.get()
        offset = stm.var_offs.get()
        samples = int(duration*self.fs)

        # Check if the frequency is smaller than self.fs/2
        self.aux.bigFrequency(frequency, self.fs)

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        sawtooth = amplitude * signal.sawtooth(2*np.pi*frequency*time + phase*np.pi, width=maxpos) + offset * np.ones(len(time))

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        fig, ax = self.fig, self.ax
        self.addLoadButton(fig, ax, self.fs, time, sawtooth, stm, 'Sawtooth wave')
        self.addScaleSaturateRadiobuttons(fig, offset)
        
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

    def addLoadButton(self, fig, ax, fs, time, audio, menu, name):
        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.selectedAudio.shape == (1,): 
                self.cm.createControlMenu(self, name, fs, audio)
            else:
                self.cm.createControlMenu(self, name, fs, self.selectedAudio)
            plt.close(fig)
            menu.destroy()
            axload._but_load = but_load # reference to the Button (otherwise the button does nothing)

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

    def addScaleSaturateRadiobuttons(self, fig, offset):
        if offset > 0.5 or offset < -0.5:
            def exceed(label):
                options = {'scale': 0, 'saturate': 1}
                option = options[label]
                if option == 0:
                    for i in range(len(self.selectedAudio)):
                        if self.selectedAudio[i] > 1:
                            self.selectedAudio[i] = 1
                        elif self.selectedAudio[i] < -1:
                            self.selectedAudio[i] = -1
                elif option == 1:
                    if max(self.selectedAudio) > 1:
                        self.selectedAudio = self.selectedAudio/max(abs(self.selectedAudio))
                    elif min(self.selectedAudio) < -1:
                        self.selectedAudio = self.selectedAudio/min(abs(self.selectedAudio))
                rax._radio = radio # reference to the Button (otherwise the button does nothing)

            rax = fig.add_axes([0.75, 0.9, 0.15, 0.1]) # [left, bottom, width, height]
            radio = RadioButtons(rax, ('scale', 'saturate'))
            radio.on_clicked(exceed)