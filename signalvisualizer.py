import tkinter as tk
from matplotlib import backend_bases

from inputLoad import Load
from generateNoise import Noise
from generatePureTone import PureTone
from generateFreeAdd import FreeAdditionPureTones

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Start(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Delete two options of the toolbar of the figures. This must be done before the figures are created
        backend_bases.NavigationToolbar2.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to  previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
        )

        self.frames = {}
        self.initialize_frame('SignalVisualizer')

    def initialize_frame(self, page_name):
        if page_name == 'SignalVisualizer':
            self.frames['SignalVisualizer'] = SignalVisualizer(master=self.container, controller=self)
            self.frames['SignalVisualizer'].grid(row=0, column=0, sticky="nsew")
            self.show_frame('SignalVisualizer')
        elif page_name == 'Load':
            self.frames['Load'] = Load(master=self.container, controller=self)
            self.frames['Load'].grid(row=0, column=0, sticky="nsew")
            self.show_frame('Load')
        elif page_name == 'Noise':
            self.frames['Noise'] = Noise(master=self.container, controller=self)
            self.frames['Noise'].grid(row=0, column=0, sticky="nsew")
            self.show_frame('Noise')
        elif page_name == 'PureTone':
            self.frames['PureTone'] = PureTone(master=self.container, controller=self)
            self.frames['PureTone'].grid(row=0, column=0, sticky="nsew")
            self.show_frame('PureTone')
        elif page_name == 'FreeAdditionPureTones':
            self.frames['FreeAdditionPureTones'] = FreeAdditionPureTones(master=self.container, controller=self)
            self.frames['FreeAdditionPureTones'].grid(row=0, column=0, sticky="nsew")
            self.show_frame('FreeAdditionPureTones')

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == 'SignalVisualizer':
            menubar = frame.menubar(self)
            self.configure(menu=menubar)

class SignalVisualizer(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.controller.geometry('710x420') # size of the window
        self.controller.title('Signal Visualizer')
        self.controller.iconbitmap('icon.ico')

    def menubar(self, root):
        # the menu bar will be at the top of the window
        menubar = tk.Menu(root)
            
        # creation of the options in the menu bar
        signalmenu = tk.Menu(menubar, tearoff=0) # tearoff=0 to avoid useless lines
        signalmenu.add_command(label="Info")
        signalmenu.add_command(label="Exit", command=self.quit)

        generatemenu = tk.Menu(menubar, tearoff=0)
        generatemenu.add_command(label="Pure tone", command=lambda: self.controller.initialize_frame('PureTone'))
        generatemenu.add_command(label="Free addition of pure tones", command=lambda: self.controller.initialize_frame('FreeAdditionPureTones'))
        generatemenu.add_command(label="Noise", command=lambda: self.controller.initialize_frame('Noise'))

        knownmenu = tk.Menu(generatemenu, tearoff=0)
        knownmenu.add_command(label="Square wave")
        knownmenu.add_command(label="Sawtooth wave")
        knownmenu.add_command(label="Rosenberg pulse")

        inputmenu = tk.Menu(menubar, tearoff=0)
        inputmenu.add_command(label="Load", command=lambda: self.controller.initialize_frame('Load'))
        inputmenu.add_command(label="Record")

        optionsmenu = tk.Menu(menubar, tearoff=0)
        optionsmenu.add_command(label="General")
        optionsmenu.add_command(label="Signal")
        optionsmenu.add_command(label="Spectrogram")

        # adding the options created to the menu bar
        menubar.add_cascade(label="Signal Visualizer", menu=signalmenu)
        menubar.add_cascade(label="Generate", menu=generatemenu)
        generatemenu.add_cascade(label="Known periodic signals", menu=knownmenu)
        menubar.add_cascade(label="Input", menu=inputmenu)
        menubar.add_cascade(label="Options", menu=optionsmenu)

        return menubar
    
    # def createWindowButtons(self):
    #     w1Button = tk.Button(self, text="Window1", command=lambda: self.controller.show_frame('LoadApp')) # with lambda, the action is only made when the button is pressed
    #     w1Button.configure(state="disabled")
    #     w1Button.grid()
    
if __name__ == "__main__":
    app = Start()
    app.mainloop()
