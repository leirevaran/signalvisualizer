import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import unicodedata
from tkinter import ttk
from matplotlib.widgets import SpanSelector, Button, RadioButtons

from auxiliar import Auxiliar
from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class PureTone(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.aux = Auxiliar()
        self.cm = ControlMenu()
        self.fig, self.ax = plt.subplots()
        self.selectedAudio = np.empty(1)
        self.toneMenu()

    def toneMenu(self):
        tm = tk.Toplevel()
        tm.resizable(True, True)
        tm.title('Generate pure tone')
        tm.iconbitmap('icons/icon.ico')
        tm.lift() # Place the toplevel window at the top
        # self.aux.windowGeometry(tm, 850, 475)

        # Adapt the window to different sizes
        for i in range(4):
            tm.columnconfigure(i, weight=1)

        for i in range(6):
            tm.rowconfigure(i, weight=1)

        # If the 'generate' menu is closed, close also the generated figure
        def on_closing():
            tm.destroy()
            plt.close(self.fig)
        tm.protocol("WM_DELETE_WINDOW", on_closing)

        # Read the default values of the atributes from a csv file
        list = self.aux.readFromCsv()
        duration = list[1][2]
        amplitude = list[1][4]
        self.fs = list[1][6]
        offset = list[1][8]
        frequency = list[1][10]
        phase = list[1][12]

        # SCALES
        tm.var_dura = tk.DoubleVar(value=duration)
        tm.var_offs = tk.DoubleVar(value=offset)
        tm.var_ampl = tk.DoubleVar(value=amplitude)
        tm.var_freq = tk.IntVar(value=frequency)
        tm.var_phas = tk.DoubleVar(value=phase)

        def updateExpression(event):
            sign = str(ent_offs.get()+' + '+str(ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(ent_freq.get())+'t + '+str(ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
            lab_sign.configure(text=sign)

        sca_dura = tk.Scale(tm, from_=0.01, to=30, variable=tm.var_dura, length=500, orient='horizontal', resolution=0.01)
        sca_offs = tk.Scale(tm, from_=-1, to=1, variable=tm.var_offs, length=500, orient='horizontal', tickinterval=1, command=updateExpression, resolution=0.01)
        sca_ampl = tk.Scale(tm, from_=0, to=1, variable=tm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, command=updateExpression, resolution=0.01)
        sca_freq = tk.Scale(tm, from_=0, to=48000/2, variable=tm.var_freq, length=500, orient='horizontal', tickinterval=10000, command=updateExpression)
        sca_phas = tk.Scale(tm, from_=-1, to=1, variable=tm.var_phas, length=500, orient='horizontal', tickinterval=1, command=updateExpression, resolution=0.01)
        
        sca_dura.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_offs.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_ampl.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_freq.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        sca_phas.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        tm.var_fs = tk.IntVar(value=self.fs)
        vcmd = (tm.register(self.aux.onValidate), '%S', '%s', '%d')
        vcfs = (tm.register(self.aux.onValidateInt), '%S')

        ent_dura = ttk.Entry(tm, textvariable=tm.var_dura, validate='key', validatecommand=vcmd)
        ent_offs = ttk.Entry(tm, textvariable=tm.var_offs, validate='key', validatecommand=vcmd)
        ent_ampl = ttk.Entry(tm, textvariable=tm.var_ampl, validate='key', validatecommand=vcmd)
        ent_freq = ttk.Entry(tm, textvariable=tm.var_freq, validate='key', validatecommand=vcmd)
        ent_phas = ttk.Entry(tm, textvariable=tm.var_phas, validate='key', validatecommand=vcmd)
        ent_fs = ttk.Entry(tm, textvariable=tm.var_fs, validate='key', validatecommand=vcfs)

        def fsEntry(event):
            fs = int(ent_fs.get())
            if fs > 48000:
                tm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=tm, title='Wrong sample frequency value', message=text)
            else: return True

        ent_offs.bind('<Return>', updateExpression)
        ent_ampl.bind('<Return>', updateExpression)
        ent_freq.bind('<Return>', updateExpression)
        ent_phas.bind('<Return>', updateExpression)
        ent_fs.bind('<Return>', fsEntry)

        ent_dura.grid(column=4, row=0, sticky=tk.EW, padx=5, pady=5)
        ent_offs.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        ent_ampl.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_freq.grid(column=4, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_phas.grid(column=4, row=4, sticky=tk.EW, padx=5, pady=5)
        ent_fs.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        sign = str(ent_offs.get()+' + '+str(ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(ent_freq.get())+'t + '+str(ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
        lab_dura = ttk.Label(tm, text='Total duration (s)')
        lab_offs = ttk.Label(tm, text='Offset')
        lab_ampl = ttk.Label(tm, text='Amplitude')
        lab_freq = ttk.Label(tm, text='Frequency (Hz)')
        lab_phas = ttk.Label(tm, text='Phase ('+ unicodedata.lookup("GREEK SMALL LETTER PI") +' rad)')
        lab_expr = ttk.Label(tm, text='Expression')
        lab_sign = ttk.Label(tm, text=sign, font=('TkDefaultFont', 12))
        lab_fs = ttk.Label(tm, text='Fs (Hz)')

        lab_dura.grid(column=0, row=0, sticky=tk.E)
        lab_offs.grid(column=0, row=1, sticky=tk.E)
        lab_ampl.grid(column=0, row=2, sticky=tk.E)
        lab_freq.grid(column=0, row=3, sticky=tk.E)
        lab_phas.grid(column=0, row=4, sticky=tk.E)
        lab_expr.grid(column=0, row=5, sticky=tk.E, rowspan=2)
        lab_sign.grid(column=1, row=5, rowspan=2, columnspan=3)
        lab_fs.grid(column=3, row=5, sticky=tk.E)
        
        # BUTTONS
        def checkValues(but):
            self.fs = int(ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True:
                return
            if but == 1: self.plotPureTone(tm, lab_sign, ent_ampl, ent_freq, ent_phas, ent_offs)
            elif but == 2: self.saveDefaultValues(tm, list)

        but_gene = ttk.Button(tm, command=lambda: checkValues(1), text='Generate')
        but_save = ttk.Button(tm, command=lambda: checkValues(2), text='Save values as default')
        but_help = ttk.Button(tm, command=lambda: self.controller.help.createHelpMenu(self, 1), text='🛈', width=2)

        but_gene.grid(column=4, row=7, sticky=tk.EW, padx=5, pady=5)
        but_save.grid(column=4, row=6, sticky=tk.EW, padx=5, pady=5)
        but_help.grid(column=3, row=7, sticky=tk.E, padx=5, pady=5)

        checkValues(1)

    def saveDefaultValues(self, tm, list):
        amplitude = tm.var_ampl.get()
        frequency = tm.var_freq.get()
        phase = tm.var_phas.get()
        duration = tm.var_dura.get()
        offset = tm.var_offs.get()

        new_list = [['NOISE','\t duration', list[0][2],'\t amplitude', list[0][4],'\t fs', list[0][6],'\t noise type', list[0][8]],
                ['PURE TONE','\t duration', duration,'\t amplitude', amplitude,'\t fs', self.fs,'\t offset', offset,'\t frequency', frequency,'\t phase',  phase],
                ['SQUARE WAVE','\t duration', list[2][2],'\t amplitude', list[2][4],'\t fs', list[2][6],'\t offset', list[2][8],'\t frequency', list[2][10],'\t phase', list[2][12],'\t active cycle', list[2][14]],
                ['SAWTOOTH WAVE','\t duration', list[3][2],'\t amplitude', list[3][4],'\t fs', list[3][6],'\t offset', list[3][8],'\t frequency', list[3][10],'\t phase', list[3][12],'\t max position', list[3][14]],
                ['FREE ADD OF PT','\t duration', list[4][2],'\t octave', list[4][4],'\t freq1', list[4][6],'\t freq2', list[4][8],'\t freq3', list[4][10],'\t freq4', list[4][12],'\t freq5', list[4][14],'\t freq6', list[4][16],'\t amp1', list[4][18],'\t amp2', list[4][20],'\t amp3', list[4][22],'\t amp4', list[4][24],'\t amp5', list[4][26],'\t amp6', list[4][28]],
                ['SPECTROGRAM','\t colormap', list[5][2]]]
        self.aux.saveDefaultAsCsv(new_list)

    def plotPureTone(self, tm, lab_sign, ent_ampl, ent_freq, ent_phas, ent_offs):
        amplitude = tm.var_ampl.get()
        frequency = tm.var_freq.get()
        phase = tm.var_phas.get()
        duration = tm.var_dura.get()
        offset = tm.var_offs.get()
        samples = int(duration*self.fs)

        # Update expression
        sign = str(ent_offs.get()+' + '+str(ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(ent_freq.get())+'t + '+str(ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
        lab_sign.configure(text=sign)

        # Check if the frequency is smaller than self.fs/2
        self.aux.bigFrequency(frequency, self.fs)

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        ptone = amplitude * (np.cos(2*np.pi * frequency*time + phase*np.pi)) + offset

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        fig, ax = self.fig, self.ax
        self.addLoadButton(fig, ax, self.fs, time, ptone, duration, tm, 'Pure tone')
        self.addScaleSaturateRadiobuttons(fig, offset)

        # Plot the pure tone
        limite = max(abs(ptone))*1.1
        ax.plot(time, ptone)
        fig.canvas.manager.set_window_title('Pure tone')
        ax.set(xlim=[0, duration], ylim=[-limite, limite], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        ax.axhline(y=1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=1.0
        ax.axhline(y=-1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=-1.0
        ax.axhline(y=offset, color='blue', linewidth='1', label="offset") # draw an horizontal line in y=offset
        ax.legend(loc="upper right")

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
                if option == 0: # scale
                    for i in range(len(self.selectedAudio)):
                        if self.selectedAudio[i] > 1:
                            self.selectedAudio[i] = 1
                        elif self.selectedAudio[i] < -1:
                            self.selectedAudio[i] = -1
                elif option == 1: # saturate
                    if max(self.selectedAudio) > 1:
                        self.selectedAudio = self.selectedAudio/max(abs(self.selectedAudio))
                    elif min(self.selectedAudio) < -1:
                        self.selectedAudio = self.selectedAudio/min(abs(self.selectedAudio))
                rax._radio = radio # reference to the Button (otherwise the button does nothing)

            rax = fig.add_axes([0.75, 0.9, 0.15, 0.1]) # [left, bottom, width, height]
            radio = RadioButtons(rax, ('scale', 'saturate'))
            radio.on_clicked(exceed)