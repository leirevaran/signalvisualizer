from cProfile import label
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from scipy.io.wavfile import read

root = tk.Tk()
root.title("Signal Visualizer") # name of the window
root.iconbitmap("images/icon.ico") # icon at the top of the window

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        master.geometry('900x600') # size of the window
        master.resizable(True,True)        
        
        self.pack()
        self.createMenuBar()

    def createMenuBar(self):
        # the menu bar will be at the top of the window (root)
        self.menubar = tk.Menu(root)
        
        # creation of the options in the menu bar
        self.signalmenu = tk.Menu(self.menubar, tearoff=0)
        self.signalmenu.add_command(label="Info")
        self.signalmenu.add_command(label="Exit", command=root.quit)

        self.generatemenu = tk.Menu(self.menubar, tearoff=0)
        self.generatemenu.add_command(label="Pure tone")
        self.generatemenu.add_command(label="Free addition of pure tones")
        self.generatemenu.add_command(label="Known periodic signals")
        self.generatemenu.add_command(label="Noise")

        self.inputmenu = tk.Menu(self.menubar, tearoff=0)
        self.inputmenu.add_command(label="Load", command=self.loadAudioFile)
        self.inputmenu.add_command(label="Record")

        self.optionsmenu = tk.Menu(self.menubar, tearoff=0)
        self.optionsmenu.add_command(label="General")
        self.optionsmenu.add_command(label="Signal")
        self.optionsmenu.add_command(label="Spectrogram")

        # adding the options created to the menu bar
        self.menubar.add_cascade(label="Signal Visualizer", menu=self.signalmenu)
        self.menubar.add_cascade(label="Generate", menu=self.generatemenu)
        self.menubar.add_cascade(label="Input", menu=self.inputmenu)
        self.menubar.add_cascade(label="Options", menu=self.optionsmenu)

        root.config(menu=self.menubar)

    def loadAudioFile(self):
        # Open filename
        filename = tk.filedialog.askopenfilename(title = "Open file",filetypes = (("wav files","*.wav"),))
        # If no file has been selected
        if filename == '':
            return

        # Load audio data
        audioData = read(filename)
        audio = audioData[1]

        plt.plot(audio[0:1024])
        plt.ylabel("Amplitude")
        plt.xlabel("Time")
        plt.show()

app = Application(master=root)
app.mainloop()