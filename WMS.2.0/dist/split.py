#!/usr/bin/env python3
""" Program pentru extragerea paginilor dintr-un pdf. Putem sa extragem fiecare pagina, pagina sau paginile pe care
dorim, fiecare in document separat sau in seturi de mai multe documente.
"""
import os
import sys
import PyPDF2
from PyPDF2 import PdfFileWriter
from subprocess import call
from time import sleep

# Alegem directorul in care lucram.
d = os.getcwd()
##################################################################################################################
try:
    pdf_input = input("Introduceti numele fisierului din care extragem foi.\n")
    pdfFile = pdf_input + '.pdf'
    pdfFileBase = pdfFile.replace('.pdf', '')
    # Deschidem fișierul pdf și numărăm câte pagini are.
    file = open(pdfFile, 'rb')
except IndexError:
    input('Nu exista niciun fișier pdf.')
    quit()


###################################################################################################################
def fiecare_pagina(file):
    """ Extragem fiecare pagina. """
    read_pdf = PyPDF2.PdfFileReader(file)
    total_pages = len(read_pdf.pages)
    for page in range(total_pages):
        write_pdf = PdfFileWriter()
        write_pdf.addPage(read_pdf.pages[page])
        # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul 
        # extras la urmă.
        with open('0' + str(page + 1) + '.pdf', 'wb') as f:
            write_pdf.write(f)
    # clear()
    main()
    return None


###################################################################################################################
def interval_de(file):
    """ Extragem un set de pagini. """
    write_pdf = PdfFileWriter()
    read_pdf = PyPDF2.PdfFileReader(file)
    # Aici se trece intervalul de pagini care se extrage, de la pana la.
    starts_with = input("Prima pagina:  ")
    ends_with = input("Ultima pagina:  ")
    page_num = int(starts_with) - 1
    pages = []
    while page_num <= int(ends_with) - 1:
        pages.append(page_num)
        page_num += 1
    for page_num in pages:
        write_pdf.addPage(read_pdf.pages[page_num])
        # Aici se scrie numele fișierului extras. Este indicat sa nu se modifice mai bine se redenumește fișierul 
        # extras la urma.
        with open('0' + str(starts_with) + '.pdf', 'wb') as f:
            write_pdf.write(f)
    # clear()
    main()
    return None


###################################################################################################################
def pagina_nr(file):
    """ Scriem numărul paginii sau paginilor dacă sunt mai multe. """
    read_pdf = PyPDF2.PdfFileReader(file)
    # Aici se trec(e) numărul paginii(lor) care se extrag(e).
    page_numbers = input('Introduceți numărul paginilor pe care doriți\nsă le extrageți, cu spațiu între ele: \n')
    page_list = page_numbers.split()
    for i in range(len(page_list)):
        page_list[i] = int(page_list[i])
    pages = [num - 1 for num in page_list]
    for page_num in pages:
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(read_pdf.pages[page_num])
        # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul 
        # extras la urmă.
        with open('0' + str(page_num + 1) + '.pdf', 'wb') as f:
            pdf_writer.write(f)
    # clear()
    main()
    return None


###################################################################################################################
def seturi_de(file):
    """ Documentul pdf se împarte în pagini egale de câte x. """
    read_pdf = PyPDF2.PdfFileReader(file)
    total_pages = len(read_pdf.pages)
    # Aici se trece intervalul de pagini care se extrage.
    set_of = int(input("Seturi de cate: "))
    number = total_pages % set_of
    if number != 0:
        print('Paginile nu se impart in mod egal.')
        main()
    pages = [num for num in range(set_of)]
    count = 0
    while count <= total_pages - set_of:
        pdf_writer = PdfFileWriter()
        for page_num in pages:
            pdf_writer.addPage(read_pdf.pages[page_num])
        # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul 
        # extras la urmă.
        with open('0' + str(pages[0] + 1) + '.pdf', 'wb') as f:
            pdf_writer.write(f)
        pages = [num + set_of for num in pages]
        count += set_of
    # clear()
    main()
    return None


