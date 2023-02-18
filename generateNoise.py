import tkinter as tk

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Noise(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.controller.geometry('710x420') # size of the window
        self.controller.title("Generate noise")
        self.noiseMenu()

    def noiseMenu(self):
        nm = tk.Toplevel()
        nm.geometry('360x145')
        nm.resizable(True, True)
        nm.title('Generate noise')
        nm.wm_transient(self) # Place the toplevel window at the top
        # cm.iconbitmap('images/icon.ico')

        # LABELS
        lab_ampl = tk.Label(nm, text='Max. amplitude (dB)')
        lab_dura = tk.Label(nm, text='Total duration (s)')
        lab_ampl.grid(column=0, row=1, sticky=tk.E)
        lab_dura.grid(column=0, row=2, sticky=tk.E)

        # ENTRYS
        nm.var_ampl = tk.DoubleVar(value=1)
        nm.var_dura = tk.DoubleVar(value=1)
        self.ent_ampl = tk.Entry(nm, textvariable=nm.var_ampl, validate='key')
        self.ent_dura = tk.Entry(nm, textvariable=nm.var_dura, validate='key')

        def amplitudeEntry(event):
            maxAmplitude = float(self.ent_ampl.get())

        def durationEntry(event):
            duration = float(self.ent_dura.get())

        self.ent_ampl.bind('<Return>', amplitudeEntry)
        self.ent_dura.bind('<Return>', durationEntry)
        self.ent_ampl.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)
        self.ent_dura.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)

        # BUTTONS
        # Checks if all the values inserted by the user are correct
        def checkValues():
            pass

        self.but_samp = tk.Button(nm, text='New sample', command=lambda: self.generateNoise())
        self.but_gene = tk.Button(nm, text='Generate', command=lambda: checkValues())
        self.but_samp.grid(column=0, row=3, sticky=tk.EW, padx=5)
        self.but_gene.grid(column=1, row=3, sticky=tk.EW, padx=5)

        # OPTION MENUS
        nm.options = ['White noise','Pink noise', 'Brown noise']
        nm.var_opts = tk.StringVar()
        nm.var_opts.set(nm.options[0])
        self.dd_opts = tk.OptionMenu(nm, nm.var_opts, *nm.options)
        self.dd_opts.config(width=15)
        self.dd_opts.grid(column=0, row=0, sticky=tk.W, padx=5)

    def generateNoise(self):
        pass

