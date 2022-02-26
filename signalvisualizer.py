import tkinter as tk
from loadApp import LoadApp

class Start(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self._frame = None
        self.switch_frame(SignalVisualizer)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


class SignalVisualizer(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        master.geometry('700x500') # size of the window

        self.createMenuBar()

    def createMenuBar(self):
        # the menu bar will be at the top of the window
        menubar = tk.Menu(self.master)
        
        # creation of the options in the menu bar
        signalmenu = tk.Menu(menubar, tearoff=0)
        signalmenu.add_command(label="Info")
        signalmenu.add_command(label="Exit", command=self.master.quit)

        generatemenu = tk.Menu(menubar, tearoff=0)
        generatemenu.add_command(label="Pure tone")
        generatemenu.add_command(label="Free addition of pure tones")
        generatemenu.add_command(label="Known periodic signals")
        generatemenu.add_command(label="Noise")

        inputmenu = tk.Menu(menubar, tearoff=0)
        inputmenu.add_command(label="Load", command=lambda: self.master.switch_frame(LoadApp))
        inputmenu.add_command(label="Record")

        optionsmenu = tk.Menu(menubar, tearoff=0)
        optionsmenu.add_command(label="General")
        optionsmenu.add_command(label="Signal")
        optionsmenu.add_command(label="Spectrogram")

        # adding the options created to the menu bar
        menubar.add_cascade(label="Signal Visualizer", menu=signalmenu)
        menubar.add_cascade(label="Generate", menu=generatemenu)
        menubar.add_cascade(label="Input", menu=inputmenu)
        menubar.add_cascade(label="Options", menu=optionsmenu)

        self.master.config(menu=menubar)

if __name__ == "__main__":
    app = Start()
    app.mainloop()