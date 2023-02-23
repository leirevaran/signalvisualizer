import tkinter as tk

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class PureTone(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.toneMenu()

    def toneMenu(self):
        tm = tk.Toplevel()
        tm.geometry('760x545')
        tm.resizable(True, True)
        tm.title('Generate pure tone')
        tm.iconbitmap('images/icon.ico')
        tm.wm_transient(self) # Place the toplevel window at the top

        # LABELS
        lab_ampl = tk.Label(tm, text='Amplitude (dB)')
        lab_freq = tk.Label(tm, text='Frequency (Hz)')
        lab_phas = tk.Label(tm, text='Phase (pi rad)')
        lab_dura = tk.Label(tm, text='Total duration (s)')
        lab_offs = tk.Label(tm, text='Offset')
        lab_expr = tk.Label(tm, text='Expression')

        lab_ampl.grid(column=0, row=0, sticky=tk.E)
        lab_freq.grid(column=0, row=1, sticky=tk.E)
        lab_phas.grid(column=0, row=2, sticky=tk.E)
        lab_dura.grid(column=0, row=3, sticky=tk.E)
        lab_offs.grid(column=0, row=4, sticky=tk.E)
        lab_expr.grid(column=0, row=5, sticky=tk.E)

        # SCALERS
        tm.var_ampl = tk.DoubleVar(value=0.5)
        tm.var_freq = tk.DoubleVar(value=2)
        tm.var_phas = tk.DoubleVar(value=0)
        tm.var_dura = tk.DoubleVar(value=1)
        tm.var_offs = tk.DoubleVar(value=0)

        self.sca_ampl = tk.Scale(tm, from_=0, to=1, variable=tm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, resolution=0.1)
        self.sca_freq = tk.Scale(tm, from_=0, to=20000, variable=tm.var_freq, length=500, orient='horizontal', tickinterval=10000)
        self.sca_phas = tk.Scale(tm, from_=-1, to=1, variable=tm.var_phas, length=500, orient='horizontal', tickinterval=1, resolution=0.1)
        self.sca_dura = tk.Scale(tm, from_=0, to=30, variable=tm.var_dura, length=500, orient='horizontal', tickinterval=5)
        self.sca_offs = tk.Scale(tm, from_=-2, to=2, variable=tm.var_offs, length=500, orient='horizontal', tickinterval=1, resolution=0.01)
        
        self.sca_ampl.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_freq.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_phas.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_dura.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_offs.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # ENTRYS
        cm.var_size = tk.DoubleVar(value=0.09)
        cm.var_over = tk.DoubleVar()
        cm.var_minf = tk.IntVar()
        cm.var_maxf = tk.IntVar(value=self.audiofs/2)
        cm.var_minp = tk.DoubleVar(value=75.0)

        self.ent_size = tk.Entry(cm, textvariable=cm.var_size, state='disabled', validate='key', validatecommand=vcmd)
        self.ent_over = tk.Entry(cm, textvariable=cm.var_over, state='disabled', validate='key', validatecommand=vcmd)
        self.ent_minf = tk.Entry(cm, textvariable=cm.var_minf, state='disabled', validate='key', validatecommand=vcmd)
        self.ent_maxf = tk.Entry(cm, textvariable=cm.var_maxf, state='disabled', validate='key', validatecommand=vcmd)
        self.ent_minp = tk.Entry(cm, textvariable=cm.var_minp, state='disabled', validate='key', validatecommand=vcmd)

        self.ent_size.bind('<Return>', windowLengthEntry)
        self.ent_over.bind('<Return>', overlapEntry)
        self.ent_minf.bind('<Return>', minfreqEntry)
        self.ent_maxf.bind('<Return>', maxfreqEntry)
        self.ent_minp.bind('<Return>', minpitchEntry)

        self.ent_size.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        self.ent_over.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5, columnspan=1)
        self.ent_minf.grid(column=1, row=6, sticky=tk.EW, padx=5, pady=5)
        self.ent_maxf.grid(column=1, row=7, sticky=tk.EW, padx=5, pady=5)
        self.ent_minp.grid(column=1, row=12, sticky=tk.EW, padx=5, pady=5)
        
        # BUTTONS
        self.but_gene = tk.Button(tm, text='Generate', command=lambda: self.generatePureTone(tm))
        self.but_gene.grid(column=3, row=6, sticky=tk.EW, padx=5)

    def generatePureTone(self, tm):
        pass