import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import Button, SpanSelector, RadioButtons

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class RosenbergPulse(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.fig, self.ax = plt.subplots()
        self.rpFrag = np.empty(1)
        self.cm = ControlMenu()
        self.rosenbergMenu()

    def rosenbergMenu(self):
        rm = tk.Toplevel()
        rm.resizable(True, True)
        rm.title('Generate Rosenberg pulse')
        # tm.iconbitmap('icon.ico')
        rm.wm_transient(self) # Place the toplevel window at the top
        self.cm.windowGeometry(rm, 850, 475)

        # Adapt the window to different sizes
        for i in range(4):
            rm.columnconfigure(i, weight=1)

        for i in range(6):
            rm.rowconfigure(i, weight=1)

        # SCALES
        rm.var_dura = tk.IntVar(value=1)
        rm.var_ampl = tk.DoubleVar(value=0.5)
        rm.var_freq = tk.IntVar(value=1)
        rm.var_rist = tk.IntVar(value=30)
        rm.var_dect = tk.IntVar(value=50)

        self.sca_dura = tk.Scale(rm, from_=0.01, to=30, variable=rm.var_dura, length=500, orient='horizontal', resolution=0.01)
        self.sca_ampl = tk.Scale(rm, from_=0, to=1, variable=rm.var_ampl, length=500, orient='horizontal', resolution=0.01)
        self.sca_freq = tk.Scale(rm, from_=1, to=4800, variable=rm.var_freq, length=500, orient='horizontal')
        self.sca_rist = tk.Scale(rm, from_=10, to=90, variable=rm.var_rist, length=500, orient='horizontal')
        self.sca_dect = tk.Scale(rm, from_=10, to=90, variable=rm.var_dect, length=500, orient='horizontal')
        
        self.sca_dura.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_ampl.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_freq.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_rist.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_dect.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        
        # ENTRYS
        rm.var_fs = tk.IntVar(value=48000)
        vcfl = (rm.register(self.cm.onValidateFloat), '%s', '%S')
        vcin = (rm.register(self.cm.onValidateInt), '%S')

        self.ent_dura = ttk.Entry(rm, textvariable=rm.var_dura, validate='key', validatecommand=vcin)
        self.ent_ampl = ttk.Entry(rm, textvariable=rm.var_ampl, validate='key', validatecommand=vcfl)
        self.ent_freq = ttk.Entry(rm, textvariable=rm.var_freq, validate='key', validatecommand=vcin)
        self.ent_rist = ttk.Entry(rm, textvariable=rm.var_rist, validate='key', validatecommand=vcin)
        self.ent_dect = ttk.Entry(rm, textvariable=rm.var_dect, validate='key', validatecommand=vcin)
        self.ent_fs = ttk.Entry(rm, textvariable=rm.var_fs, validate='key', validatecommand=vcin)

        def timeEntry(event):
            risingTime = int(self.ent_rist.get())
            decreasingTime = int(self.ent_dect.get())
            if risingTime + decreasingTime > 100:
                rm.var_rist.set('30')
                rm.var_dect.set('50')
                text = 'Rising time + Decreasing time cannot be greater than 100.'
                tk.messagebox.showerror(parent=rm, title='Wrong combination of rising and decreasing time', message=text)
            else: return True
        
        def fsEntry(event):
            fs = int(self.ent_fs.get())
            if fs > 48000:
                rm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=rm, title='Wrong sample frequency value', message=text)
            else: return True

        self.ent_rist.bind('<Return>', timeEntry)
        self.ent_dect.bind('<Return>', timeEntry)
        self.ent_fs.bind('<Return>', fsEntry)

        self.ent_dura.grid(column=4, row=0, sticky=tk.EW, padx=5, pady=5)
        self.ent_ampl.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_freq.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.ent_rist.grid(column=4, row=3, sticky=tk.EW, padx=5, pady=5)
        self.ent_dect.grid(column=4, row=4, sticky=tk.EW, padx=5, pady=5)
        self.ent_fs.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        lab_dura = ttk.Label(rm, text='Total duration (s)')
        lab_ampl = ttk.Label(rm, text='Amplitude')
        lab_freq = ttk.Label(rm, text='Frequency (Hz)')
        lab_rist = ttk.Label(rm, text='Rising time (%)')
        lab_dect = ttk.Label(rm, text='Decreasing time (%)')
        lab_fs = ttk.Label(rm, text='Fs (Hz)')

        lab_dura.grid(column=0, row=0, sticky=tk.E)
        lab_ampl.grid(column=0, row=1, sticky=tk.E)
        lab_freq.grid(column=0, row=2, sticky=tk.E)
        lab_rist.grid(column=0, row=3, sticky=tk.E)
        lab_dect.grid(column=0, row=4, sticky=tk.E)
        lab_fs.grid(column=3, row=5, sticky=tk.E)
        
        # BUTTONS
        def checkValues():
            self.rist = int(self.ent_rist.get())
            self.dect = int(self.ent_dect.get())
            self.fs = int(self.ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True or timeEntry(self.rist) != True or timeEntry(self.dect) != True:
                return
            self.generateRosenbergPulse(rm)

        self.but_gene = ttk.Button(rm, text='Generate', command=lambda: checkValues())
        self.but_gene.grid(column=4, row=6, sticky=tk.EW, padx=5, pady=5)

    def generateRosenbergPulse(self, rm):
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        duration = float(self.ent_dura.get())
        samples = int(duration*self.fs)

        # If the frequency is greater than or equal to fs/2, show a warning
        if frequency >= self.fs/2:
            tk.messagebox.showwarning(title="Big frequency", message="The frequency is greater than or equal to half the value of the sample frequency ("+str(self.fs/2)+" Hz).") # show warning

        self.time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        self.rosenberg = amplitude * rosenberg(frequency, self.time, self.rist, self.dect, self.fs)

        # If the window has been closed, create it again
        if plt.fignum_exists(self.fig.number):
            self.ax.clear() # delete the previous plot
        else:
            self.fig, self.ax = plt.subplots() # create the window

        # Takes the selected fragment and opens the control menu when clicked
        def load(event):
            if self.rpFrag.shape == (1,): 
                text = "First select a fragment with the left button of the cursor."
                tk.messagebox.showerror(parent=self, title="No fragment selected", message=text) # show error
                return
            if max(self.rpFrag) > 1 or min(self.rpFrag) < -1:
                text = "The amplitude is exceeding the limits y=1 or y=-1.\nDo you want to continue?"
                if tk.messagebox.askokcancel(title="Exceeding amplitude", message=text) == False:
                    return
            plt.close(self.fig)
            self.span.clear()
            rm.destroy()
            self.cm.createControlMenu(self, 'Rosenberg pulse', self.fs, self.rpFrag)

        # Adds a 'Load' button to the figure
        axload = self.fig.add_axes([0.8, 0.01, 0.09, 0.05]) # left, bottom, width, height
        self.but_load = Button(axload, 'Load')
        self.but_load.on_clicked(load)

        # Plot the Rosenberg pulse
        limite = max(abs(self.rosenberg))*1.1
        self.ax.plot(self.time, self.rosenberg)
        self.fig.canvas.manager.set_window_title('Rosenberg pulse')
        self.ax.set(xlim=[0, duration], ylim=[-limite, limite], xlabel='Time (s)', ylabel='Amplitude')
        self.ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0

        self.span = SpanSelector(self.ax, self.listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)
        
        plt.show()

    def listenFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.time, (xmin, xmax))
        self.rpFrag = self.rosenberg[ini:end+1]
        sd.play(self.rpFrag, self.fs)