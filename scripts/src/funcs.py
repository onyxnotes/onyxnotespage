'''
Created on Mon Sep 12 12:48:04 PM CEST 2022

@file: funcs.py

@author: Yoquec

@desc:
    Archivo que tendrá las helper functions para OnyxConvert.py
'''
import os
from typing import Callable, List, Tuple
from src.GlobalVars import HOME, COLORFUL, ONYXIMAGEFOLDER, ONYXCONTENTPREFIX
import functools
from src.URLtools import Dir

if COLORFUL:
    from termcolor import colored


def isFile(path: str) -> bool:
    return os.path.isfile(path)


def removeChars(string: str, *args) -> str:
    """
    Función que elimina una serie de caracteres
    especificados de una string
    """
    pstring = string

    if isinstance(args[0], list):
        args = args[0]

    for i in args:
        pstring = pstring.replace(i, "")

    return pstring


def currentFolderCheck() -> bool:
    "Comprueba que estamos en una carpeta o subcarpeta de onyxnotes"
    # Get the path
    currentpath = os.getcwd()
    return "onyx" in currentpath.lower()


def checkExtension(filepath, ext) -> bool:
    """
    Check that the file that is going to be
    parsed is of the markdown extension
    """
    if ext != "md":
        printWarning(
            f"El archivo {filepath} no es un archivo de markdown.\n\nIgnorandolo...")

        return False
    else:
        return True


def printWarning(text: str) -> None:
    """
    Prints a warning message to the screen
    """
    print(
        f'\n{colorfull("ALERTA", "magenta", highlight=True)}: {text}\n'
    )
    return


def printError(text: str) -> None:
    """
    Prints an error message to the screen
    """
    print(
        f'\n{colorfull("Error", "red", highlight=True)}: {text}\n'
    )
    return


def printSuccess(text: str) -> None:
    """
    Prints a success message to the screen
    """
    print(
        f'\n{colorfull("Éxito", "green", highlight=True)}: {text}\n'
    )
    return


def getFileNameAndExt(filepath: Dir) -> Tuple["str", "str"]:
    """
    From a full file path, extract the file's name
    and extension
    """
    filepathsplit = filepath.link.split("/")
    filesplit = filepathsplit[-1].split(".")
    filename = ".".join(filesplit[:-1])
    ext = filesplit[-1].lower()
    return (filename, ext)


def compose(*functions: Callable) -> Callable:
    """
    Function composition gracias a Arjaan codes :)
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions)


def moveImages(onyxrootdir: Dir, uni_notes_folder: Dir, imgQueue: List[str]) -> None:
    """Función que meterá todas las imagenes procesadas dentro de la 
    carpeta de Onyx"""
    for img in imgQueue:
        os.system(f'cp "{uni_notes_folder}/Pasted images/{img}" {onyxrootdir}/assets/images/PastedImages/')


def moveFile(onyxrootdir: Dir, uni_notes_folder: Dir, filepath: Dir, contents: str) -> None:
    """Funcion que mete el archivo dentro de la carpeta de Onyx"""
    filecmd = filepath.link.replace(uni_notes_folder.link, "")
    if filecmd[0] == "/":
        filecmd = filecmd[1:]

    hugofile = filecmd.replace(" ", r"\ ")
    cmd = f'cd {onyxrootdir} && hugo new {hugofile}'
    input(cmd)
    os.system(cmd)

    with open(f'{onyxrootdir}/{ONYXCONTENTPREFIX}/{filecmd}', "a") as file:
        file.write(contents)

    return



    


def getOnyxRootDir() -> Dir:
    """
    Devuelve la raiz de la carpeta de onyx
    del sistema
    La devuelve SIN el último /
    """
    folders = os.getcwd().split("/")
    indx = 0
    backupname = ""
    for folder in folders:
        if "onyx" in folder.lower():
            break
        indx += 1

    # Si no se ha encontrado ninguna carpeta
    # que contenga el nombre de onyx,
    # introducir manualmente.
    else:
        backupname = input("No he sido capaz de encontrar la carpeta de Onyx...\n\n\
¿Podrías decírmela a continuación?: ")
        # set -1 as flag for not found
        indx = -1

    if indx == -1:
        onyxroot = backupname
    else:
        onyxroot = "/".join(folders[:indx + 1])

    # return the folder without `~`
    return Dir(onyxroot)


def colorfull(text: str,
              color: str,
              highlight: bool = False,
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


def confirmArgs(uninotesroot, argpath) -> bool:
    """
    Comprueba que los argumentos han sido introducidos correctamente
    Devuelve True si son aceptados
    """
    confirmation = input(f"\n[{colorfull('INFO', 'green')}]: ¿Es {colorfull(uninotesroot, 'magenta')}\
 el directorio de Uni notes, y {colorfull(argpath, 'magenta')} lo que se deseea convertir? [y/N]  ")

    # Comprobar la confirmación
    if confirmation.rstrip().lower().replace(" ", "") != "y":
        print(f"\n{colorfull('ALERTA', 'magenta', highlight=True)}: Especifica \
el argumento de `path` en la terminal con '-p'. \nEscribe {colorfull('python3 UniNotesConvert.py -h', 'green')} \
para más infomación")

        return False

    else:
        return True


def updateUniNotes(unidir: str) -> None:
    "Comprueba que estemos usando la  ultima versión de uni notes"
    os.system(f"cd {unidir} && git checkout main && git pull")
    return
