import tkinter as tk
import csv
from pathlib import Path
from matplotlib.widgets import Button
from scipy.io.wavfile import write

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Auxiliar():

    ##########################################################################
    # CALLED FROM SIGNAL VISUALIZER AND GENERATE FREE ADDITION OF PURE TONES #
    ##########################################################################
    
    # Calculates the width and height of the window depending on the screen size of the computer
    # Position the main window in the middle of the screen if 'middle' is True
    def windowGeometry(self, window, w, h, middle):
        ws0 = 1920 # common width of the screen
        hs0 = 1080 # common height of the screen
        # get screen width and height
        ws = window.winfo_screenwidth() # width of the screen
        hs = window.winfo_screenheight() # height of the screen
        # calculate window width and height
        new_w = int(ws * w / ws0) # adapt the widhth to the screen
        new_h = int(hs * h / hs0) # adapt the height to the screen
        # calculate x and y coordinates for the main window
        x = (ws/2) - (new_w/2)
        y = (hs/2) - (new_h/2)
        if middle: window.geometry('%dx%d+%d+%d' % (new_w, new_h, x, y))
        else: window.geometry('%dx%d' % (new_w, new_h))
        window.deiconify()


    #################################################
    # CALLED FROM CONTROL MENU AND GENERATE MODULES #
    #################################################

    # Called when inserting something in an entry. Only lets the user enter integers or floats. It does not allow leaving the entry empty.
    def onValidate(self, S, s, d):
        if S.isdigit() and d == "0": # if the user is deleting the last remaining digit
            if len(s) == 2:
                for i in s:
                    if i == '.':
                        return False
                return True
            elif len(s) == 1:
                return False
            else:
                return True
        if S == "." and d == "1": # if the user is inserting a dot
            for i in s:
                if i == '.': # if there is already a dot
                    return False
            return True
        # if the user is inserting or deleting a digit (which is not the last one) or deleting a dot
        if S.isdigit() or (S == "." and d == "0"): 
            return True
        return False
    
    # Called when inserting something in the entry of fs. Only lets the user enter numbers.
    def onValidateInt(self, S):
        if S.isdigit():
            return True
        return False
    

    ################################
    # CALLED FROM GENERATE MODULES #
    ################################
    
    # Shows a warning if the frequency is greater than or equal to fs/2
    def bigFrequency(self, freq, fs):
        if freq >= fs/2:
            tk.messagebox.showwarning(title="Big frequency", message="The frequency is greater than or equal to half the value of the sample frequency ("+str(fs/2)+" Hz).") # show warning
    
    def readFromCsv(self):
        file = 'csv/atributes.csv'
        list = []
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                list.append(row)
        return list
    
    def saveDefaultAsCsv(self, list):
        file = 'csv/atributes.csv'
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(list)


    ############################
    # CALLED FROM CONTROL MENU #
    ############################
    
    # Used for saving a waveform as a wav or csv file
    def saveasWavCsv(self, cm, fig, x, y, dist, fs):
        def save(event):
            file = tk.filedialog.asksaveasfilename(title='Save', defaultextension=".wav", filetypes=(("wav files","*.wav"),("csv files","*.csv"),))
            if file is None or file == '':
                return
            if file.endswith('wav'):
                self.fileName = Path(file).stem # take only the name of the file without the '.wav' and the path
                cm.title(self.fileName) # update the name of the window
                write(file, fs, y) # generates a wav file in the selected folder
            elif file.endswith('.csv'):
                with open(file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["x", "y"])
                    for i in range(len(x)):
                        writer.writerow([x[i], y[i]])

        # Adds a 'Save' button to the figure
        axsave = fig.add_axes([0.91, dist, 0.05, 0.04]) # [left, bottom, width, height]
        but_save = Button(axsave, 'Save')
        but_save.on_clicked(save)
        axsave._but_save = but_save # reference to the Button (otherwise the button does nothing)

    # Save the values of 'x' and 'y' axis of a plot as a csv file
    def saveasCsv(self, fig, x, y, dist, opt):
        def save(event):
            file = tk.filedialog.asksaveasfilename(title='Save', defaultextension=".csv", filetypes=(("csv files","*.csv"),))
            if file is None or file == '':
                return
            with open(file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["x", "y"])
                for i in range(len(x)):
                    if opt == 'SC':
                        writer.writerow([x[i], y[i][0]])
                    else:
                        writer.writerow([x[i], y[i]])

        # Adds a 'Save' button to the figure
        axsave = fig.add_axes([0.91, dist, 0.05, 0.04]) # [left, bottom, width, height]
        but_save = Button(axsave, 'Save')
        but_save.on_clicked(save)
        axsave._but_save = but_save # reference to the Button (otherwise the button does nothing)