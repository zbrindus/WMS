#!/usr/bin/env python3

import ctypes
import datetime
import json
import os
import PIL.Image
import PyPDF2
import pytesseract
import re
import shutil
import sys
import tempfile
from natsort import natsorted
from operator import itemgetter
from pdf2image import convert_from_path, convert_from_bytes
from PyPDF2 import PdfFileWriter, PdfReader, PdfFileMerger
from PIL import ImageFilter
from pyzbar.pyzbar import decode
from time import sleep
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo

######################################## DIRECTORUL DE LUCRU ##############################################


def rootDir():
    # Directorul de lucru.
    if getattr(sys, 'frozen', False):
        # The application is frozen
        root_dir = os.path.realpath(os.path.join(os.path.dirname(sys.executable), '..'))
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        root_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    return root_dir

############################################# DESPARTIREA PE FACTURI #######################################


def split_main():
    d = rootDir() + '\\dist'
    # Aflam anul. Vom avea nevoie de el la imaprtirea paginilor, cand cautam in codul de bare.
    today  = datetime.date.today()
    year = today.year
    
    # Deschidem fișierul pdf.
    for file in os.listdir(rootDir()):
        if file.endswith('.pdf'):
            pdf_file = rootDir() + '\\' + file
    pdf_file_base = pdf_file.replace('.pdf', '')
    # Declarăm scriitorul și cititorul de pdf.
    reader = PdfReader(pdf_file)

    # Numărul total de pagini din pdf.
    number_of_pages = len(reader.pages)

    # Transformăm paginile în imagini individuale.
    with tempfile.NamedTemporaryFile(mode='wb'):
        img_file = convert_from_path(pdf_file)
        for i in range(len(img_file)):
            img_file[i].save('image' + str(i) + '.jpg')

    # Aranjăm paginile în ordine alfabetică, ca nu cumva după 1 să vină 10.
    dec = [imgFile for imgFile in os.listdir(d) if imgFile.endswith('.jpg')]
    to_decode = natsorted(dec)
    
    # Facem o listă cu imaginile care au un cod de bare care începe cu anul in curs. Acestea vor fi prima pagină din pdf.
    first_page = []
    for j in range(len(to_decode)):
        a = decode(PIL.Image.open(to_decode[j]))
        # print(a)
        if len(a) > 0:
            if len(a) == 2:
                barcode = a[1][0]
                sample = barcode[0:4].decode('utf-8')
                if sample == str(year):
                    first_page.append(j)
                else:
                    barcode = a[0][0]
                    sample = barcode[0:4].decode('utf-8')
                    if sample == str(year):
                        first_page.append(j)
            else:
                barcode = a[0][0]
                sample = barcode[0:4].decode('utf-8')
                if sample == str(year):
                    first_page.append(j)

    # Și adăugăm numărul total de pagini..
    first_page.append(number_of_pages)

    # Aflăm care va fi ultima pagină la fiecare primă pagină.
    last_pages = [first_page[i+1] - 1 for i in range(len(first_page)-1)]

    # Extragem paginile.
    for n in range(len(last_pages)):
        writer = PdfFileWriter()
        add_page = []
        page_nr = first_page[n]
        while page_nr <= last_pages[n]:
            add_page.append(page_nr)
            page_nr += 1
        for page_num in add_page:
            writer.addPage(reader.pages[page_num])
            # Aici se scrie numele fișierului extras. Este indicat sa nu se modifice
            # mai bine se redenumește fișierul extras la urma.
            with open('{0}_page_0'.format(pdf_file_base) + str(page_nr) + '.pdf', 'wb') as f:
                writer.write(f)
   
    # Ștergem imaginile JPG.
    for imgFile in os.listdir(d):
        if imgFile.endswith('.jpg'):
            os.remove(imgFile)
    # Stergem pdf-ul initial.
    os.remove(pdf_file)
    
############################################# REDENUMIRE FACTURI ###########################################


