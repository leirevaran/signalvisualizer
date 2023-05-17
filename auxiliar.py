import tkinter as tk
import csv

# To avoid blurry fonts
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class Auxiliar():

    # Calculates the width and height of the window depending on the screen size of the computer
    def windowGeometry(self, window, x, y):
        normal_w = 1920
        normal_h = 1080
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window_w = int(w * x / normal_w)
        window_h = int(h * y / normal_h)
        window.geometry('%dx%d' % (window_w, window_h))

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
    
    # Shows a warning if the frequency is greater than or equal to fs/2
    def bigFrequency(self, freq, fs):
        if freq >= fs/2:
            tk.messagebox.showwarning(title="Big frequency", message="The frequency is greater than or equal to half the value of the sample frequency ("+str(fs/2)+" Hz).") # show warning