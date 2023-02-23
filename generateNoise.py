import tkinter as tk
import colorednoise as cn
import matplotlib.pyplot as plt

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Noise(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.noiseMenu()

    def noiseMenu(self):
        nm = tk.Toplevel()
        nm.geometry('660x240')
        nm.resizable(True, True)
        nm.title('Generate noise')
        nm.iconbitmap('images/icon.ico')
        nm.wm_transient(self) # Place the toplevel window at the top

        # LABELS
        lab_type = tk.Label(nm, text='Noise type')
        lab_ampl = tk.Label(nm, text='Max. amplitude (dB)')
        lab_dura = tk.Label(nm, text='Total duration (s)')
        lab_type.grid(column=0, row=0, sticky=tk.E)
        lab_ampl.grid(column=0, row=1, sticky=tk.E)
        lab_dura.grid(column=0, row=2, sticky=tk.E)

        # SCALERS
        nm.var_ampl = tk.DoubleVar(value=1)
        nm.var_dura = tk.DoubleVar(value=1)
        self.sca_ampl = tk.Scale(nm, from_=0, to=1, variable=nm.var_ampl, length=500, orient='horizontal', tickinterval=0.1, resolution=0.1)
        self.sca_dura = tk.Scale(nm, from_=0, to=30, variable=nm.var_dura, length=500, orient='horizontal', tickinterval=5)
        self.sca_ampl.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5, columnspan=3)
        self.sca_dura.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5, columnspan=3)

        # BUTTONS
        self.but_samp = tk.Button(nm, text='New sample', command=lambda: self.newSample(nm))
        self.but_gene = tk.Button(nm, text='Generate', command=lambda: self.generateNoise(nm))
        self.but_samp.grid(column=2, row=4, sticky=tk.EW, padx=5)
        self.but_gene.grid(column=3, row=4, sticky=tk.EW, padx=5)

        # OPTION MENUS
        nm.options = ['White noise','Pink noise', 'Brown noise']
        nm.var_opts = tk.StringVar()
        nm.var_opts.set(nm.options[0])
        self.dd_opts = tk.OptionMenu(nm, nm.var_opts, *nm.options)
        self.dd_opts.config(width=15)
        self.dd_opts.grid(column=1, row=0, sticky=tk.W, padx=5)

    def newSample(self, nm):
        pass

    def generateNoise(self, nm):
        choice = nm.var_opts.get()
        maxampl = float(self.sca_ampl.get())
        duration = self.sca_dura.get()
        samples = 2**16
        print(samples)

        if choice == 'White noise':
            beta = 0
        elif choice == 'Pink noise':
            beta = 1
        elif choice == 'Brown noise':
            beta = 2

        noise = cn.powerlaw_psd_gaussian(beta, samples)
        plt.plot(noise)
        plt.xlabel('Samples (time-steps)')
        plt.ylabel('Amplitude')
        plt.title(str(choice))
        plt.xlim(1, 5000)
        plt.show()