def redenumire(elem, new_dict, img_to_ocr):
    # Din elementele extrase referitoare la furnizor, intâi facem un dicționar,
    # după care îl transformăm în listă. Din această listă vom scoate elementele de care vom avea nevoie.
    new_dictionary = new_dict[0]
    my_list = [i for i in new_dictionary.values()]
    inv_line = ''.join(my_list[0])
    inv_split = ''.join(my_list[1])
    inv_num = 'doc_number' + ''.join(my_list[2])
    inv_name = ''.join(my_list[3])
    img_crop = eval(''.join(my_list[4]))
    # Facem inca un ocr la imaginea documentului dar cu setarile noi si salvam textul intr-un fisier temporar.
    ocr_file = img_to_ocr.crop(img_crop)
    # ocr_file.save('SALVAT.JPG', 'JPEG') # ca sa vedem ce imagine avem.
    ocr_config = r"--psm 6 --oem 3 -c tessedit_char_whitelist=('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ')"
    text = pytesseract.image_to_string(ocr_file, config=ocr_config)
    with open('.temp.txt', 'w') as myFile:
        myFile.write(text)
    if elem == '':
        pass
    else:
        try:
            # Deschidem fisierul temporar, cautam dupa numarul facturii si asamblam denumirea noua a facturii.
            with open('.temp.txt', 'r') as readTemporaryFile:
                linie = [rand for rand in readTemporaryFile if inv_line in rand]
                # print(linie)
                doc_number = [item.strip().split(inv_split) for item in linie]
                final_doc_number = eval(inv_num)
                number = final_doc_number.split()
                final_doc_name = inv_name + str(number[0]) + '.pdf'
        except IndexError:
            # final_doc_name = 'error'
            final_doc_name = inv_name + 'AVIZ_0'
        return final_doc_name


def redenumire_main():
    # Alegem directorul în care lucrăm.
    d = os.getcwd()
    # Deschidem fișierul json.
    with open('setari.json') as json_file:
        data = json.load(json_file)
    # Facem o listă a furnizorilor pe care le-am scos din fișierul JSON.
    furnizori = list(data.keys())
    # In Windows trebuie sa aratam calea catre Tesseract. In Linux se comenteaza linia de mai jos.
    # pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    # Creăm o listă care conține toate fișierele cu extensia .pdf din folder.
    pdf_files = [pdfFile for pdfFile in os.listdir(rootDir()) if pdfFile.endswith('.pdf')]
    # Deschidem unul câte unul fiecare document .pdf din listă și extragem prima pagină.
    for i in range(len(pdf_files)):
        count = i
        path = rootDir() + '\\' + pdf_files[i]
        # print("Renaming " + pdf_files[i])
        with tempfile.NamedTemporaryFile(mode='wb'):
            images_from_path = convert_from_path(path)
            # Decupăm porțiunea de sus a facturii unde pot fi numele furnizorului și nr. de factură.
            crop_box = (0, 0, 1900, 970)
            img_file = images_from_path[0].crop(crop_box)
            # Transformăm imaginea în text.
            ocr_config = r"--psm 6 --oem 3 -c tessedit_char_whitelist=('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ')"
            text = pytesseract.image_to_string(img_file, config=ocr_config)
            # Căutăm dacă vreun nume de furnizor din lista furnizorilor se găsește în textul scanat.
            # Dacă da, atunci începem redenumirea fișierelor.
            for nume in furnizori:
                if nume in text.upper():
                    # Din fișierul json scoatem elementele care se referă la acest furnizor și care ne ajută
                    # să redenumim fișierul pdf.
                    date = data[nume]
                    # Redenumim pdf-urile unul câte unul.
                    nume_final = redenumire(nume, date, img_file)
                    try:
                        if 'AVIZ_0' in nume_final:
                            nume_aviz = nume_final + str(count) + ".pdf"
                            os.rename(path, nume_aviz)
                        else:
                            os.rename(path, nume_final)
                    except FileNotFoundError:
                        pass
                    # Ștergem fișierul temporar.
                    sleep(1.5)
                    os.remove('.temp.txt')
    # print("Finished.")
    for file in os.listdir(d):
        if file.endswith('.pdf'):
            # shutil.move(file, rootDir() + '\\' + 'De_trimis')
            shutil.move(file, rootDir())

