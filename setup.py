from distutils.core import setup
import py2exe

Mydata_files = [('', ['setari.json']),
                ('', ['libiconv.dll']),
                 ('', ['libzbar-64.dll'])
                ]

setup(
    # pentru varianta cmd
    # console=['main.py'],
    
    # pentru varianta windows
    windows=['main.pyw'],
    data_files = Mydata_files,
    )