###################################################################################################################
def seturi_de_la_pana_la(file):
    """ Se poate împărți în pagini de câte x începând de la și până la. """
    read_pdf = PyPDF2.PdfFileReader(file)
    # Aici se trece intervalul de pagini care se extrage.
    first_page = int(input("De la: "))
    last_page = int(input("Pana la: "))
    set_of = int(input("Seturi de cate: "))
    total_pages = (last_page - first_page) + 1
    number = total_pages % set_of
    if number != 0:
        print('Paginile nu se impart in mod egal.')
        sys.exit()
    pages = [num + (first_page - 1) for num in range(set_of)]
    count = 0
    while count <= total_pages - set_of:
        pdf_writer = PdfFileWriter()
        for page_num in pages:
            pdf_writer.addPage(read_pdf.pages[page_num])
        # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul
        # extras la urmă.
        with open('0' + str(pages[0] + 1) + '.pdf', 'wb') as f:
            pdf_writer.write(f)
            f.close()
        pages = [num + set_of for num in pages]
        count += set_of
    # clear()
    main()
    return None


###################################################################################################################
def select(rasp):
    """ Aici se selectează opțiunile. """
    if rasp == 1:
        print('---------------------------------------------')
        print('Ati selectat:\nFiecare pagina un document.')
        print('---------------------------------------------')
        fiecare_pagina(file)
    if rasp == 2:
        print('---------------------------------------------')
        print('Ati selectat:\nTot documentul in seturi de cate x.')
        print('---------------------------------------------')
        seturi_de(file)
    if rasp == 3:
        print('---------------------------------------------')
        print('Ati selectat:\nDoar paginile x y z.')
        print('---------------------------------------------')
        pagina_nr(file)
    if rasp == 4:
        print('---------------------------------------------')
        print('Ati selectat:\nPaginile de la pana la.')
        print('---------------------------------------------')
        interval_de(file)
    if rasp == 5:
        print('---------------------------------------------')
        print('Ati selectat:\nPaginile de la pana la in seturi de cate x.')
        print('---------------------------------------------')
        seturi_de_la_pana_la(file)
    if rasp == 6:
        print('---------------------------------------------')
        print('Ati selectat:\nTerminarea programului.')
        print('---------------------------------------------')
        input('Apăsați ENTER pentru terminare.')
        sys.exit()
    return None


###################################################################################################################
def main():
    """ Partea principală a programului, de aici pornește si aici se întoarce. """
    read_pdf = PyPDF2.PdfFileReader(file)
    total_pages = len(read_pdf.pages)
    i = 0
    while i < 1:
        print('---------------------------------------------')
        print('Program pentru despărțirea documentului \nîn mai multe pagini. Putem să scoatem:\n')
        print('1. Fiecare pagină un document.')
        print('2. Tot documentul în seturi de x pagini.')
        print('3. Doar paginile x y z.')
        print('4. Paginile de la până la.')
        print('5. Paginile de la până la în seturi de câte x.')
        print('6. Terminarea programului.')
        print('---------------------------------------------')
        print('Documentul are ' + str(total_pages) + ' pagini.\n---------------------------------------------')
        answer = int(input('Alegeți o cifră corespunzătoare\nunei operațiuni din lista de mai sus.\n-------------------'
                           '--------------------------\n'))
        lst = [1, 2, 3, 4, 5, 6]
        if answer not in lst:
            print('Nu ați ales nimic din listă.\nÎncercați din nou. \n')
            i = 0
        else:
            select(answer)
            break
    return None


###################################################################################################################
def clear():
    """ Ca să "curățim" ecranul după fiecare opțiune executată. """
    sleep(1)
    _ = call('clear' if os.name == 'posix' else 'cls')


###################################################################################################################
if __name__ == "__main__":
    main()
