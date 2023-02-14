# WMS
Pentru scanat facturile la lucru

Ca sa functioneze programul:
	Trebuie instalat:
	1. Tesseract
	2. Poppler
	3. In Environment Variables in PATH (atat la User cat si la System)
		C:\Program Files\poppler-22.04.0\Library\bin
		C:\Program Files\Tesseract-OCR\
	
	Programele Tesseract si Poppler, sunt in folderul "Requirements". Sa le copiezi de acolo in C:\Program Files.

######################
Daca sunt probleme la scanare sau daca vrei sa adaugi o firma:
	Se editeaza "setari.json" din folderul "dist", dar cel mai bine este sa folosesti programul python "setariJSON.py" din directorul "bin\find" si sa adaugi schimbarile in "setari.json".

######################
Daca vrei sa editezi programul:
	Se poate edita din folderul "bin", programul "main.py". Dupa ce s-au facut editarile si testarile, se compileaza programul cu comanda "python setup.py py2exe".
	Pentru editare, pe langa python 3.11, trebuie sa fie instalate modulele din "requirements.txt" aflat tot in folderul "bin".

######################
Daca la pornirea programului apare mesajul:
	1. VCRUMTIME140.DLL is missing, trebuie instalat vc_redist.x64.exe din folderul Requirements\VCRedist.
	2. Could not find module "libzbar-64.dll", trebuie instalat vcredist_x64.exe din folderul Requirements\VCRedist.
	
