#!/usr/bin/env python3

import ctypes
import datetime
import json
import os
import PIL.Image
import PyPDF2
import pytesseract
import shutil
import sys
import tempfile
from natsort import natsorted
from operator import itemgetter
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfReader
from pyzbar.pyzbar import decode
from time import sleep

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
        a = decode(Image.open(to_decode[j]))
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
    # Curatim ecranul.
    sleep(1)
    os.system('cls')
    main()
    
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
            final_doc_name = inv_name + '_AVIZ_0'
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
        print("Renaming " + pdf_files[i])
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
                        '''
                        if nume_final == "error":
                            nume_aviz = nume + "_AVIZ_0" + str(count) + ".pdf"
                            os.rename(path, nume_aviz)
                        '''
                        if '_AVIZ_0' in nume_final:
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
            shutil.move(file, rootDir() + '\\' + 'De_trimis')
    # Curatim ecranul.
    sleep(1)
    os.system('cls')
    main()

##################################### REDENUMIRE FACTURI EXTERNE ###########################################


def ocr_crop_box(box):
    # Alegem directorul in care lucram.
    d = rootDir() + '\\dist'
    # Creem o lista care sa contina toate fisierele jpg pe care le-am creat.
    img_files = [file for file in os.listdir(d) if file.endswith('.jpg')]
    img_files = natsorted(img_files)
    # Scoatem textul din imagine.
    for imgFile in img_files:
        image=Image.open(imgFile)
    # Scoatem textul din imagine.
        crop = image.crop(box)
        custom_config = r"--psm 6 --oem 3 -c tessedit_char_whitelist=('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ')"
        text = pytesseract.image_to_string(crop, config = custom_config)
    # Salvam textul extras din imagine in fisierul text 'str.txt'.
        with open('str.txt', 'a') as text_file:
            text_file.write(text)
            text_file.close()
            
def extern_main(name):
    # Creem o lista care sa contina toate fisierele cu extensia .pdf din folder.
    pdf_files = [file for file in os.listdir(rootDir()) if file.endswith('.pdf')]
    pdf_files = natsorted(pdf_files, key=itemgetter(1))

    pdfWriter = PyPDF2.PdfFileWriter()

    # Deschidem unul cate unul fiecare document .pdf din lista si extragem prima pagina.
    for pdfFile in pdf_files:
        filepath = rootDir() + '\\' + pdfFile
        with open(filepath, 'rb'):
            pdfReader = PyPDF2.PdfFileReader(filepath, strict=False)
            pdfWriter.addPage(pdfReader.getPage(0))
        
    # Creem un document pdf temporar care va contine toate paginile extrase anterior. 
    output_filename = ('_pdf_file.pdf')
    with open(output_filename, 'wb') as output:
        pdfWriter.write(output)
    
    # Transformam fisierul pdf astfel creat, in JPEG. Vor fi atatea imagini, cate pagini sunt in pdf.
    images = convert_from_path(output_filename, 500)
    for i, image in enumerate(images):
        fname = "image" + str(i) + ".jpg"
        image.save(fname, "JPEG")
    
    # Daca am apasat butonul DELL atunci le redenumim ca si DELL, daca am apasat HP, mergem pe HP.
    if name == "DELL":
        print('Renaming DELL\n##########\n' )
        # Sunt setarile pentru zona in care se scaneaza ( stanga, sus, dreapta, jos).
        box = (0, 1550, 5800, 1900)
    if name == "HP":
        print('Renaming HP\n##########\n' )
        # Sunt setarile pentru zona in care se scaneaza ( stanga, sus, dreapta, jos).
        box = (900, 1550, 2900, 2000)
    
    ocr_crop_box(box)
    
    # Extragem liniile care contin nr. factura si nr. order. 
    with open('str.txt', 'r') as f:
        linie = [line for line in f if 'Customer No' in line]
    # Si le scriem intr-un fisier nou dupa care stergem primul fisier.
    with open('nume.txt', 'w') as f:
        for item in linie:
            f.write("%s" % item)
    # Liniile de mai jos sunt pentru cazul in care s-a scanat gresit si au aparut hieroglife in loc de cifre. 
    removetable = str.maketrans('','','|')
    out_list = [s.translate(removetable) for s in open('nume.txt')]
    # Asamblam numele final al documentului si facem o lista care contine aceste nume.
    docName = [line.split() for line in out_list]
    with open('numeFinal.txt', 'w') as finalName:
        for item in range(len(docName)):
            finalName.write('DELL_' + docName[item][2] + '_' + docName[item][9] + '.pdf\n')
    # Stergem fisierul _pdf_file.pdf. Daca nu il stergem acum, atunci va fi primul fisier pdf redenumit si ne da peste cap tot programul. 
    os.remove('_pdf_file.pdf')
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
                d = rootDir() + '\\dist'
                for file in os.listdir(d):
                    if file.endswith('.pdf'):
                        shutil.move(file, rootDir() + '\\De_trimis')
                pdfCount += 1
    
    # Alegem directorul in care lucram.
    d = rootDir() + '\\dist'
    # Stergem fisierul numeFinal.txt.
    os.remove('numeFinal.txt')
    # Stergem fisierul nume.txt.
    os.remove('nume.txt')
    # Stergem fisierul str.txt.
    os.remove('str.txt')
    # Stergem imaginile .jpg.
    img_files = [file for file in os.listdir(d) if file.endswith('.jpg')]
    for file in img_files:
        os.remove(file)
    # Curatim ecranul.
    sleep(1)
    os.system('cls')
    main()

######################################## PROGRAMUL PRINCIPAL ###############################################   



def main():
    print('-------------------------------------------------')
    message = input(' 1. Split\n 2. Rename\n 3. DELL\n 4. HP\n 5. Exit\n-------------------------------------------------\n')
    
    if message == '1':
        print('Splitting document.')
        split_main()

    if message == '2':
        redenumire_main()

    if message == '3':
        extern_main('DELL')

    if message == '4':
        extern_main('HP')

    if message == '5':
        sys.exit()

if __name__ == "__main__":
    main()
