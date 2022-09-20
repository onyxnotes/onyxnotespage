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
import sys
from tqdm import tqdm
import numpy as np
from typing import List, Union
from src.LinkConverter import OnyxLinkConverter
from src.Patterns import *  # import all patterns
from src.ArgParser import getArguments
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



def processFile(filepath: Dir, uninotesdir: Dir) -> str:
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
            LinkConverter = OnyxLinkConverter(
                contents_formated_images,
                uninotesdir,
                filepath,
                verbose=True
            )
            contents_formated_images_links = LinkConverter.process()


        convertedDoc = "\n".join(contents_formated_images_links)

    # # If the extension of the file was not markdown, return None
    else:
        printWarning("\n".join([
            f"File {colorfull('filepath', 'magenta')} is not a markdown file",
            "Skipping..."
        ]))
        # contents_formated_images = ["Nope"]
        convertedDoc = ""

    return convertedDoc


def onyxConvert(target:Dir, unidir: Dir) -> bool:
    """
    Funcion que discierne entre archivos
    carpetas y los convierte.
    """
    # raise NotImplementedError()
    onyx_folder = getOnyxRootDir()
    
    moveFile(onyx_folder, unidir, target, processFile(target, unidir))
    moveImages(onyx_folder, unidir, imagequeue)



    return True

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
