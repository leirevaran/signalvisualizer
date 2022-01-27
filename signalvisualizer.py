from tkinter import *
import matplotlib.pyplot as plt

root = Tk() # creation of the window
root.title("Signal Visualizer") # name of the window
root.iconbitmap("images/icon.ico") # icon at the top of the window
root.geometry("630x571") # size of the window
#root.config(bg="blue") # change the background color of the window

frame = Frame(root) # create a frame son of the root
frame.pack() # pack the frame inside the root
frame.config(
    bg = "grey",
    width=630, height=571,
    cursor="hand2"
)

x = [1,2,3] # corresponding x axis values
y = [2,4,1] # corresponding y axis values

plt.plot(x, y) # plotting the points
 
plt.xlabel('x - axis') # naming the x axis
plt.ylabel('y - axis') # naming the y axis
plt.title('First graph') # giving a title to my graph

plt.show() # function to show the plot

button1=Button(frame,text='Hello')
button1.pack(side='bottom')

root.mainloop() # this line must always go at the bottom