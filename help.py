import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class HelpMenu():

    def createHelpMenu(self, root, value):
        hm = tk.Toplevel()
        hm.resizable(False, False)
        hm.title('Help menu')
        hm.iconbitmap('icons/icon.ico')
        hm.wm_transient(root) # Place the toplevel window at the top

        noise_html = 'html/en/Generate noise/Generatenoise.html'
        puret_html = 'html/en/Generate pure tone/Generatepuretone.html'
        sawtw_html = 'html/en/Generate sawtooth signal/Generatesawtoothsignal.html'
        squaw_html = 'html/en/Generate square wave/Generatesquarewave.html'
        harmo_html = 'html/en/Harmonic synthesis/Harmonicsynthesis.html'
        loadf_html = 'html/en/Load audio file/Loadaudiofile.html'
        recor_html = 'html/en/Record audio/Recordaudio.html'
        visua_html = 'html/en/Visualization window/Visualizationwindow.html'

        # RADIOBUTTONS
        hm.var_html = tk.IntVar(value=value)

        rdb_pton = ttk.Radiobutton(hm, variable=hm.var_html, value=1, command=lambda: self.showHelp(puret_html, frm_html), text='Pure Tone')
        rdb_addt = ttk.Radiobutton(hm, variable=hm.var_html, value=2, command=lambda: self.showHelp(harmo_html, frm_html), text='Addition of tones')
        rdb_sqwv = ttk.Radiobutton(hm, variable=hm.var_html, value=3, command=lambda: self.showHelp(squaw_html, frm_html), text='Square wave')
        rdb_stwv = ttk.Radiobutton(hm, variable=hm.var_html, value=4, command=lambda: self.showHelp(sawtw_html, frm_html), text='Sawtooth wave')
        rdb_nois = ttk.Radiobutton(hm, variable=hm.var_html, value=5, command=lambda: self.showHelp(noise_html, frm_html), text='Noise')
        rdb_load = ttk.Radiobutton(hm, variable=hm.var_html, value=6, command=lambda: self.showHelp(loadf_html, frm_html), text='Load file')
        rdb_reco = ttk.Radiobutton(hm, variable=hm.var_html, value=7, command=lambda: self.showHelp(recor_html, frm_html), text='Record sound')
        rdb_visu = ttk.Radiobutton(hm, variable=hm.var_html, value=8, command=lambda: self.showHelp(visua_html, frm_html), text='Visualization')

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
        frm_html = HtmlFrame(hm, horizontal_scrollbar="auto", messages_enabled=False)
        frm_html.grid(column=1, row=0, rowspan=8)

        # Initialize the help frame by showing the required help
        if value == 1:
            self.showHelp(puret_html, frm_html)
        elif value == 2:
            self.showHelp(harmo_html, frm_html)
        elif value == 3:
            self.showHelp(squaw_html, frm_html)
        elif value == 4:
            self.showHelp(sawtw_html, frm_html)
        elif value == 5:
            self.showHelp(noise_html, frm_html)
        elif value == 6:
            self.showHelp(loadf_html, frm_html)
        elif value == 7:
            self.showHelp(recor_html, frm_html)
        elif value == 8:
            self.showHelp(visua_html, frm_html)

    def showHelp(self, html, frm_html):
        file = open(html, 'r', encoding="utf8")
        data = file.read()
        frm_html.load_html(data)