##################################### REDENUMIRE FACTURI DELL SI HP ###########################################


def extern_main(name):

    if name == "DELL":
        box = (0, 0, 1900, 970)
        psm = r'--psm 6'
        invoice_no = r"Invoice No\s*(\d*)"
        order_no = r"Order No\s*(\d*)"
    
    if name == "HP":
        box = (0, 0, 1900, 970)
        psm = r'--psm 6'
        searchTerm = '90'

    count = 0
    lstLine = []
    pdf_files = [pdfFile for pdfFile in os.listdir(rootDir()) if pdfFile.endswith('.pdf')]
    # Deschidem unul câte unul fiecare document .pdf din listă și extragem prima pagină.
    for i in range(len(pdf_files)):
        count += 1
        rename = "DELL_" + str(count)
        path = rootDir() + '\\' + pdf_files[i]
        # print("Renaming " + pdf_files[i])
        with tempfile.NamedTemporaryFile(mode='wb'):
            images_from_path = convert_from_path(path)
            # Decupăm porțiunea de sus a facturii unde pot fi numele furnizorului și nr. de factură.
            cropped_img_file = images_from_path[0].crop(box)
            img_file = cropped_img_file.filter(ImageFilter.MedianFilter)
            img_file.point( lambda p: 255 if p > 123 else 0 )
            # Transformăm imaginea în text.
            conf = r" --oem 3 -c tessedit_char_whitelist=('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ')"
            ocr_config = psm + conf
            text = pytesseract.image_to_string(img_file, config=ocr_config)
            
            if name == "DELL":
                Invoice = re.findall(invoice_no, str(text))
                Order = re.findall(order_no, str(text))

                invoice_No = [invoice for invoice in Invoice]
                order_No = [order for order in Order]

                for invoice in invoice_No:
                    for order in order_No:
                        searchterm = "DELL_" + str(invoice) + "_" + str(order)

                # Salvam textul extras din imagine in fisierul text 'str.txt'.
                # Daca nu se gaseste nr. de Invoice, atunci numele va fi DELL si nr. de ordine al facturii.
                if len(invoice_No) == 0:
                    lstLine.append(rename)
                # Daca nu se gaseste nr. de Order, atunci numele va fi DELL si nr. de ordine al facturii.
                elif len(order_No) == 0:
                    lstLine.append(rename)
                else:
                    lstLine.append(searchterm)

    with open('numeFinal.txt', 'w') as finalName:
        for nr, item in enumerate(lstLine):
            if name == "DELL":
                finalName.write(item + '.pdf\n')
            if name == "HP":
                finalName.write('HP_' + docName[item][0] + '.pdf\n')
    # Stergem fisierul _pdf_file.pdf. Daca nu il stergem acum, atunci va fi primul fisier pdf redenumit si ne da peste cap tot programul. 
    # os.remove('_pdf_file.pdf')
    # Redenumim fisierele.
    pdfCount = 0
    with open('numeFinal.txt') as finalName:
        lines = finalName.readlines()
        lines = [line.rstrip() for line in lines]
        for file in os.listdir(rootDir()):
            if file.endswith('.pdf'):
                filepath = rootDir() + '\\' + file
                os.rename(filepath, lines[pdfCount])
                # Alegem directorul in care lucram.
                d = rootDir() + "\\dist"
                for file in os.listdir(d):
                    if file.endswith('.pdf'):
                        # shutil.move(file, rootDir() + '\\De_trimis')
                        shutil.move(file, rootDir())
                pdfCount += 1

    # Alegem directorul in care lucram.
    d = rootDir() + "\\dist"
    # Stergem fisierul numeFinal.txt.
    os.remove('numeFinal.txt')
    # Stergem fisierul nume.txt.
    # os.remove('nume.txt')
    # Stergem fisierul str.txt.
    # os.remove('str.txt')
    # Stergem imaginile .jpg.
    img_files = [file for file in os.listdir(d) if file.endswith('.jpg')]
    for file in img_files:
        os.remove(file)

