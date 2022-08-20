'''
Created on Sat Aug 20 09:17:24 PM CEST 2022

@file: UniNotesConvert.py

@author: Yoquec, Roliver

@desc:
    Archivo que se encargará de convertir los apuntes que tenemos
    de UniNotes a Onyx con el formato necesario para HUGO.

@License:
    MIT License

    Copyright (c) 2022 Alvaro Viejo

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
--------------------------------------------------------------------

Funcionamiento:
    El script necesitará que se especifique un apunte con la path 
    completa (desde ~/) al archivo o carpeta que se quiera convertir
'''

'''
LIBRERÍAS
--------------------------------------------------------------------
'''
import os
import sys
import argparse
from typing import Tuple

try: 
    from termcolor import colored
    COLORFUL = True
except ImportError as ie:
    print(f"""The package `termcolor` is an optional dependency, \
which seems to not be installed in your system.
It's purpose is to provide colorful and more informative prints in the terminal

To install it, stop the script with CTRL-C and type:
\t>>> python3 -m pip install termcolor
Or, get all the optional dependencies at once running
\t>>> python3 -m pip install -r requirements.txt
""")
    COLORFUL = False

'''
FUNCIONES
--------------------------------------------------------------------
'''
def getArgumentParser() -> argparse.ArgumentParser:
    """
    Function that prepares an argument parser with argument options
    (To be used indide getArguments)
    """
    parser = argparse.ArgumentParser(
            description="""
    Archivo que se encargará de convertir los apuntes que tenemos
    de UniNotes a Onyx con el formato necesario para HUGO.
    """
            )
    # Adding optional arguments
    parser.add_argument("-p", "--path", help = "La path \
    completa (desde ~/) al archivo o carpeta que se quiera convertir")

    return parser



def currentFolderCheck() -> bool:
    "Comprueba que estamos en una carpeta o subcarpeta de onyxnotes"
    # Get the path
    currentpath = os.getcwd()
    return "onyx" in currentpath.lower()



def getArguments() -> Tuple[str, str]:
    """
    Function that reads and sets program variable when reading 
    command-line arguments

    return value:
        (uni_notes dir, file or path to convert)
    """
    # Get the path
    parser = getArgumentParser()
    args = parser.parse_args()
    filepath = args.path

    # Get the folder in which Uni Notes is stored
    folders = filepath.split("/")
    indx = 0
    backupname = ""

    for foldername in folders:
        if "uni" in foldername.lower():
            break
        indx  += 1

    else:
        backupname = input("No he sido capaz de encontrar la carpeta de Uni notes...\n\n\
¿Podrías decírmela a continuación?: ")
        indx = -1

    # if the folder wasn't found
    if indx == -1:
        uninotesroot = backupname
    else:
        uninotesroot = "/".join(folders[:indx + 1])

    # Check the folder specified is indeed a subfolder of the root
    if uninotesroot in filepath:
        return (uninotesroot, filepath)
    else:
        raise NameError(f"{filepath} is not a subfolder of {uninotesroot}!")



def colorfull(text: str, 
        color: str, 
        highlight:bool = False, 
        available: bool = COLORFUL
        ):
    "Devuelve el text colorido en la terminal para drip extra"
    # comprueba si está termcolor instalado
    if available:
        # comprueba si se ha especificado subrayado
        if highlight:
            return colored(text, color, attrs=["reverse", "blink"])
        else:
            return colored(text, color)
    else:
        return text



def updateUniNotes(fullpath: str) -> None:
    "Comprueba que estemos usando la  ultima versión de uni notes"
    os.system(f"cd {fullpath} && git branch main && git pull")



def confirmArgs(uninotesroot, argpath) -> bool:
    """
    Comprueba que los argumentos han sido introducidos correctamente
    Devuelve True si son aceptados
    """
    confirmation = input(f"\n[{colorfull('INFO', 'green')}]: ¿Es {colorfull(uninotesroot, 'magenta')}\
 el directorio de Uni notes, y {colorfull(argpath, 'magenta')} lo que se deseea convertir? [y/N]  ")

    #Comprobar la confirmación
    if confirmation.rstrip().lower().replace(" ", "") != "y":
        print(f"\n{colorfull('ALERTA', 'magenta', highlight=True)}: Especifica \
el argumento de `path` en la terminal con '-p'. \nEscribe {colorfull('python3 UniNotesConvert.py -h', 'green')} \
para más infomación")

        return False

    else:
        return True



def isFile(path: str) -> bool:
    return os.path.isfile(path)


'''
ENTRADA DEL PROGRAMA
--------------------------------------------------------------------
'''

if __name__ == "__main__":
    # Comprobar que estamos desde la carpeta de onyx
    if not currentFolderCheck():
        print(f'\n{colorfull("ERROR", "red", highlight=True)}: No te encuentras \
en ninguna carpeta o subcarpeta de onyx.\nPor favor dirígete a una de ellas y \
vuelve a ejecutar el script.\n')
        sys.exit()

    # Get both the root and file/dir
    uninotesroot, argpath = getArguments()

    # Confirmar argumentos
    if not confirmArgs(uninotesroot, argpath):
        sys.exit()

