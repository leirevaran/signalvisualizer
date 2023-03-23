import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
import sounddevice as sd
from tkinter import ttk
from scipy import signal
from matplotlib.widgets import Button, SpanSelector, RadioButtons

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class SawtoothWave(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.fig, self.ax = plt.subplots()
        self.stwFrag = np.empty(1)
        self.cm = ControlMenu()
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

        # SCALERS
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

        # If the frequency is greater than or equal to fs/2, show a warning
        if frequency >= self.fs/2:
            tk.messagebox.showwarning(title="Big frequency", message="The frequency is greater than or equal to half the value of the sample frequency ("+str(self.fs/2)+" Hz).") # show warning

        self.time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        self.sawtooth = amplitude * signal.sawtooth(2*np.pi*frequency*self.time + phase*np.pi, width=maxpos) + offset * np.ones(len(self.time))

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.stwFrag.shape == (1,): 
                text = "First select a fragment with the left button of the cursor."
                tk.messagebox.showerror(parent=self, title="No fragment selected", message=text) # show error
                return
            if max(self.stwFrag) > 1 or min(self.stwFrag) < -1:
                text = "The amplitude is exceeding the limits y=1 or y=-1.\nDo you want to continue?"
                if tk.messagebox.askokcancel(title="Exceeding amplitude", message=text) == False:
                    return
            plt.close(self.fig)
            self.span.clear()
            stm.destroy()
            self.cm.createControlMenu(self, 'Sawtooth signal', self.fs, self.stwFrag)

        # Adds a 'Load' button to the figure
        axload = self.fig.add_axes([0.8, 0.01, 0.09, 0.05]) # left, bottom, width, height
        self.but_load = Button(axload, 'Load')
        self.but_load.on_clicked(load)

        # Add scale/saturate radio buttons
        def exceed(label):
            options = {'scale': 0, 'saturate': 1}
            option = options[label]
            if option == 0:
                for i in range(len(self.stwFrag)):
                    if self.stwFrag[i] > 1:
                        self.stwFrag[i] = 1
                    elif self.stwFrag[i] < -1:
                        self.stwFrag[i] = -1
            elif option == 1:
                if max(self.stwFrag) > 1:
                    self.stwFrag = self.stwFrag/max(abs(self.stwFrag))
                elif min(self.stwFrag) < -1:
                    self.stwFrag = self.stwFrag/min(abs(self.stwFrag))

        rax = self.fig.add_axes([0.75, 0.9, 0.15, 0.1])
        radio = RadioButtons(rax, ('scale', 'saturate'))
        radio.on_clicked(exceed)
        
        # Plot the pure tone
        limite = max(abs(self.sawtooth))*1.1
        self.ax.clear()
        self.ax.plot(self.time, self.sawtooth)
        self.fig.canvas.manager.set_window_title('Sawtooth signal')
        self.ax.set(xlim=[0, duration], ylim=[-limite, limite], xlabel='Time (s)', ylabel='Amplitude')
        self.ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        self.ax.axhline(y=1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=1.0
        self.ax.axhline(y=-1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=-1.0
        self.ax.axhline(y=offset, color='blue', linewidth='1', label="offset") # draw an horizontal line in y=offset
        self.ax.legend(loc="upper right")

        self.span = SpanSelector(self.ax, self.listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)
        
        plt.show()

    def listenFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.time, (xmin, xmax))
        self.stwFrag = self.sawtooth[ini:end+1]
        sd.play(self.stwFrag, self.fs)