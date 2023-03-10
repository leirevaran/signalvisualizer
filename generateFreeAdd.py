import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from tkinter import ttk
from matplotlib.widgets import Button, SpanSelector

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class FreeAdditionPureTones(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.ax = plt.axes()
        self.fs = 48000 # sample frequency
        self.faptFrag = np.empty(1)
        self.cm = ControlMenu()
        self.freeAddMenu()

    def freeAddMenu(self):
        fam = tk.Toplevel()
        fam.geometry('790x570')
        fam.resizable(True, True)
        fam.title('Free addition of pure tones')
        # fam.iconbitmap('icon.ico')
        fam.wm_transient(self) # Place the toplevel window at the top

        # SCALERS
        fam.var_amp1 = tk.DoubleVar(value=0.5)
        fam.var_amp2 = tk.DoubleVar(value=0)
        fam.var_amp3 = tk.DoubleVar(value=0)
        fam.var_amp4 = tk.DoubleVar(value=0)
        fam.var_amp5 = tk.DoubleVar(value=0)
        fam.var_amp6 = tk.DoubleVar(value=0)
        fam.var_dura = tk.IntVar(value=1)

        self.sca_amp1 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp1, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp2 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp2, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp3 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp3, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp4 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp4, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp5 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp5, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_amp6 = tk.Scale(fam, from_=0, to=1, variable=fam.var_amp6, length=300, orient='vertical', tickinterval=0.1, resolution=0.01)
        self.sca_dura = tk.Scale(fam, from_=1, to=30, variable=fam.var_dura, length=500, orient='horizontal')

        self.sca_amp1.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp2.grid(column=2, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp3.grid(column=3, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp4.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp5.grid(column=5, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp6.grid(column=6, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_dura.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=5)

        # ENTRY/SPINBOX
        fam.var_frq1 = tk.DoubleVar(value=2)
        fam.var_frq2 = tk.DoubleVar(value=0)
        fam.var_frq3 = tk.DoubleVar(value=0)
        fam.var_frq4 = tk.DoubleVar(value=0)
        fam.var_frq5 = tk.DoubleVar(value=0)
        fam.var_frq6 = tk.DoubleVar(value=0)
        fam.var_octv = tk.IntVar(value=1)

        self.ent_frq1 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq1, validate='key', width=10)
        self.ent_frq2 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq2, validate='key', width=10)
        self.ent_frq3 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq3, validate='key', width=10)
        self.ent_frq4 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq4, validate='key', width=10)
        self.ent_frq5 = ttk.Spinbox(fam, from_=0, to=24000, textvariable=fam.var_frq5, validate='key', width=10)
        self.ent_frq6 = ttk.Spinbox(fam, from_=0, to=24000, textvariable=fam.var_frq6, validate='key', width=10)
        self.ent_dura = ttk.Entry(fam, textvariable=fam.var_dura, validate='key', width=10)
        self.ent_octv = ttk.Spinbox(fam, from_=1, to=6, textvariable=fam.var_octv, validate='key', width=10, state='readonly')

        self.ent_frq1.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq2.grid(column=2, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq3.grid(column=3, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq4.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq5.grid(column=5, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_frq6.grid(column=6, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_dura.grid(column=6, row=3, sticky=tk.EW, padx=5, pady=5)
        self.ent_octv.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        lab_ton1 = tk.Label(fam, text='1')
        lab_ton2 = tk.Label(fam, text='2')
        lab_ton3 = tk.Label(fam, text='3')
        lab_ton4 = tk.Label(fam, text='4')
        lab_ton5 = tk.Label(fam, text='5')
        lab_ton6 = tk.Label(fam, text='6')
        lab_freq = tk.Label(fam, text='Frequency (Hz)')
        lab_ampl = tk.Label(fam, text='Amplitude')
        lab_dura = tk.Label(fam, text='Total duration (s)')
        lab_octv = tk.Label(fam, text='Octave')

        lab_ton1.grid(column=1, row=0, sticky=tk.EW)
        lab_ton2.grid(column=2, row=0, sticky=tk.EW)
        lab_ton3.grid(column=3, row=0, sticky=tk.EW)
        lab_ton4.grid(column=4, row=0, sticky=tk.EW)
        lab_ton5.grid(column=5, row=0, sticky=tk.EW)
        lab_ton6.grid(column=6, row=0, sticky=tk.EW)
        lab_freq.grid(column=0, row=1, sticky=tk.E)
        lab_ampl.grid(column=0, row=2, sticky=tk.E)
        lab_dura.grid(column=0, row=3, sticky=tk.E)
        lab_octv.grid(column=0, row=4, sticky=tk.E)
        
        # BUTTONS
        self.but_gene = ttk.Button(fam, text='Generate', command=lambda: self.generateFAPT())
        self.but_load = ttk.Button(fam, text='Load', command=lambda: self.load(fam), state='disabled')
        self.but_gene.grid(column=6, row=8, sticky=tk.EW, padx=5)
        self.but_load.grid(column=5, row=8, sticky=tk.EW, padx=5)

        # notes
        self.but_noteC = ttk.Button(fam, text='C', command=lambda: self.notesHarmonics(1))
        self.but_ntCDb = ttk.Button(fam, text='CDb', command=lambda: self.notesHarmonics(2))
        self.but_noteD = ttk.Button(fam, text='D', command=lambda: self.notesHarmonics(3))
        self.but_ntDEb = ttk.Button(fam, text='DEb', command=lambda: self.notesHarmonics(4))
        self.but_noteE = ttk.Button(fam, text='E', command=lambda: self.notesHarmonics(5))
        self.but_noteF = ttk.Button(fam, text='F', command=lambda: self.notesHarmonics(6))
        self.but_ntFGb = ttk.Button(fam, text='FGb', command=lambda: self.notesHarmonics(7))
        self.but_noteG = ttk.Button(fam, text='G', command=lambda: self.notesHarmonics(8))
        self.but_ntGAb = ttk.Button(fam, text='GAb', command=lambda: self.notesHarmonics(9))
        self.but_noteA = ttk.Button(fam, text='A', command=lambda: self.notesHarmonics(10))
        self.but_ntABb = ttk.Button(fam, text='ABb', command=lambda: self.notesHarmonics(11))
        self.but_noteB = ttk.Button(fam, text='B', command=lambda: self.notesHarmonics(12))

        self.but_noteC.grid(column=1, row=6, sticky=tk.EW, padx=5)
        self.but_ntCDb.grid(column=2, row=6, sticky=tk.EW, padx=5)
        self.but_noteD.grid(column=3, row=6, sticky=tk.EW, padx=5)
        self.but_ntDEb.grid(column=4, row=6, sticky=tk.EW, padx=5)
        self.but_noteE.grid(column=5, row=6, sticky=tk.EW, padx=5)
        self.but_noteF.grid(column=6, row=6, sticky=tk.EW, padx=5)
        self.but_ntFGb.grid(column=1, row=7, sticky=tk.EW, padx=5)
        self.but_noteG.grid(column=2, row=7, sticky=tk.EW, padx=5)
        self.but_ntGAb.grid(column=3, row=7, sticky=tk.EW, padx=5)
        self.but_noteA.grid(column=4, row=7, sticky=tk.EW, padx=5)
        self.but_ntABb.grid(column=5, row=7, sticky=tk.EW, padx=5)
        self.but_noteB.grid(column=6, row=7, sticky=tk.EW, padx=5)

    def generateFAPT(self):
        self.ax.clear()
        self.but_load.config(state='active')
        frq1 = float(self.ent_frq1.get())
        frq2 = float(self.ent_frq2.get())
        frq3 = float(self.ent_frq3.get())
        frq4 = float(self.ent_frq4.get())
        frq5 = float(self.ent_frq5.get())
        frq6 = float(self.ent_frq6.get())
        amp1 = self.sca_amp1.get()
        amp2 = self.sca_amp2.get()
        amp3 = self.sca_amp3.get()
        amp4 = self.sca_amp4.get()
        amp5 = self.sca_amp5.get()
        amp6 = self.sca_amp6.get()
        duration = float(self.ent_dura.get())
        samples = int(duration*self.fs)

        self.time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        fapt1 = amp1 * (np.sin(2*np.pi * frq1*self.time))
        fapt2 = amp2 * (np.sin(2*np.pi * frq2*self.time))
        fapt3 = amp3 * (np.sin(2*np.pi * frq3*self.time))
        fapt4 = amp4 * (np.sin(2*np.pi * frq4*self.time))
        fapt5 = amp5 * (np.sin(2*np.pi * frq5*self.time))
        fapt6 = amp6 * (np.sin(2*np.pi * frq6*self.time))
        self.fapt = fapt1+fapt2+fapt3+fapt4+fapt5+fapt6

        # Plot free addition of pure tones
        plt.plot(self.time, self.fapt)
        plt.grid() # add grid lines
        self.ax = plt.gca() # gca = get current axes
        self.fig = plt.gcf() # gca = get current figure
        self.fig.canvas.manager.set_window_title('Free addition of pure tones')
        plt.xlim(0, duration)
        limite = max(abs(self.fapt))*1.1
        plt.ylim(-limite, limite)
        plt.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('Generate free addition of pure tones')

        self.span = SpanSelector(self.ax, self.listenFragment, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='tab:blue'), interactive=True, drag_from_anywhere=True)
        
        plt.show()

    def listenFragment(self, xmin, xmax):
        ini, end = np.searchsorted(self.time, (xmin, xmax))
        self.faptFrag = self.fapt[ini:end+1]
        sd.play(self.faptFrag, self.fs)

    # Add a 'Load' button that takes the selected fragment and opens the control menu when clicked
    def load(self, fam):
        # if the window of the figure has been closed or no fragment has been selected, show error
        if plt.fignum_exists(self.fig.number): # if no fragment selected
            if self.faptFrag.shape == (1,): 
                text = "First select a fragment with the left button of the cursor."
                tk.messagebox.showerror(parent=self, title="No fragment selected", message=text) # show error
            else:
                plt.close(self.fig)
                self.span.clear()
                fam.destroy()
                self.cm.createControlMenu(self, 'Free addition of pure tones', self.fs, self.faptFrag)
        else: # if figure window closed
            text = "First generate a signal and select a fragment with the left button of the cursor."
            tk.messagebox.showerror(parent=self, title="No signal generated", message=text) # show error

    def notesHarmonics(self, note):
        # Calculate fundamental frequency of the note
        oct = float(self.ent_octv.get())
        fundfreq = 440*np.exp(((oct-4)+(note-10)/12)*np.log(2))

        # Configure the fundamental frequency in the slider
        self.ent_frq1.set(value=round(fundfreq,2))
        self.sca_amp1.set(value=1)

        # 2nd harmonic
        freq = fundfreq*2
        self.ent_frq2.set(value=round(freq,2))
        self.sca_amp2.set(value=0.83)

        # 3rd harmonic
        freq = fundfreq*3
        self.ent_frq3.set(value=round(freq,2))
        self.sca_amp3.set(value=0.67)

        # 4th harmonic
        freq = fundfreq*4
        self.ent_frq4.set(value=round(freq,2))
        self.sca_amp4.set(value=0.5)

        # 5th harmonic
        freq = fundfreq*5
        self.ent_frq5.set(value=round(freq,2))
        self.sca_amp5.set(value=0.33)

        # 6th harmonic
        freq = fundfreq*6
        self.ent_frq6.set(value=round(freq,2))
        self.sca_amp6.set(value=0.17)
