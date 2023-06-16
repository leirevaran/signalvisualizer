import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame

from auxiliar import Auxiliar

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Help(tk.Frame):

    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.hm = None

    def createHelpMenu(self, value):
        # If it already exists, change it with the new value and take it to the front
        if self.hm != None:
            self.hm.var_html.set(value) # change the selected radiobutton
            self.getValue(value) # change the html
            self.hm.focus_set() # Place the toplevel window at the top
            return
        
        self.hm = tk.Toplevel()
        self.hm.resizable(False, False)
        self.hm.title('Help menu')
        self.hm.iconbitmap('icons/icon.ico')
        self.hm.lift() # Place the toplevel window at the top
        self.aux = Auxiliar()
        self.aux.windowGeometry(self.hm, 975, 600, True)

        def on_closing():
            self.hm.destroy()
            self.hm = None
        self.hm.protocol("WM_DELETE_WINDOW", on_closing)

        self.noise_html = 'html/en/Generate noise/Generatenoise.html'
        self.puret_html = 'html/en/Generate pure tone/Generatepuretone.html'
        self.sawtw_html = 'html/en/Generate sawtooth signal/Generatesawtoothsignal.html'
        self.squaw_html = 'html/en/Generate square wave/Generatesquarewave.html'
        self.harmo_html = 'html/en/Harmonic synthesis/Harmonicsynthesis.html'
        self.loadf_html = 'html/en/Load audio file/Loadaudiofile.html'
        self.recor_html = 'html/en/Record audio/Recordaudio.html'
        self.visua_html = 'html/en/Visualization window/Visualizationwindow.html'

        # RADIOBUTTONS
        self.hm.var_html = tk.IntVar(value=value)

        rdb_pton = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=1, command=lambda: self.showHelp(self.puret_html), text='Pure Tone')
        rdb_addt = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=2, command=lambda: self.showHelp(self.harmo_html), text='Addition of tones')
        rdb_sqwv = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=3, command=lambda: self.showHelp(self.squaw_html), text='Square wave')
        rdb_stwv = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=4, command=lambda: self.showHelp(self.sawtw_html), text='Sawtooth wave')
        rdb_nois = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=5, command=lambda: self.showHelp(self.noise_html), text='Noise')
        rdb_load = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=6, command=lambda: self.showHelp(self.loadf_html), text='Load file')
        rdb_reco = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=7, command=lambda: self.showHelp(self.recor_html), text='Record sound')
        rdb_visu = ttk.Radiobutton(self.hm, variable=self.hm.var_html, value=8, command=lambda: self.showHelp(self.visua_html), text='Control menu')

        # positioning Radiobuttons
        rdb_pton.grid(column=0, row=0, sticky=tk.EW, padx=5, pady=5)
        rdb_addt.grid(column=0, row=1, sticky=tk.EW, padx=5, pady=5)
        rdb_sqwv.grid(column=0, row=2, sticky=tk.EW, padx=5, pady=5)
        rdb_stwv.grid(column=0, row=3, sticky=tk.EW, padx=5, pady=5)
        rdb_nois.grid(column=0, row=4, sticky=tk.EW, padx=5, pady=5)
        rdb_load.grid(column=0, row=5, sticky=tk.EW, padx=5, pady=5)
        rdb_reco.grid(column=0, row=6, sticky=tk.EW, padx=5, pady=5)
        rdb_visu.grid(column=0, row=7, sticky=tk.EW, padx=5, pady=5)

        # FRAME
        self.frm_html = HtmlFrame(self.hm, horizontal_scrollbar="auto", messages_enabled=False)
        self.frm_html.grid(column=1, row=0, rowspan=8)

        # Initialize the help frame by showing the required help
        self.getValue(value)

    def getValue(self, value):
        if value == 1:
            self.showHelp(self.puret_html)
        elif value == 2:
            self.showHelp(self.harmo_html)
        elif value == 3:
            self.showHelp(self.squaw_html)
        elif value == 4:
            self.showHelp(self.sawtw_html)
        elif value == 5:
            self.showHelp(self.noise_html)
        elif value == 6:
            self.showHelp(self.loadf_html)
        elif value == 7:
            self.showHelp(self.recor_html)
        elif value == 8:
            self.showHelp(self.visua_html)

    def showHelp(self, html):
        file = open(html, 'r', encoding="utf8")
        data = file.read()
        self.frm_html.load_html(data)