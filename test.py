# importing only those functions 
# which are needed 
from tkinter import *
from tkinter.ttk import *

# creating tkinter window 
root = Tk()

# Adding widgets to the root window 
Label(root, text='GeeksforGeeks', font=(
    'Verdana', 15)).grid(row=0, column=0, pady=10)

# Creating a photoimage object to use image 
photo = PhotoImage(file=r".\images\edit_test.png")
# Resizing image to fit on button
photoimage = photo.subsample(3, 3)

# here, image option is used to 
# set image on button 
Button(root, text='Click Me !', image=photoimage).grid(row=0, column=0)

mainloop()
