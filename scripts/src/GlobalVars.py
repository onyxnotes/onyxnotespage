'''
Created on Mon Sep 12 12:16:51 PM CEST 2022

@file: GlobalVars.py

@author: Yoquec

@desc:
    Archivo que declara las variables globales a usar
    en OnyxConvert.py
'''
import os
from sys import platform
AVAILABLEPLATFORMS = ["linux", "linux2"]

# Carpeta HOME (solo funciona en Linux)
if platform in AVAILABLEPLATFORMS:
    HOME = os.environ["HOME"]
else:
    raise ImportError("Platform is not linux, could not import the home variable.")


# Check for the colorful module
try: 
    from termcolor import colored
    COLORFUL = True
except ImportError as ie:
    print(f"""The package `termcolor` is an optional dependency, \
which seems to not be installed in your system.
It's purpose is to provide colorful and more informative prints in the terminal

To install it, stop the script with CTRL-C and type:
\t>>> python3 -m pip install termcolor
""")
    COLORFUL = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~
# Onyx website variables
#~~~~~~~~~~~~~~~~~~~~~~~~~~
ONYXBASEURL = "https://onyxnotes.com"
ONYXCONTENTPREFIX = "content/en" # sin / al final para ser consistentes
# Carpeta de onyxnotes donde irán las imágenes
ONYXIMAGEFOLDER = "images/PastedImages"

#~~~~~~~~~~~~~~~~~~~~~~~~~~
# Other script variables
#~~~~~~~~~~~~~~~~~~~~~~~~~~
CHARSTOREMOVEIMG = ["!", "[", "]"]
