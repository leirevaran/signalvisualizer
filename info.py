import tkinter as tk
from tkinter import ttk

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Info(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.infoWindow()

    def infoWindow(self):
        iw = tk.Toplevel()
        iw.resizable(False, False)
        iw.title('Information')
        iw.iconbitmap('icons/icon.ico')
        iw.wm_transient(self) # Place the toplevel window at the top
        # self.cm.windowGeometry(iw, 850, 250)

        # LABELS
        lab_titl = ttk.Label(iw, text='Signal Visualizer', font=('TkDefaultFont', 12))
        lab_intr = ttk.Label(iw, text='A collaboration between University of the Basque Country (UPV/EHU)\nand Musikene, Higher School of Music of the Basque Country.\n')
        
        lab_lea1 = ttk.Label(iw, font=('TkDefaultFont', 9, "italic"), text='Project leader:')
        lab_con1 = ttk.Label(iw, font=('TkDefaultFont', 9, "italic"), text='Project leader from Musikene:')
        lab_dev1 = ttk.Label(iw, font=('TkDefaultFont', 9, "italic"), text='Developers:')
        lab_ico1 = ttk.Label(iw, font=('TkDefaultFont', 9, "italic"), text='Program icon and logo made by:')

        lab_lea2 = ttk.Label(iw, text='Inma Hernáez Rioja')
        lab_con2 = ttk.Label(iw, text='José María Bretos')
        lab_dev2 = ttk.Label(iw, text='Leire Varela Aranguren, Valentin Lurier, Eder del Blanco Sierra, Mikel Díez García')
        lab_ico2 = ttk.Label(iw, text='Sergio Santamaría Martínez')

        lab_ahol = ttk.Label(iw, text='\nHiTZ Basque Center for Language Technologies - Aholab Signal Processing Laboratory (UPV/EHU).\n')
        lab_refe = ttk.Label(iw, text='References:')
        lab_ref1 = ttk.Label(iw, text='Function for creating brown (or red) noise made by Hristo Zhivomirov:\n'+'Hristo Zhivomirov (2020). Pink, Red, Blue and Violet Noise Generation with Matlab.\n'+'https://www.mathworks.com/matlabcentral/fileexchange/42919-pink-red-blue-and-violet-noise-generation-with-matlab\n'+'MATLAB Central File Exchange. Retrieved August 4, 2020.')
        lab_ref2 = ttk.Label(iw, text='Master thesis describing the version of the software Signal Visualizer in Matlab made by Eder del Blanco Sierra:\n'+'Eder del Blanco Sierra (2020). Programa de apoyo a la enseñanza musical.\n'+'University of the Basque Country (UPV/EHU). Department of Communications Engineering. Retrieved August 8, 2020.\n'+'The function has been modified by Valentin Lurier and Mikel Díez García.')

        # positioning Labels
        lab_titl.grid(column=0, row=0, sticky=tk.W, columnspan=40, padx=20, pady=10)
        lab_intr.grid(column=0, row=1, sticky=tk.W, columnspan=40, padx=20)

        lab_lea1.grid(column=0, row=2, sticky=tk.W, padx=20)
        lab_con1.grid(column=0, row=3, sticky=tk.W, padx=20)
        lab_dev1.grid(column=0, row=4, sticky=tk.W, padx=20)
        lab_ico1.grid(column=0, row=5, sticky=tk.W, padx=20)

        lab_lea2.grid(column=1, row=2, sticky=tk.W, padx=20)
        lab_con2.grid(column=1, row=3, sticky=tk.W, padx=20)
        lab_dev2.grid(column=1, row=4, sticky=tk.W, padx=20)
        lab_ico2.grid(column=1, row=5, sticky=tk.W, padx=20)

        lab_ahol.grid(column=0, row=7, sticky=tk.W, columnspan=40, padx=20)
        lab_refe.grid(column=0, row=8, sticky=tk.W, columnspan=40, padx=20)
        lab_ref1.grid(column=0, row=9, sticky=tk.W, columnspan=40, padx=20)
        lab_ref2.grid(column=0, row=10, sticky=tk.W, columnspan=40, padx=20, pady=20)