'''
Created on Mon Sep 12 12:35:02 PM CEST 2022

@file: ArgParser.py

@author: Yoquec

@desc:
    Archivo que prepara el parser para los argumentos de la terminal
'''
import argparse
from typing import Tuple
import sys
from src.GlobalVars import HOME
from src.URLtools import Dir

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
    filepathstr = args.path
    filepath = Dir(filepathstr)
    """
    Esta parte del codigo es muy sucia, deberia de ser
    reimplementada. La funcionalidad de la que se
    encarga es comprobar que en efecto se ha introducido
    un argumento al script desde la terminal.
    Si nada se ha introducido, solo imprime la ayuda y
    sale del programa.

    Esto probablemente se pueda implementar de una forma
    mas limpia haciendo una subclase del parser que 
    modifique el metodo error(), como explica este
    este post de stack overflow:
        https://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu

    Aun asi por ahora funciona sin problemas, asi que
    lo dejo para la posteridad.
    """
    # Check a filepath has been introduced, if not,
    # exit and display help
    if filepath.link is None:
        # show parser help
        parser.print_help()
        # exit the program
        sys.exit(0)

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
        # Flag to indicate folder not found
        indx = -1

    # if the folder wasn't found
    if indx == -1:
        uninotesroot = Dir(backupname)
    else:
        # if found, reconstruct the folders
        uninotesroot = Dir(("/".join(folders[:indx + 1])))

    # Check the folder specified is indeed a subfolder of the root
    if str(uninotesroot) in filepath.link:
        return (uninotesroot, filepath)
    else:
        raise ValueError(f"{filepath} is not a subfolder of {uninotesroot}!")


# Check if the module has any problems
if __name__ == "__main__":
    print("Everything OK!")
