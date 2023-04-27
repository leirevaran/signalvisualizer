import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk

from controlMenu import ControlMenu
from help import HelpMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class FreeAdditionPureTones(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.fs = 48000 # sample frequency
        self.cm = ControlMenu()
        self.fig, self.ax = plt.subplots()
        self.file = 'csv/generateFreeAdd.csv'
        self.freeAddMenu()

    def freeAddMenu(self):
        fam = tk.Toplevel()
        fam.resizable(True, True)
        fam.title('Free addition of pure tones')
        # fam.iconbitmap('icon.ico')
        fam.wm_transient(self) # Place the toplevel window at the top
        self.cm.windowGeometry(fam, 800, 600)
        hm = HelpMenu()

        # Adapt the window to different sizes
        for i in range(6):
            fam.columnconfigure(i, weight=1)

        for i in range(4):
            fam.rowconfigure(i, weight=1)

        # Read the default values of the atributes from a csv file
        list = self.cm.readFromCsv(self.file)
        freq1 = list[0]
        freq2 = list[1]
        freq3 = list[2]
        freq4 = list[3]
        freq5 = list[4]
        freq6 = list[5]
        ampl1 = list[6]
        ampl2 = list[7]
        ampl3 = list[8]
        ampl4 = list[9]
        ampl5 = list[10]
        ampl6 = list[11]
        duration = list[12]
        octave = list[13]

        # SCALES
        fam.var_amp1 = tk.DoubleVar(value=ampl1)
        fam.var_amp2 = tk.DoubleVar(value=ampl2)
        fam.var_amp3 = tk.DoubleVar(value=ampl3)
        fam.var_amp4 = tk.DoubleVar(value=ampl4)
        fam.var_amp5 = tk.DoubleVar(value=ampl5)
        fam.var_amp6 = tk.DoubleVar(value=ampl6)
        fam.var_dura = tk.IntVar(value=duration)

        self.sca_amp1 = tk.Scale(fam, from_=1, to=0, variable=fam.var_amp1, length=300, orient='vertical', resolution=0.01)
        self.sca_amp2 = tk.Scale(fam, from_=1, to=0, variable=fam.var_amp2, length=300, orient='vertical', resolution=0.01)
        self.sca_amp3 = tk.Scale(fam, from_=1, to=0, variable=fam.var_amp3, length=300, orient='vertical', resolution=0.01)
        self.sca_amp4 = tk.Scale(fam, from_=1, to=0, variable=fam.var_amp4, length=300, orient='vertical', resolution=0.01)
        self.sca_amp5 = tk.Scale(fam, from_=1, to=0, variable=fam.var_amp5, length=300, orient='vertical', resolution=0.01)
        self.sca_amp6 = tk.Scale(fam, from_=1, to=0, variable=fam.var_amp6, length=300, orient='vertical', resolution=0.01)
        self.sca_dura = tk.Scale(fam, from_=1, to=30, variable=fam.var_dura, length=500, orient='horizontal')

        self.sca_amp1.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp2.grid(column=2, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp3.grid(column=3, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp4.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp5.grid(column=5, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_amp6.grid(column=6, row=2, sticky=tk.EW, padx=5, pady=5)
        self.sca_dura.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=5)

        # ENTRY/SPINBOX
        fam.var_frq1 = tk.DoubleVar(value=freq1)
        fam.var_frq2 = tk.DoubleVar(value=freq2)
        fam.var_frq3 = tk.DoubleVar(value=freq3)
        fam.var_frq4 = tk.DoubleVar(value=freq4)
        fam.var_frq5 = tk.DoubleVar(value=freq5)
        fam.var_frq6 = tk.DoubleVar(value=freq6)
        fam.var_octv = tk.IntVar(value=octave)

        vcmd = (fam.register(self.cm.onValidateFloat), '%s', '%S')

        self.ent_frq1 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq1, validate='key', width=10)
        self.ent_frq2 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq2, validate='key', width=10)
        self.ent_frq3 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq3, validate='key', width=10)
        self.ent_frq4 = ttk.Spinbox(fam, from_=0, to=20000, textvariable=fam.var_frq4, validate='key', width=10)
        self.ent_frq5 = ttk.Spinbox(fam, from_=0, to=24000, textvariable=fam.var_frq5, validate='key', width=10)
        self.ent_frq6 = ttk.Spinbox(fam, from_=0, to=24000, textvariable=fam.var_frq6, validate='key', width=10)
        self.ent_dura = ttk.Entry(fam, textvariable=fam.var_dura, validate='key', width=10, validatecommand=vcmd)
        self.ent_octv = ttk.Spinbox(fam, from_=1, to=6, textvariable=fam.var_octv, validate='key', width=10, state='readonly')
        self.ent_octv.config(state='disabled')

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
        self.but_gene = ttk.Button(fam, command=lambda: self.generateFAPT(fam), text='Generate')
        self.but_pian = ttk.Button(fam, command=lambda: self.pianoKeyboard(), text='Show piano')
        self.but_save = ttk.Button(fam, command=lambda: self.saveDefaultValues(), text='Save values as default')
        self.but_help = ttk.Button(fam, command=lambda: hm.createHelpMenu(self, 2), text='🛈', width=2)

        self.but_gene.grid(column=6, row=8, sticky=tk.EW, padx=5, pady=5)
        self.but_pian.grid(column=2, row=4, sticky=tk.EW, padx=5, pady=5)
        self.but_save.grid(column=6, row=7, sticky=tk.EW, padx=5, pady=5)
        self.but_help.grid(column=5, row=8, sticky=tk.E, padx=5, pady=5)

        self.generateFAPT(fam)

    def saveDefaultValues(self):
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
        oct = float(self.ent_octv.get())

        list = [frq1, frq2, frq3, frq4, frq5, frq6, amp1, amp2, amp3, amp4, amp5, amp6, duration, oct]
        self.cm.saveDefaultAsCsv(self.file, list)

    def generateFAPT(self, fam):
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

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        fapt1 = amp1 * (np.sin(2*np.pi * frq1*time))
        fapt2 = amp2 * (np.sin(2*np.pi * frq2*time))
        fapt3 = amp3 * (np.sin(2*np.pi * frq3*time))
        fapt4 = amp4 * (np.sin(2*np.pi * frq4*time))
        fapt5 = amp5 * (np.sin(2*np.pi * frq5*time))
        fapt6 = amp6 * (np.sin(2*np.pi * frq6*time))
        fapt = fapt1+fapt2+fapt3+fapt4+fapt5+fapt6

        fig, ax = self.cm.generateWindow(self, self.fig, self.ax, self.fs, time, fapt, fam, 'Free addition of pure tones')

        # Plot free addition of pure tones
        limite = max(abs(fapt))*1.1
        ax.plot(time, fapt)
        fig.canvas.manager.set_window_title('Free addition of pure tones')
        ax.set(xlim=[0, duration], ylim=[-limite, limite], xlabel='Time (s)', ylabel='Amplitude')
        ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        ax.grid() # add grid lines

        plt.show()

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

    def pianoKeyboard(self):
        self.piano = tk.Toplevel()
        self.piano.title("Piano")
        # self.piano.geometry('{}x200'.format(300))
        self.but_pian.configure(state='disabled')
        self.ent_octv.config(state='active')

        # If the piano window is closed, reactivate the "show piano" button
        def on_closing():
            self.piano.destroy()
            self.but_pian.configure(state='active')
            self.ent_octv.config(state='disabled')
        self.piano.protocol("WM_DELETE_WINDOW", on_closing)

        white_keys = 7
        black = [1, 1, 0, 1, 1, 1, 0]
        white_notes = [1, 3, 5, 6, 8, 10, 12]
        black_notes = [2, 4, 0, 7, 9, 11]

        for i in range(white_keys):
            btn_white = tk.Button(self.piano, bg='white', activebackground='gray87', command=lambda i=i: self.notesHarmonics(white_notes[i]))
            btn_white.grid(row=0, column=i*3, rowspan=2, columnspan=3, sticky='nsew')

        for i in range(white_keys - 1):
            if black[i]:
                btn_black = tk.Button(self.piano, bg='black', activebackground='gray12', command=lambda i=i: self.notesHarmonics(black_notes[i]))
                btn_black.grid(row=0, column=(i*3)+2, rowspan=1, columnspan=2, sticky='nsew')

        for i in range(white_keys*3):
            self.piano.columnconfigure(i, weight=1)

        for i in range(2):
            self.piano.rowconfigure(i, weight=1)

        # Position the piano window in the middle of the screen
        w = 300 # width for the Tk root
        h = 200 # height for the Tk root

        # get screen width and height
        ws = self.piano.winfo_screenwidth() # width of the screen
        hs = self.piano.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the self.piano window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        # set the dimensions of the screen and where it is placed
        self.piano.geometry('%dx%d+%d+%d' % (w, h, x, y))