##################################### EXTRAGERE FIECARE PAGINA ###########################################


def fiecare_pagina():
    # Deschidem fișierul pdf.
    for file in os.listdir(rootDir()):
        if file.endswith('.pdf'):
            pdf_file = rootDir() + '\\' + file
    pdf_file_base = pdf_file.replace('.pdf', '')
    # Declarăm scriitorul și cititorul de pdf.
    reader = PdfReader(pdf_file)
    
    # Numărul total de pagini din pdf.
    number_of_pages = len(reader.pages)
    
    for page in range(number_of_pages):
        write_pdf = PdfFileWriter()
        write_pdf.addPage(reader.pages[page])
        # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul 
        # extras la urmă.
        with open(os.path.join(os.pardir, '0' + str(page + 1) + '.pdf'), 'wb') as f:
            write_pdf.write(f)

##################################### IMPARTIRE DOCUMENT IN SETURI DE CATE ####################################


def seturi_de():
    """ Documentul pdf se împarte în pagini egale de câte x. """
    # Deschidem fișierul pdf.
    for file in os.listdir(rootDir()):
        if file.endswith('.pdf'):
            pdf_file = rootDir() + '\\' + file
    pdf_file_base = pdf_file.replace('.pdf', '')
    # Cate pagini are documentul.
    read_pdf = PdfReader(pdf_file)
    total_pages = len(read_pdf.pages)
    # Intervalul la care se pot imparti paginile.
    set_of = [st for st in range(1, total_pages + 1) if (total_pages % st == 0) and (st > 1)]
    string1 = 'Sunt in total ' + str(total_pages) + ' pagini.\n'
    string2 = 'Se poate imparti in ' + ', '.join(str(elem) for elem in set_of) + ' pagini egale.\n'
    name = askstring('Info', string1 + '\n' + string2)
    if int(name) in set_of:
        showinfo('Info', 'Se imparte\n in {}'.format(name) + ' seturi.\n')
        pages = [num for num in range(int(name))]
        count = 0
        while count <= total_pages - int(name):
            pdf_writer = PdfFileWriter()
            for page_num in pages:
                pdf_writer.addPage(read_pdf.pages[page_num])
            # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul 
            # extras la urmă.
            with open(os.path.join(os.pardir, '0' + str(pages[0] + 1) + '.pdf'), 'wb') as f:
                pdf_writer.write(f)
            pages = [num + int(name) for num in pages]
            count += int(name)
    else:
        showinfo('Info', 'Nu se poate imparti\n in {}'.format(name) + ' seturi.\n')

##################################### EXTRAGE PAGINILE X, Y, Z ####################################


def pagina_nr():
    """ Extragem doar anumite pagini, poate sa fie aleator. """
    # Deschidem fișierul pdf.
    for file in os.listdir(rootDir()):
        if file.endswith('.pdf'):
            pdf_file = rootDir() + '\\' + file
    pdf_file_base = pdf_file.replace('.pdf', '')
    # Cate pagini are documentul.
    read_pdf = PdfReader(pdf_file)
    total_pages = len(read_pdf.pages)
    # Aici se trec(e) numărul paginii(lor) care se extrag(e).
    string1 = 'Sunt in total ' + str(total_pages) + ' pagini.\n'
    string2 = 'Numărul paginilor pe care\nle extragem, cu spațiu între ele: \n'
    page_numbers = askstring('Info', string1 + '\n' + string2)
    page_list = page_numbers.split()
    for i in range(len(page_list)):
        page_list[i] = int(page_list[i])
    pages = [num - 1 for num in page_list]
    for page_num in pages:
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(read_pdf.pages[page_num])
        # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul 
        # extras la urmă.
        with open(os.path.join(os.pardir, '0' + str(page_num + 1) + '.pdf'), 'wb') as f:
            pdf_writer.write(f)

