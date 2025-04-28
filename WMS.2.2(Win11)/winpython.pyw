import functii
from tkinter import *
from tkinter import messagebox
from tkinter.simpledialog import askstring
from time import sleep

master = Tk()
master.geometry("200x180")  # Size of the window 
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
    #functii.mutare('IN')
    functii.redenumire_main(eFactura=False)
    #functii.mutare('OUT')
    sleep(1)
    message()


def extract():
    #functii.mutare('IN')
    functii.split_main()
    functii.redenumire_main(eFactura=False)
    #functii.mutare('OUT')
    sleep(1)
    message()


def efactura():
    #functii.mutare('IN')
    functii.split_main()
    functii.rotate()
    functii.redenumire_main(eFactura=True)
    #functii.mutare('OUT')
    sleep(1)
    message()


def dell():
    #functii.mutare('IN')
    functii.split_main()
    functii.extern_main('DELL')
    #functii.mutare('OUT')
    sleep(1)
    message()


def hp():
    #functii.mutare('IN')
    functii.split_main()
    functii.extern_main('HP')
    #functii.mutare('OUT')
    sleep(1)
    message()


def split():
    #functii.mutare('IN')
    functii.split_main()
    #functii.mutare('OUT')
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

def codeReader():
    val = askstring("Value", "Cate caractere are codul de bare?")
    functii.scanare_coduri_de_bara(val)
    sleep(1)
    message()

# this will create button widgets and  put them in position
dell_button = Button(master, text="DELL", height=2, width=10, command=dell)
dell_button.place(x=10, y=10)

hp_button = Button(master, text="HP", height=2, width=10, command=hp)
hp_button.place(x=105, y=10)

efactura_button = Button(master, text='E-Factura', height=2, width=10, command=efactura)
efactura_button.place(x=10, y=120)

manual_extract_button = Button(master, text='Redenumire\nMulte facturi', height=2, width=10, command=extract)
manual_extract_button.place(x=105, y=60)

rename_button = Button(master, text="Redenumire\nO factura", height=2, width=10, command=redenum)
rename_button.place(x=10, y=60)

# extract_button = Button(master, text="Split", height=2, width=8, command=lambda:my_open())
# extract_button.place(x=115, y=60)

# efactura_button = Button(master, text='Barcode\nscanner', height=2, width=8, command=codeReader)
# efactura_button.place(x=115, y=120)

exit_button = Button(master, text="Iesire", height=2, width=10, command=master.destroy)
exit_button.place(x=105, y=120)


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
    b7.place(x=68, y=170)

    b8 = Button(child, text='Iesire', command=master.destroy)
    b8.place(x=145, y=200) 

    b9 = Button(child, text='Inapoi', command=child.destroy)
    b9.place(x=20, y=200)
master.mainloop()
