import tkinter as tk
from tkinter import ttk

from auxiliar import Auxiliar

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class AdvancedSettings():

    def advancedSettings(self):
        adse = tk.Toplevel()
        adse.geometry('738x420')
        adse.resizable(True, True)
        adse.title('Pitch - Advanced settings')
        adse.iconbitmap('icons/icon.ico')
        self.aux = Auxiliar()

        # Adapt the window to different sizes
        for i in range(3):
            adse.columnconfigure(i, weight=1)

        for i in range(11):
            adse.rowconfigure(i, weight=1)

        # LABELS (adse)
        lab_aucc = tk.Label(adse, text='Autocorrelation / Cross-correlation', bd=6, font=('TkDefaultFont', 10))
        lab_sith = tk.Label(adse, text='Silence treshold')
        lab_voth = tk.Label(adse, text='Voicing treshold')
        lab_octc = tk.Label(adse, text='Octave cost')
        lab_ocjc = tk.Label(adse, text='Octave jump cost')
        lab_vunc = tk.Label(adse, text='Voiced-unvoiced cost')

        lab_subh = tk.Label(adse, text='Subharmonics', bd=6, font=('TkDefaultFont', 10))
        lab_mxfc = tk.Label(adse, text='Max frequency component')
        lab_mxsh = tk.Label(adse, text='Max number of subharmonics')
        lab_cmpf = tk.Label(adse, text='Compression factor')
        lab_ptso = tk.Label(adse, text='Number of points per octave')

        lab_spin = tk.Label(adse, text='Spinet', bd=6, font=('TkDefaultFont', 10))
        lab_winl = tk.Label(adse, text='Window length')
        lab_mnfi = tk.Label(adse, text='Min filter frequency')
        lab_mxfi = tk.Label(adse, text='Max filter frequency')
        lab_filt = tk.Label(adse, text='Number of filters')

        lab_cand = tk.Label(adse, text='Max number of candidates')
        lab_draw = tk.Label(adse, text='Drawing style')

        # positioning Labels (adse)
        lab_aucc.grid(column=0, row=0, sticky=tk.E, columnspan=2)
        lab_sith.grid(column=0, row=1, sticky=tk.E)
        lab_voth.grid(column=0, row=2, sticky=tk.E)
        lab_octc.grid(column=0, row=3, sticky=tk.E)
        lab_ocjc.grid(column=0, row=4, sticky=tk.E)
        lab_vunc.grid(column=0, row=5, sticky=tk.E)

        lab_subh.grid(column=1, row=7)
        lab_mxfc.grid(column=0, row=8, sticky=tk.E)
        lab_mxsh.grid(column=0, row=9, sticky=tk.E)
        lab_cmpf.grid(column=0, row=10, sticky=tk.E)
        lab_ptso.grid(column=0, row=11, sticky=tk.E)

        lab_spin.grid(column=3, row=0)
        lab_winl.grid(column=2, row=1, sticky=tk.E)
        lab_mnfi.grid(column=2, row=2, sticky=tk.E)
        lab_mxfi.grid(column=2, row=3, sticky=tk.E)
        lab_filt.grid(column=2, row=4, sticky=tk.E)

        lab_cand.grid(column=2, row=8, sticky=tk.E)
        lab_draw.grid(column=2, row=9, sticky=tk.E)

        # ENTRYS (adse)
        adse.var_sith = tk.DoubleVar(value=0.03)
        adse.var_voth = tk.DoubleVar(value=0.45)
        adse.var_octc = tk.DoubleVar(value=0.01)
        adse.var_ocjc = tk.DoubleVar(value=0.35)
        adse.var_vunc = tk.DoubleVar(value=0.14)

        adse.var_mxfc = tk.DoubleVar(value=1250)
        adse.var_subh = tk.IntVar(value=15)
        adse.var_cmpf = tk.DoubleVar(value=0.84)
        adse.var_ptso = tk.IntVar(value=48)

        adse.var_winl = tk.DoubleVar(value=0.04)
        adse.var_mnfi = tk.DoubleVar(value=70)
        adse.var_mxfi = tk.DoubleVar(value=5000)
        adse.var_filt = tk.IntVar(value=250)

        adse.var_cand = tk.IntVar(value=15)

        vcmd = (adse.register(self.aux.onValidate), '%S', '%s', '%d')

        ent_sith = ttk.Entry(adse, textvariable=adse.var_sith, validate='key', validatecommand=vcmd)
        ent_voth = ttk.Entry(adse, textvariable=adse.var_voth, validate='key', validatecommand=vcmd)
        ent_octc = ttk.Entry(adse, textvariable=adse.var_octc, validate='key', validatecommand=vcmd)
        ent_ocjc = ttk.Entry(adse, textvariable=adse.var_ocjc, validate='key', validatecommand=vcmd)
        ent_vunc = ttk.Entry(adse, textvariable=adse.var_vunc, validate='key', validatecommand=vcmd)

        ent_mxfc = ttk.Entry(adse, textvariable=adse.var_mxfc, validate='key', validatecommand=vcmd)
        ent_subh = ttk.Entry(adse, textvariable=adse.var_subh, validate='key', validatecommand=vcmd)
        ent_cmpf = ttk.Entry(adse, textvariable=adse.var_cmpf, validate='key', validatecommand=vcmd)
        ent_ptso = ttk.Entry(adse, textvariable=adse.var_ptso, validate='key', validatecommand=vcmd)
        
        ent_winl = ttk.Entry(adse, textvariable=adse.var_winl, validate='key', validatecommand=vcmd)
        ent_mnfi = ttk.Entry(adse, textvariable=adse.var_mnfi, validate='key', validatecommand=vcmd)
        ent_mxfi = ttk.Entry(adse, textvariable=adse.var_mxfi, validate='key', validatecommand=vcmd)
        ent_filt = ttk.Entry(adse, textvariable=adse.var_filt, validate='key', validatecommand=vcmd)

        ent_cand = ttk.Entry(adse, textvariable=adse.var_cand, validate='key', validatecommand=vcmd)

        # positioning Entrys (adse)
        ent_sith.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)
        ent_voth.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_octc.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_ocjc.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)
        ent_vunc.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5)

        ent_subh.grid(column=1, row=8, sticky=tk.EW, padx=5, pady=5)
        ent_mxfc.grid(column=1, row=9, sticky=tk.EW, padx=5, pady=5)
        ent_cmpf.grid(column=1, row=10, sticky=tk.EW, padx=5, pady=5)
        ent_ptso.grid(column=1, row=11, sticky=tk.EW, padx=5, pady=5)

        ent_winl.grid(column=3, row=1, sticky=tk.EW, padx=5, pady=5)
        ent_mnfi.grid(column=3, row=2, sticky=tk.EW, padx=5, pady=5)
        ent_mxfi.grid(column=3, row=3, sticky=tk.EW, padx=5, pady=5)
        ent_filt.grid(column=3, row=4, sticky=tk.EW, padx=5, pady=5)

        ent_cand.grid(column=3, row=8, sticky=tk.EW, padx=5, pady=5)

        # CHECKBOX (adse)
        adse.var_accu = tk.StringVar(value=0)
        chk_accu = tk.Checkbutton(adse, text='Very accurate', variable=adse.var_accu)
        chk_accu.grid(column=1, row=6, sticky=tk.W)

        # RADIOBUTTONS (adse)
        adse.var_draw = tk.IntVar(value=1)
        
        rdb_curv = tk.Radiobutton(adse, text='curve', variable=adse.var_draw, value=1)
        rdb_spec = tk.Radiobutton(adse, text='speckles', variable=adse.var_draw, value=2)
        
        rdb_curv.grid(column=3, row=9, sticky=tk.W)
        rdb_spec.grid(column=3, row=9, sticky=tk.E)

        # BUTTONS (adse)
        but_apply = ttk.Button(adse, text='Apply', command=lambda: self.apply(adse))
        but_apply.configure()
        but_apply.grid(column=3, row=11, sticky=tk.EW, padx=5, pady=5)

    def apply(self, adse):
        self.silenth = adse.var_sith.get()
        self.voiceth = adse.var_voth.get()
        self.octcost = adse.var_octc.get()
        self.ocjumpc = adse.var_ocjc.get()
        self.vuncost = adse.var_vunc.get()
        self.veryacc = adse.var_accu.get()

        self.maxcomp = adse.var_mxfc.get()
        self.maxsubh = adse.var_subh.get()
        self.compfac = adse.var_cmpf.get()
        self.pntsoct = adse.var_ptso.get()

        self.windlen = adse.var_winl.get()
        self.minfilt = adse.var_mnfi.get()
        self.maxfilt = adse.var_mxfi.get()
        self.filters = adse.var_filt.get()

        self.maxcand = adse.var_cand.get()
        self.drawing = adse.var_draw.get()

        adse.destroy()

    def getVariables(self):
        return self.maxcand, self.drawing
    
    def getAutocorrelationVars(self):
        return self.silenth, self.voiceth, self.octcost, self.ocjumpc, self.vuncost, self.veryacc
    
    def getSubharmonicsVars(self):
        return self.maxcomp, self.maxsubh, self.compfac, self.pntsoct
    
    def getSpinetVars(self):
        return self.windlen, self.minfilt, self.maxfilt, self.filters

    # Used when the user hasn't opened the advanced settings' window
    def createVariables(self):
        # Create variables for the advanced settings of Pitch
        self.maxcand = 15 # max number of candidates
        self.drawing = 1 # drawing style
        # Autocorrelation / Cross-correlation
        self.silenth = 0.03 # silence treshold
        self.voiceth = 0.45 # voicing treshold
        self.octcost = 0.01 # octave cost
        self.ocjumpc = 0.35 # octave jump cost
        self.vuncost = 0.14 # voiced unvoiced cost
        self.veryacc = 0 # very accurate
        # Subharmonics
        self.maxcomp = 1250 # max frequency component
        self.maxsubh = 15 # max number of subharmonics
        self.compfac = 0.84 # compression factor
        self.pntsoct = 48 # number of points per octave
        # Spinet
        self.windlen = 0.04 # window length
        self.minfilt = 70 # min filter frequency
        self.maxfilt = 5000 # max filter frequency
        self.filters = 250 # number of filters
