import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import Button, SpanSelector

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class PureTone(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.ax = plt.axes()
        self.fs = 48000 # sample frequency
        self.ptFrag = np.empty(1)
        self.cm = ControlMenu()
        self.toneMenu()

    def toneMenu(self):
        tm = tk.Toplevel()
        tm.geometry('815x445')
        tm.resizable(True, True)
        tm.title('Generate pure tone')
        tm.iconbitmap('icon.ico')
        tm.wm_transient(self) # Place the toplevel window at the top

        # SCALERS
        tm.var_dura = tk.IntVar(value=1)
        tm.var_offs = tk.DoubleVar(value=0)
        tm.var_ampl = tk.DoubleVar(value=0.5)
        tm.var_freq = tk.IntVar(value=2)
        tm.var_phas = tk.DoubleVar(value=0)

        def updateExpression(event):
            sign = str(self.ent_offs.get()+' + '+str(self.ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(self.ent_freq.get())+'t + '+str(self.ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
            lab_sign.configure(text=sign)

        self.sca_dura = tk.Scale(tm, from_=0.01, to=30, variable=tm.var_dura, length=500, orient='horizontal', resolution=0.01)
        self.sca_offs = tk.Scale(tm, from_=-1, to=1, variable=tm.var_offs, length=500, orient='horizontal', tickinterval=1, command=updateExpression, resolution=0.01)
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
        lab_ampl = tk.Label(tm, text='Amplitude')
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
        self.but_load = ttk.Button(tm, text='Load', command=lambda: self.load(tm), state='disabled')
        self.but_gene.grid(column=4, row=6, sticky=tk.EW, padx=5)
        self.but_load.grid(column=4, row=5, sticky=tk.EW, padx=5)

    def generatePureTone(self, lab_sign):
        self.ax.clear()
        self.but_load.config(state='active')
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        phase = float(self.ent_phas.get())
        duration = float(self.ent_dura.get())
        offset = float(self.ent_offs.get())
        samples = int(duration*self.fs)

        # Update expression
        sign = str(self.ent_offs.get()+' + '+str(self.ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(self.ent_freq.get())+'t + '+str(self.ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
        lab_sign.configure(text=sign)

        self.time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        self.ptone = amplitude * (np.cos(2*np.pi * frequency*self.time + phase*np.pi)) + offset

        # Plot the pure tone
        plt.plot(self.time, self.ptone)
        plt.grid() # add grid lines
        self.ax = plt.gca() # gca = get current axes
        self.fig = plt.gcf() # gca = get current figure
        self.fig.canvas.manager.set_window_title('Pure tone')
        plt.xlim(0, duration)
        limite = max(abs(self.ptone))*1.1
        plt.ylim(-limite, limite)
        plt.axhline(y=1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=1.0
        plt.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        plt.axhline(y=-1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=-1.0
        plt.axhline(y=offset, color='blue', linewidth='1', label="offset") # draw an horizontal line in y=offset
        plt.legend(loc="upper right")
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('Generate pure tone')

        self.span = SpanSelector(self.ax, self.listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)
        
        plt.show()

    def listenFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.time, (xmin, xmax))
        self.ptFrag = self.ptone[ini:end+1]
        sd.play(self.ptFrag, self.fs)

    # Add a 'Load' button that takes the selected fragment and opens the control menu when clicked
    def load(self, tm):
        # if the window of the figure has been closed or no fragment has been selected, show error
        if plt.fignum_exists(self.fig.number): # if no fragment selected
            if self.faptFrag.shape == (1,): 
                text = "First select a fragment with the left button of the cursor."
                tk.messagebox.showerror(parent=self, title="No fragment selected", message=text) # show error
            else:
                plt.close(self.fig)
                self.span.clear()
                tm.destroy()
                self.cm.createControlMenu(self, 'Free addition of pure tones', self.fs, self.faptFrag)
        else: # if figure window closed
            text = "First generate a signal and select a fragment with the left button of the cursor."
            tk.messagebox.showerror(parent=self, title="No signal generated", message=text) # show error