###################################### EXTRAGE PAGINILE DE LA X PANA LA Y ###############################


def interval_de():
    """ Extragem un set de pagini. """
    # Deschidem fișierul pdf.
    for file in os.listdir(rootDir()):
        if file.endswith('.pdf'):
            pdf_file = rootDir() + '\\' + file
    pdf_file_base = pdf_file.replace('.pdf', '')
    write_pdf = PdfFileWriter()
    read_pdf = PdfReader(pdf_file)
    # Cate pagini are documentul.
    total_pages = len(read_pdf.pages)
    # Aici se trece intervalul de pagini care se extrage, de la pana la.
    string1 = 'Sunt in total ' + str(total_pages) + ' pagini.\n'
    string2 = 'De la pagina, pana la pagina\ncu spațiu între ele: \n'
    page_numbers = askstring('Info', string1 + '\n' + string2)
    page_list = page_numbers.split()
    page_num = int(page_list[0]) - 1
    pages = []
    while page_num <= int(page_list[1]) - 1:
        pages.append(page_num)
        page_num += 1
    for page_num in pages:
        write_pdf.addPage(read_pdf.pages[page_num])
        # Aici se scrie numele fișierului extras. Este indicat sa nu se modifice mai bine se redenumește fișierul 
        # extras la urma.
        with open(os.path.join(os.pardir, '0' + str(page_list[0]) + '.pdf'), 'wb') as f:
            write_pdf.write(f)

############################### IMPARTIRE DOCUMENT IN SETURI DE CATE X INCEPAND DE LA POZITIA Y ###############


def seturi_de_la_pana_la():
    """ Se poate împărți în pagini de câte x începând de la și până la. """
    # Deschidem fișierul pdf.
    for file in os.listdir(rootDir()):
        if file.endswith('.pdf'):
            pdf_file = rootDir() + '\\' + file
    pdf_file_base = pdf_file.replace('.pdf', '')
    read_pdf = PdfReader(pdf_file)
    # Cate pagini are documentul.
    total_pages = len(read_pdf.pages)
    # Aici se trece intervalul de pagini care se extrage.
    string1 = 'Sunt in total ' + str(total_pages) + ' pagini.\n'
    string2 = 'De la pagina, pana la pagina\nin seturi de cate\ncu spațiu între ele: \n'
    page_numbers = askstring('Info', string1 + '\n' + string2)
    page_list = page_numbers.split()
    first_page = int(page_list[0])
    last_page = int(page_list[1])
    set_of = int(page_list[2])
    total_pages = (last_page - first_page) + 1
    number = total_pages % set_of
    if number != 0:
        messagebox.showerror("Eroare", "Paginile nu se impart in mod egal.")
        sys.exit()
    pages = [num + (first_page - 1) for num in range(set_of)]
    count = 0
    while count <= total_pages - set_of:
        pdf_writer = PdfFileWriter()
        for page_num in pages:
            pdf_writer.addPage(read_pdf.pages[page_num])
        # Aici se scrie numele fișierului extras. Este indicat să nu se modifice mai bine se redenumește fișierul
        # extras la urmă.
        with open(os.path.join(os.pardir, '0' + str(pages[0] + 1) + '.pdf'), 'wb') as f:
            pdf_writer.write(f)
            f.close()
        pages = [num + set_of for num in pages]
        count += set_of

######################################### LIPIRE PAGINI ######################################################


def merge():
    """ Facem un singur document din foile pdf aflate in director. """
    # Facem o lista cu documentele pdf din director.
    x = [a for a in os.listdir(rootDir()) if a.endswith(".pdf")]
    # Facem un singur document din lista de mai sus.
    merger = PdfFileMerger()
    for pdf in x:
        merger.append(open(os.path.join(os.pardir, pdf), 'rb'))
    # Scriem fisierul creat in director.
    with open(os.path.join(os.pardir, "result.pdf"), "wb") as fout:
        merger.write(fout)
