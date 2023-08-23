import functii
from tkinter import *
from tkinter import messagebox
from time import sleep

master = Tk()
master.geometry("200x220")  # Size of the window 
master.title("")  # Adding a title
master.resizable(False, False)
master.eval('tk::PlaceWindow . center')

"""
Daca este nevoie de ceva text, se scoate comment-ul.
Label
var = StringVar()
var.set("Redenumire facturi" + "\n" + "scanate")
label = Label(master, textvariable=var, font=("Helvetica", 14), justify='center')
label.pack(padx=10, pady=15, side=TOP)
"""

#functions
def message():
    messagebox.showinfo(title="Terminare", message="Am terminat")


def redenum():
    functii.redenumire_main()
    sleep(1)
    message()


def extract():
    functii.split_main()
    functii.redenumire_main()
    sleep(1)
    message()


def dell():
    functii.split_main()
    functii.extern_main('DELL')
    sleep(1)
    message()


def hp():
    functii.split_main()
    functii.extern_main('HP')
    sleep(1)
    message()


def split():
    functii.split_main()
    sleep(1)
    message()


def every_pages():
    functii.fiecare_pagina()
    sleep(1)
    message()


def set_of():
    functii.seturi_de()
    sleep(1)
    message()


def pages():
    functii.pagina_nr()
    sleep(1)
    message()


def interval():
    functii.interval_de()
    sleep(1)
    message()


def sets_from():
    functii.seturi_de_la_pana_la()
    sleep(1)
    message()


def merge():
    functii.merge()
    sleep(1)
    message()

# this will create button widgets and  put them in position
dell_button = Button(master, text="DELL", height=2, width=7, command=dell)
dell_button.place(x=20, y=10)

hp_button = Button(master, text="HP", height=2, width=7, command=hp)
hp_button.place(x=20, y=60)

manual_extract_button = Button(master, text='Bulk\n rename', height=2, width=7, command=extract)
manual_extract_button.place(x=20, y=120)

rename_button = Button(master, text="Rename", height=2, width=8, command=redenum)
rename_button.place(x=115, y=10)

extract_button = Button(master, text="Split", height=2, width=8, command=lambda:my_open())
extract_button.place(x=115, y=60)

exit_button = Button(master, text="Iesire", height=2, width=8, command=master.destroy)
exit_button.place(x=115, y=120)


def my_open():
    child=Toplevel(master) # Child window 
    child.title("SplitPDF")
    child.transient(master) # set to be on top of the main window
    child.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
    child.resizable(False, False)
    x = master.winfo_rootx()
    y = master.winfo_rooty()
    geom = "+%d+%d" % (x,y)
    dimension = "200x230" + geom
    child.geometry(dimension)
    
    my_str1 = StringVar()
    l1 = Label(child,  textvariable=my_str1 )
    my_str1.set("")
    
    b1 = Button(child, text='Split\nfacturi', height=2, width=8, command=split)
    b1.place(x=20, y=10)

    b2 = Button(child, text='Fiecare\npagina', height=2, width=8, command=every_pages)
    b2.place(x=20, y=60)

    b3 = Button(child, text='Seturi de', height=2, width=8, command=set_of)
    b3.place(x=20, y=110)

    b4 = Button(child, text='Doar\npaginile', height=2, width=8, command=pages)
    b4.place(x=120, y=10)

    b5 = Button(child, text='De la\npana la', height=2, width=8, command=interval)
    b5.place(x=120, y=60)

    b6 = Button(child, text='De la\npana la\nin seturi de', height=3, width=9, command=sets_from)
    b6.place(x=113, y=105)

    b7 = Button(child, text='Lipire\ndocumente', height=3, width=9, command=merge)
    b7.place(x=65, y=170)

    b8 = Button(child, text='Iesire', command=master.destroy)
    b8.place(x=145, y=170) 

    b9 = Button(child, text='Inapoi', command=child.destroy)
    b9.place(x=20, y=170)
master.mainloop()
