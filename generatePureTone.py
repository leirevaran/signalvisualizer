import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
from tkinter import ttk

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class PureTone(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.fig, self.ax = plt.subplots()
        self.cm = ControlMenu()
        self.toneMenu()

    def toneMenu(self):
        tm = tk.Toplevel()
        tm.resizable(True, True)
        tm.title('Generate pure tone')
        # tm.iconbitmap('icon.ico')
        tm.wm_transient(self) # Place the toplevel window at the top
        self.cm.windowGeometry(tm, 850, 475)

        # Adapt the window to different sizes
        for i in range(4):
            tm.columnconfigure(i, weight=1)

        for i in range(6):
            tm.rowconfigure(i, weight=1)

        # SCALES
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
        self.sca_freq = tk.Scale(tm, from_=0, to=48000/2, variable=tm.var_freq, length=500, orient='horizontal', tickinterval=10000, command=updateExpression)
        self.sca_phas = tk.Scale(tm, from_=-1, to=1, variable=tm.var_phas, length=500, orient='horizontal', tickinterval=1, command=updateExpression, resolution=0.01)
        
        self.sca_dura.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_offs.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_ampl.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_freq.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_phas.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        tm.var_fs = tk.IntVar(value=48000)
        vcmd = (tm.register(self.cm.onValidateFloat), '%s', '%S')
        vcfs = (tm.register(self.onValidateFs), '%S')

        self.ent_dura = ttk.Entry(tm, textvariable=tm.var_dura, validate='key', validatecommand=vcmd)
        self.ent_offs = ttk.Entry(tm, textvariable=tm.var_offs, validate='key', validatecommand=vcmd)
        self.ent_ampl = ttk.Entry(tm, textvariable=tm.var_ampl, validate='key', validatecommand=vcmd)
        self.ent_freq = ttk.Entry(tm, textvariable=tm.var_freq, validate='key', validatecommand=vcmd)
        self.ent_phas = ttk.Entry(tm, textvariable=tm.var_phas, validate='key', validatecommand=vcmd)
        self.ent_fs = ttk.Entry(tm, textvariable=tm.var_fs, validate='key', validatecommand=vcfs)

        def fsEntry(event):
            fs = int(self.ent_fs.get())
            if fs > 48000:
                tm.var_fs.set('48000')
                text = 'The sample frequency cannot be greater than 48000 Hz.'
                tk.messagebox.showerror(parent=tm, title='Wrong sample frequency value', message=text)
            else: return True

        self.ent_offs.bind('<Return>', updateExpression)
        self.ent_ampl.bind('<Return>', updateExpression)
        self.ent_freq.bind('<Return>', updateExpression)
        self.ent_phas.bind('<Return>', updateExpression)
        self.ent_fs.bind('<Return>', fsEntry)

        self.ent_dura.grid(column=4, row=0, sticky=tk.EW, padx=5, pady=5)
        self.ent_offs.grid(column=4, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_ampl.grid(column=4, row=2, sticky=tk.EW, padx=5, pady=5)
        self.ent_freq.grid(column=4, row=3, sticky=tk.EW, padx=5, pady=5)
        self.ent_phas.grid(column=4, row=4, sticky=tk.EW, padx=5, pady=5)
        self.ent_fs.grid(column=4, row=5, sticky=tk.EW, padx=5, pady=5)

        # LABELS
        sign = str(self.ent_offs.get()+' + '+str(self.ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(self.ent_freq.get())+'t + '+str(self.ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
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
        def checkValues():
            self.fs = int(self.ent_fs.get()) # sample frequency
            if fsEntry(self.fs) != True:
                return
            self.generatePureTone(tm, lab_sign)

        self.but_gene = ttk.Button(tm, text='Generate', command=lambda: checkValues())
        self.but_gene.grid(column=4, row=6, sticky=tk.EW, padx=5, pady=5)

    # Called when inserting something in the entry of fs. Only lets the user enter numbers.
    def onValidateFs(self, S):
        if S.isdigit():
            return True
        else: return False

    def generatePureTone(self, tm, lab_sign):
        amplitude = float(self.ent_ampl.get())
        frequency = float(self.ent_freq.get())
        phase = float(self.ent_phas.get())
        duration = float(self.ent_dura.get())
        offset = float(self.ent_offs.get())
        samples = int(duration*self.fs)

        # Update expression
        sign = str(self.ent_offs.get()+' + '+str(self.ent_ampl.get())+' COS(2'+unicodedata.lookup("GREEK SMALL LETTER PI")+' '+str(self.ent_freq.get())+'t + '+str(self.ent_phas.get())+unicodedata.lookup("GREEK SMALL LETTER PI")+')')
        lab_sign.configure(text=sign)

        # Check if the frequency is smaller than self.fs/2
        self.cm.bigFrequency(frequency, self.fs)

        time = np.linspace(start=0, stop=duration, num=samples, endpoint=False)
        ptone = amplitude * (np.cos(2*np.pi * frequency*time + phase*np.pi)) + offset

        self.fig, self.ax = self.cm.generateWindow(self, self.fig, self.ax, self.fs, time, ptone, tm, 'Pure tone')

        # Plot the pure tone
        limite = max(abs(ptone))*1.1
        self.ax.plot(time, ptone)
        self.fig.canvas.manager.set_window_title('Pure tone')
        self.ax.set(xlim=[0, duration], ylim=[-limite, limite], xlabel='Time (s)', ylabel='Amplitude')
        self.ax.axhline(y=0, color='black', linewidth='0.5', linestyle='--') # draw an horizontal line in y=0.0
        self.ax.axhline(y=1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=1.0
        self.ax.axhline(y=-1.0, color='red', linewidth='0.8', linestyle='--') # draw an horizontal line in y=-1.0
        self.ax.axhline(y=offset, color='blue', linewidth='1', label="offset") # draw an horizontal line in y=offset
        self.ax.legend(loc="upper right")

        plt.show()