import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from tkinter import ttk

from controlMenu import ControlMenu

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Spectrogram(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.cm = ControlMenu()
        self.file = 'csv/colormap.csv'
        self.colormapMenu()

    def colormapMenu(self):
        cmm = tk.Toplevel()
        cmm.resizable(True, True)
        cmm.title('Choose colormap of the spectrogram')
        # cmm.iconbitmap('icon.ico')
        cmm.wm_transient(self) # Place the toplevel window at the top
        # self.cm.windowGeometry(cmm, 850, 250)

        # Adapt the window to different sizes
        for i in range(1):
            cmm.columnconfigure(i, weight=1)

        for i in range(7):
            cmm.rowconfigure(i, weight=1)

        # If the 'Control menu' window is closed, close also all the generated figures
        def on_closing():
            cmm.destroy()
            plt.close('all') # closes all matplotlib figures
        cmm.protocol("WM_DELETE_WINDOW", on_closing)

        # COLORMAPS
        cmaps = [('Perceptually Uniform Sequential', [
                    'viridis', 'plasma', 'inferno', 'magma', 'cividis']),
                ('Sequential', [
                    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
                ('Sequential (2)', [
                    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                    'hot', 'afmhot', 'gist_heat', 'copper']),
                ('Diverging', [
                    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
                ('Cyclic', ['twilight', 'twilight_shifted', 'hsv']),
                ('Qualitative', [
                    'Pastel1', 'Pastel2', 'Paired', 'Accent',
                    'Dark2', 'Set1', 'Set2', 'Set3',
                    'tab10', 'tab20', 'tab20b', 'tab20c']),
                ('Miscellaneous', [
                    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                    'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                    'gist_ncar'])]
        
        gradient = np.linspace(0, 1, 256)
        gradient = np.vstack((gradient, gradient))

        # for cmap_category, cmap_list in cmaps:
        #     self.plot_color_gradients(cmap_category, cmap_list, gradient)
        
        # plt.show()

        # Read the value of the colormap from a csv file
        list = self.cm.readFromCsv(self.file)
        choice = list[0]

        for cmap_category, cmap_list in cmaps:
            for i in range(len(cmap_list)):
                if choice == cmap_list[i]:
                    category = cmap_category
                    index = i
                    break

        idx1, idx2, idx3, idx4, idx5, idx6, idx7 = 0, 0, 0, 0, 0, 0, 0

        if category == 'Perceptually Uniform Sequential':
            value = 1
            idx1 = index
        elif category == 'Sequential':
            value = 2
            idx2 = index
        elif category == 'Sequential (2)':
            value = 3
            idx3 = index
        elif category == 'Diverging':
            value = 4
            idx4 = index
        elif category == 'Cyclic':
            value = 5
            idx5 = index
        elif category == 'Qualitative':
            value = 6
            idx6 = index
        elif category == 'Miscellaneous':
            value = 7
            idx7 = index

        # OPTION MENUS
        cmm.opt_pusq = cmaps[0][1]
        cmm.opt_sequ = cmaps[1][1]
        cmm.opt_seq2 = cmaps[2][1]
        cmm.opt_dive = cmaps[3][1]
        cmm.opt_cycl = cmaps[4][1]
        cmm.opt_qual = cmaps[5][1]
        cmm.opt_misc = cmaps[6][1]

        cmm.var_pusq = tk.StringVar()
        cmm.var_sequ = tk.StringVar()
        cmm.var_seq2 = tk.StringVar()
        cmm.var_dive = tk.StringVar()
        cmm.var_cycl = tk.StringVar()
        cmm.var_qual = tk.StringVar()
        cmm.var_misc = tk.StringVar()

        # creating option menus
        self.dd_pusq = ttk.OptionMenu(cmm, cmm.var_pusq, cmm.opt_pusq[idx1], *cmm.opt_pusq)
        self.dd_sequ = ttk.OptionMenu(cmm, cmm.var_sequ, cmm.opt_sequ[idx2], *cmm.opt_sequ)
        self.dd_seq2 = ttk.OptionMenu(cmm, cmm.var_seq2, cmm.opt_seq2[idx3], *cmm.opt_seq2)
        self.dd_dive = ttk.OptionMenu(cmm, cmm.var_dive, cmm.opt_dive[idx4], *cmm.opt_dive)
        self.dd_cycl = ttk.OptionMenu(cmm, cmm.var_cycl, cmm.opt_cycl[idx5], *cmm.opt_cycl)
        self.dd_qual = ttk.OptionMenu(cmm, cmm.var_qual, cmm.opt_qual[idx6], *cmm.opt_qual)
        self.dd_misc = ttk.OptionMenu(cmm, cmm.var_misc, cmm.opt_misc[idx7], *cmm.opt_misc)

        # size of the OptionMenus
        self.dd_pusq.config(width=18)
        self.dd_sequ.config(width=18)
        self.dd_seq2.config(width=18)
        self.dd_dive.config(width=18)
        self.dd_cycl.config(width=18)
        self.dd_qual.config(width=18)
        self.dd_misc.config(width=18)

        # positioning OptionMenus
        self.dd_pusq.grid(column=0, row=1, sticky=tk.EW, padx=5)
        self.dd_sequ.grid(column=0, row=3, sticky=tk.EW, padx=5)
        self.dd_seq2.grid(column=0, row=5, sticky=tk.EW, padx=5)
        self.dd_dive.grid(column=0, row=7, sticky=tk.EW, padx=5)
        self.dd_cycl.grid(column=0, row=9, sticky=tk.EW, padx=5)
        self.dd_qual.grid(column=0, row=11, sticky=tk.EW, padx=5)
        self.dd_misc.grid(column=0, row=13, sticky=tk.EW, padx=5)

        # RADIOBUTTONS
        cmm.var_type = tk.IntVar(value=value)

        self.rdb_pusq = tk.Radiobutton(cmm, variable=cmm.var_type, value=1, command=lambda: self.displayOptions(cmm.var_type.get()), text='Perceptually Uniform Sequential')
        self.rdb_sequ = tk.Radiobutton(cmm, variable=cmm.var_type, value=2, command=lambda: self.displayOptions(cmm.var_type.get()), text='Sequential')
        self.rdb_seq2 = tk.Radiobutton(cmm, variable=cmm.var_type, value=3, command=lambda: self.displayOptions(cmm.var_type.get()), text='Sequential (2)')
        self.rdb_dive = tk.Radiobutton(cmm, variable=cmm.var_type, value=4, command=lambda: self.displayOptions(cmm.var_type.get()), text='Diverging')
        self.rdb_cycl = tk.Radiobutton(cmm, variable=cmm.var_type, value=5, command=lambda: self.displayOptions(cmm.var_type.get()), text='Cyclic')
        self.rdb_qual = tk.Radiobutton(cmm, variable=cmm.var_type, value=6, command=lambda: self.displayOptions(cmm.var_type.get()), text='Qualitative')
        self.rdb_misc = tk.Radiobutton(cmm, variable=cmm.var_type, value=7, command=lambda: self.displayOptions(cmm.var_type.get()), text='Miscellaneous')
           
        self.rdb_pusq.grid(column=0, row=0, sticky=tk.W)
        self.rdb_sequ.grid(column=0, row=2, sticky=tk.W)
        self.rdb_seq2.grid(column=0, row=4, sticky=tk.W)
        self.rdb_dive.grid(column=0, row=6, sticky=tk.W)
        self.rdb_cycl.grid(column=0, row=8, sticky=tk.W)
        self.rdb_qual.grid(column=0, row=10, sticky=tk.W)
        self.rdb_misc.grid(column=0, row=12, sticky=tk.W)

        # BUTTONS
        self.but_pusq = ttk.Button(cmm, text='Show colormap', command=lambda: self.plot_color_gradients(cmaps[0], cmaps[0][1], gradient))
        self.but_sequ = ttk.Button(cmm, text='Show colormap', command=lambda: self.plot_color_gradients(cmaps[1], cmaps[1][1], gradient))
        self.but_seq2 = ttk.Button(cmm, text='Show colormap', command=lambda: self.plot_color_gradients(cmaps[2], cmaps[2][1], gradient))
        self.but_dive = ttk.Button(cmm, text='Show colormap', command=lambda: self.plot_color_gradients(cmaps[3], cmaps[3][1], gradient))
        self.but_cycl = ttk.Button(cmm, text='Show colormap', command=lambda: self.plot_color_gradients(cmaps[4], cmaps[4][1], gradient))
        self.but_qual = ttk.Button(cmm, text='Show colormap', command=lambda: self.plot_color_gradients(cmaps[5], cmaps[5][1], gradient))
        self.but_misc = ttk.Button(cmm, text='Show colormap', command=lambda: self.plot_color_gradients(cmaps[6], cmaps[6][1], gradient))
        self.but_save = ttk.Button(cmm, text='Save changes', command=lambda: self.setColormap(cmm))

        # positioning Buttons
        self.but_pusq.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)
        self.but_sequ.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5)
        self.but_seq2.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5)
        self.but_dive.grid(column=1, row=7, sticky=tk.EW, padx=5, pady=5)
        self.but_cycl.grid(column=1, row=9, sticky=tk.EW, padx=5, pady=5)
        self.but_qual.grid(column=1, row=11, sticky=tk.EW, padx=5, pady=5)
        self.but_misc.grid(column=1, row=13, sticky=tk.EW, padx=5, pady=5)
        self.but_save.grid(column=1, row=15, sticky=tk.EW, padx=5, pady=5)

        # Put the readen value from the csv file as the default value
        self.displayOptions(value)

    def displayOptions(self, type):
        if type == 1: 
            self.dd_pusq.config(state='active')
            self.but_pusq.configure(state='active')
        else: 
            self.dd_pusq.config(state='disabled')
            self.but_pusq.configure(state='disabled')

        if type == 2: 
            self.dd_sequ.config(state='active')
            self.but_sequ.configure(state='active')
        else: 
            self.dd_sequ.config(state='disabled')
            self.but_sequ.configure(state='disabled')

        if type == 3: 
            self.dd_seq2.config(state='active')
            self.but_seq2.configure(state='active')
        else: 
            self.dd_seq2.config(state='disabled')
            self.but_seq2.configure(state='disabled')

        if type == 4: 
            self.dd_dive.config(state='active')
            self.but_dive.configure(state='active')
        else: 
            self.dd_dive.config(state='disabled')
            self.but_dive.configure(state='disabled')

        if type == 5: 
            self.dd_cycl.config(state='active')
            self.but_cycl.configure(state='active')
        else: 
            self.dd_cycl.config(state='disabled')
            self.but_cycl.configure(state='disabled')

        if type == 6: 
            self.dd_qual.config(state='active')
            self.but_qual.configure(state='active')
        else: 
            self.dd_qual.config(state='disabled')
            self.but_qual.configure(state='disabled')

        if type == 7: 
            self.dd_misc.config(state='active')
            self.but_misc.configure(state='active')
        else: 
            self.dd_misc.config(state='disabled')
            self.but_misc.configure(state='disabled')

    def plot_color_gradients(self, cmap_category, cmap_list, gradient):
        # Create figure and adjust figure height to number of colormaps
        nrows = len(cmap_list)
        figh = 0.35 + 0.15 + (nrows + (nrows-1)*0.1)*0.22
        fig, axs = plt.subplots(nrows=nrows, figsize=(6.4, figh))
        fig.subplots_adjust(top=1-.35/figh, bottom=.15/figh, left=0.2, right=0.99)

        axs[0].set_title(f"{cmap_category[0]} colormaps", fontsize=14)

        for ax, cmap_name in zip(axs, cmap_list):
            ax.imshow(gradient, aspect='auto', cmap=cmap_name)
            ax.text(-.01, .5, cmap_name, va='center', ha='right', fontsize=10,
                    transform=ax.transAxes)

        # Turn off *all* ticks & spines, not just the ones with colormaps.
        for ax in axs:
            ax.set_axis_off()

        plt.show()

    def setColormap(self, cmm):
        type = cmm.var_type.get()

        if type == 1:
            choice = cmm.var_pusq.get()
        elif type == 2: 
            choice = cmm.var_sequ.get()
        elif type == 3: 
            choice = cmm.var_seq2.get()
        elif type == 4: 
            choice = cmm.var_dive.get()
        elif type == 5: 
            choice = cmm.var_cycl.get()
        elif type == 6: 
            choice = cmm.var_qual.get()
        elif type == 7: 
            choice = cmm.var_misc.get()

        self.cm.saveDefaultAsCsv(self.file, [choice])
        cmm.destroy() # close window
        plt.close('all') # closes all matplotlib figures