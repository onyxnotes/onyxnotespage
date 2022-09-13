'''
Created on Sat Aug 20 09:17:24 PM CEST 2022

@file: OnyxConvert.py

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

####################################
# LIBRERÍAS
####################################
import os
import sys
import re
import subprocess
from tqdm import tqdm
from typing import List, Union
from src.Patterns import *  # import all patterns
from src.GlobalVars import ONYXBASEURL, ONYXCONTENTPREFIX, \
    ONYXIMAGEFOLDER, CHARSTOREMOVEIMG
from src.ArgParser import getArguments
from src.URLtools import Link, URLname
from src.funcs import *
from src.ImageConverter import OnyxImageConverter


####################################
# VARIABLES GLOBALES
####################################
# Lista de imagenes encontradas
imagequeue: List[str] = []

####################################
# FUNCIONES
####################################


def addImgToQueue(imgname: str, imagequeue=imagequeue) -> None:
    """
    Añade una imagen a la lista de imagenes encontradas,
    con el objetivo de después poder copiarlas todas a 
    su ubicación final
    """
    imagequeue.append(imgname)
    return


def convertLinks(line: str, nl: int, contents: List[str], filepath: str,
                 uninotesdir: str, linksearch=LINKSEARCH) -> str:
    """
    Método que dado una línea de un archivo, convertirá los links 
    a formato HUGO
    """
    # search links using the Regex pattern
    # after having found the images
    linkmch = linksearch.findall(line)
    if len(linkmch):
        print(f"link found in line {nl + 1}!:")
        print(linkmch, "\n")
        # NOTE: Es importante especificar la root
        # de uninotes en convertLineLink para encontrar las carpetas
        # intermedias de los archivos para poner bien
        # las imagenes en la pagina web
        contents[nl] = _convertLinks(line,
                                     selffilename=filename,
                                     uninotesdir=uninotesdir
                                     )
        line = contents[nl]
        return line
    else:
        return line


def _convertLinks(line: str,
                  # Para por si tenemos un link que sea una
                  # referencia a un heading de si mismo
                  selffilename: str,
                  uninotesdir: str,
                  # Para encontrar imagenes en general
                  linksearch: re.Pattern = LINKSEARCH,
                  charstoremove: List[str] = CHARSTOREMOVEIMG,
                  url: str = ONYXBASEURL,
                  contentprefix: str = ONYXCONTENTPREFIX
                  ) -> str:
    """
    Funcion que, especificada una linea,
    devolvera la linea con links en formato
    markdown con los endpoints para Onyx
    """

    def getUniNotesInnerFolders(filename: str) -> Union[str, None]:
        """Función que obtiene el path de las carpetas intermedias desde
        la root de uninotes de un archivo especificando su nombre"""

        # Escape space characters
        uninotesdirshell = uninotesdir.replace(" ", "\\ ")
        try:
            output = subprocess.check_output(
                f'cd {uninotesdirshell} && fd | grep "{filename}"',
                shell=True).decode()

            if output == "":
                print(
                    f"WARNING, the innerfolders of {filename} could not be found")
                innerfolders = None

            else:
                outputsplit = output[2:].split("/")
                innerfolders = "/".join(outputsplit[:-1])

        # In case the subprocess fails
        except subprocess.CalledProcessError as err:
            print(err)
            innerfolders = None

        return innerfolders

    # Get all the matches in the line
    mchs = linksearch.findall(line)

    # Go through all the matches
    for tochange in mchs:
        # If the link is not of the type `!`
        if "^" in tochange:
            if "|" in tochange:
                linkclean = removeChars(tochange, charstoremove)
                linksplit = [part.strip() for part in linkclean.split("|")]
                changeby = f'**{linksplit[1]}**'
            else:
                changeby = f'LINK ROTO: {tochange}'
            line = line.replace(tochange, changeby)

        else:
            if "!" not in tochange:
                linkclean = removeChars(tochange, charstoremove)

                # Check if the link has |
                if "|" in tochange:
                    linksplit = [part.strip() for part in linkclean.split("|")]
                    linkpath = linksplit[0]
                    linktext = linksplit[1]

                    #Check if the link has #
                    if "#" in tochange:
                        linkpathsplit = [part.strip()
                                         for part in linkpath.split("#")]
                        # TODO: Comprobar la transformacion de los nombres de los archivos a links
                        filename = linkpathsplit[0]

                        # If we have a self link
                        if len(filename) == 0:
                            filename = selffilename

                        # Get the inner folders
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        # TODO: Comprobar la transformacion de los nombres de las carpetas a links
                        innerfolderslink = innerfolders.lower().replace(" ", "-")

                        # TODO: Comprobar la transformacion de " " a "-"
                        linkname = filename.lower().replace(" ", "-")
                        # Change the name of the pointer that is being pointed to
                        # to use HUGO's syntax
                        # ie: https://onyxnotes.netlify.app/en/docs/prologue/test/#heading-1
                        linkheaderpointer = linkpathsplit[1].lower().replace(
                            " ", "-")
                        changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname}/#{linkheaderpointer})'

                    else:
                        filename = linkpath

                        # Get the inner folders
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        # TODO: Comprobar la transformacion de los nombres de las carpetas a links
                        innerfolderslink = innerfolders.lower().replace(" ", "-")

                        # TODO: Comprobar la transformacion de " " a "-"
                        linkname = linkpath.lower().replace(" ", "-")
                        changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname})'

                # No custom text to display
                else:
                    linkpath = linkclean
                    linktext = linkpath.strip()
                    # TODO: Comprobar la transformacion de los nombres de los archivos a links

                    #Check if the link has #
                    if "#" in tochange:
                        linkpathsplit = [part.strip()
                                         for part in linkpath.split("#")]
                        # TODO: Comprobar la transformacion de los nombres de los archivos a links
                        filename = linkpathsplit[0]

                        # If we have a self link
                        if len(filename) == 0:
                            filename = selffilename

                        # Get the inner folders
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        # TODO: Comprobar la transformacion de los nombres de las carpetas a links
                        innerfolderslink = innerfolders.lower().replace(" ", "-")
                        # TODO: Comprobar la transformacion de " " a "-"
                        linkname = filename.lower().replace(" ", "-")
                        # Change the name of the pointer that is being pointed to
                        # to use HUGO's syntax
                        # ie: https://onyxnotes.netlify.app/en/docs/prologue/test/#heading-1
                        linkheaderpointer = linkpathsplit[1].lower().replace(
                            " ", "-")
                        changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname}/#{linkheaderpointer})'

                    else:
                        # Get the inner folders
                        filename = linkpath.strip()
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        # TODO: Comprobar la transformacion de los nombres de las carpetas a links
                        innerfolderslink = innerfolders.lower().replace(" ", "-")
                        linkname = linkpath.lower().replace(" ", "-")
                        changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname})'

                # Change the line
                line = line.replace(tochange, changeby)

            # If it does have !
            else:
                linkclean = removeChars(tochange, charstoremove)
                linkpath = linkclean
                linktext = linkpath.strip()
                # TODO: Comprobar la transformacion de los nombres de los archivos a links

                #Check if the link has #
                if "#" in tochange:
                    linkpathsplit = [part.strip()
                                     for part in linkpath.split("#")]
                    # TODO: Comprobar la transformacion de los nombres de los archivos a links
                    filename = linkpathsplit[0]

                    # If we have a self link
                    if len(filename) == 0:
                        filename = selffilename

                    # Get the inner folders
                    innerfolders = getUniNotesInnerFolders(filename)
                    if innerfolders is None:
                        print("WARNING, no innerfolders found!")
                        innerfolders = ""

                    # TODO: Comprobar la transformacion de los nombres de las carpetas a links
                    innerfolderslink = innerfolders.lower().replace(" ", "-")
                    # TODO: Comprobar la transformacion de " " a "-"
                    linkname = filename.lower().replace(" ", "-")
                    # Change the name of the pointer that is being pointed to
                    # to use HUGO's syntax
                    # ie: https://onyxnotes.netlify.app/en/docs/prologue/test/#heading-1
                    linkheaderpointer = linkpathsplit[1].lower().replace(
                        " ", "-")
                    changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname}/#{linkheaderpointer})'

                else:
                    # Get the inner folders
                    filename = linkpath.strip()
                    innerfolders = getUniNotesInnerFolders(filename)
                    if innerfolders is None:
                        print("WARNING, no innerfolders found!")
                        innerfolders = ""

                    # TODO: Comprobar la transformacion de los nombres de las carpetas a links
                    innerfolderslink = innerfolders.lower().replace(" ", "-")
                    linkname = linkpath.lower().replace(" ", "-")
                    changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname})'

                # Change the line
                line = line.replace(tochange, changeby)

    return line


def processFile(filepath: Dir, uninotesdir: str) -> Union[List[str], None]:
    """
    Funcion que dado un archivo, lo procesara y lo devuelve en formato de HUGO
    """
    # raise NotImplementedError()
    # Get both the filename and extension
    filename, ext = getFileNameAndExt(filepath)
    # Primero haremos una comprobacion de que el archivo
    # es del formato markdown
    if checkExtension(filepath, ext):
        # 1. Abrir el archivo
        # Read the file,
        with open(filepath.link, "r") as file:
            # clean unicode, and remove newlines
            contents: List[str] = [line.rstrip() for line in file.readlines()]
    # 2. Barra de progreso # TODO

    # 3. Buscar y convertir imagenes
            ImageConverter = OnyxImageConverter(contents, verbose=True)
            contents_formated_images = ImageConverter.process()
            # Add images to queue
            for image in ImageConverter.queue:
                addImgToQueue(image)

    # 4. Buscar y convertir links
                # line = convertLinks(line,
                #         nl,
                #         contents,
                #         filename,
                #         filepath,
                #         uninotesdir
                #         )

        # convertedDoc = contents

    # # If the extension of the file was not markdown, return None
    else:
        printWarning("\n".join([
            f"File {colorfull('filepath', 'magenta')} is not a markdown file",
            "Skipping..."
        ]))
        # contents_formated_images = ["Nope"]
        # convertedDoc = None

    return convertedDoc


def onyxConvert(target, unidir) -> bool:
    """
    Funcion que discierne entre archivos
    carpetas y los convierte.
    """
    raise NotImplementedError()
    # processFile(target, unidir)
    # return True

    # 1. Manejar los errores
    # 2. Distinguir entre archivo/carpeta
    # 3. Convertir usando processFile()
    # 4. Mover imagenes a la carpeta de imagenes de onyx
    # 5. Guardar el archivo en la carpeta de onyx correspondiente.


####################################
# ENTRADA DEL PROGRAMA
####################################
if __name__ == "__main__":
    # Comprobar que estamos desde la carpeta de onyx
    if not currentFolderCheck():
        printError(
            "\n".join(
                [
                    "No te encuentras en ninguna carpeta o subcarpeta de onyx.",
                    "Por favor dirígete a una de ellas y vuelve a ejecutar el script"
                ]
            )
        )

        sys.exit(2)

    # Get both the root and file/dir arguments
    uninotesroot, argpath = getArguments()

    # Confirmar argumentos
    if not confirmArgs(uninotesroot, argpath):
        sys.exit(1)

    # Empezar a procesar el archivo o las carpetas
    status = onyxConvert(argpath, uninotesroot)
    if status:
        printSuccess(
            "El/los documentos han sido convertidos satisfactoriamente"
        )

    else:
        printError(
            "Ha habido un error procesando el/los documentos..."
        )

        # Hacer un `git stash`
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Salir del programa con un codigo de error
        sys.exit(2)
