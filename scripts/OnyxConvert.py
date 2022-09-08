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

####################################
# LIBRERÍAS
####################################
import os
import sys
import re
import argparse
import subprocess
from tqdm import tqdm
from typing import Tuple, List, Union
import itertools


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


####################################
# VARIABLES GLOBALES
####################################
HOME = os.environ["HOME"]
ONYXURL = "https://onyxnotes.com"
# Prefijo a la carpeta de contenido de onyx
ONYXCONTENTPREFIX = "content/en" # sin / al final para ser consistentes
# Prefijo a la carpeta de contenido de onyx
ONYXCONTENTPREFIX = "content/en" # sin / al final para ser consistentes
# Siempre que haya una imagen, con o sin centrado o
# ancho, hara match
CHARSTOREMOVE = ["!", "[", "]"]
# Carpeta de onyxnotes donde irán las imágenes
IMAGEFOLDER = "images/PastedImages"
# Patrón de regex para encontrar imágenes
IMGSEARCHTXT =  r"\!\[\[[\w\s]+\.[jsp][pvn][e]*g[\w\s\|]*\]\]"
IMGSEARCH = re.compile(IMGSEARCHTXT)
# Patrón de regex para encontrar imágenes centradas
IMGSEARCHCT = re.compile(
        rf'\<span\s+class=\"*centerImg\"*\s*\>\s*{IMGSEARCHTXT}\s*\<\/span\>'
)

# Patrón de regex para encontrar enlaces a otros apuntes
# NOTE: Solo se puede usar después de haber buscado imágenes,
# sino encontrará ciertas imagenes como jpg o jpegs o otros si hay
# un espacio antes de la "|"
LINKSEARCH = re.compile(
        r'\!*\[\[[\w\.\-\s]*\#*[\w\.\-\s\^]*(?<!\.png)\|*[\w\.\-\s]*(?<!\.png)\]\]'
        )
# Lista de imagenes encontradas
imagequeue: List[str] = []

####################################
# FUNCIONES
####################################
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
    if filepath is None:
        # show parser help
        parser.print_help()
        # exit the program
        sys.exit()

    elif "~" in filepath:
        # subprocess modules do not do a good job when passing `~`,
        # so we will replace it with the system's own home dir
        filepath = filepath.replace("~", HOME)

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
        uninotesroot = backupname.replace("~", HOME)
    else:
        # if found, reconstruct the folders
        uninotesroot = ("/".join(folders[:indx + 1])).replace("~", HOME)

    # Check the folder specified is indeed a subfolder of the root
    if uninotesroot in filepath:
        return (uninotesroot, filepath)
    else:
        raise ValueError(f"{filepath} is not a subfolder of {uninotesroot}!")



def getOnyxRootDir() -> str:
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
    return onyxroot.replace("~", HOME)



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



def updateUniNotes(unidir: str) -> None:
    "Comprueba que estemos usando la  ultima versión de uni notes"
    os.system(f"cd {unidir} && git checkout main && git pull")
    return



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



def addImgToQueue(imgname: str, imagequeue=imagequeue) -> None:
    """
    Añade una imagen a la lista de imagenes encontradas,
    con el objetivo de después poder copiarlas todas a 
    su ubicación final
    """
    imagequeue.append(imgname)
    return



def convertImages(line:str, nl:int, contents: List[str], imgsearch=IMGSEARCH) -> str:
    """
    Método que dado una línea de un archivo, 
    """
    imgmch = imgsearch.findall(line)
    if len(imgmch):
        print(f"Image found in line {nl + 1}!:")
        print(imgmch,"\n")
        contents[nl] = _convertImages(line)
        #NOTE: Importante actualizar la linea 
        # tras analizar las imagenes
        line = contents[nl]
        return line
    else:
        return line




def _convertImages(line: str, 
        # Para encontrar imagenes en general
        imgSearch=IMGSEARCH,
        imgSearchC=IMGSEARCHCT,
        charstoremove=CHARSTOREMOVE,
        imagefolder=IMAGEFOLDER) -> str:
    """
    Funcion que, especificada una linea,
    devolvera la linea con imagenes en formato
    HUGO.
    *Necesita ser llamada desde convertImages
    """
    def generateLineWbar(line, tochange, imgdata) -> str:
        """
        Generates the string for an image with width information
        """
        imgname = imgdata[0]
        # DEBUG: remove after use
        print(f"Img data centrado: {imgdata}")
        # Create the final image format
        changeby = f'{{< globalimgsinaltct imgpath="{imagefolder}/{imgname}" res="{imgdata[1]}x" >}}'
        # Add the image name to the queue
        addImgToQueue(imgname)
        # Substitute the old format by the new
        return line.replace(tochange, changeby)

    def generateLineWObar(line, tochange, imgstr) -> str:
        """
        Generates the string for an image without
        width information
        """
        # Get the name of the file
        imgname = imgstr.strip()
        print(f'Nombre de la imagen sin width pero centrada: "{imgname}"')
        # Create the final image format
        changeby = f'{{< globalimgsinaltctww imgpath="{imagefolder}/{imgname}" >}}'
        # Add the image name to the queue
        addImgToQueue(imgname)
        # Substitute the old format by the new
        return line.replace(tochange, changeby)

    def processLine(line):
        """
        Esta funcion, dada una linea, procesa la primera
        imagen, y solo la primera que encuentra,
        asi que en el caso de que solo haya una imagen, solo
        se llama una sola vez
        """
        # Get all the matches in the line
        mchs = imgSearch.findall(line)
        # check if the image is centered
        centMchs = imgSearchC.findall(line)

        # If the image is centered
        if len(centMchs):
            # target to change will be the first match of the centered
            # list matches
            tochange = centMchs[0]
            # Name of the image to change without the <span ...>
            imgstr = mchs[0]
            imgstrclean = removeChars(imgstr, charstoremove)
            # Check if the image has specified width
            if "|" in imgstr:
                imgdata = [
                        data.strip() for data \
                        in imgstrclean.split("|")
                        ]
                line = generateLineWbar(line, tochange, imgdata)

            # If the image has no specified width
            else:
                line = generateLineWObar(line, tochange, imgstrclean)

        # If the image is NOT centered
        else:
            imgstr = mchs[0]
            tochange = imgstr
            imgstrclean = removeChars(imgstr, charstoremove)
            # Check if the image has specified width
            if "|" in imgstr:
                imgdata = [
                        data.strip() for data \
                        in imgstrclean.split("|")
                        ]
                line = generateLineWbar(line, tochange, imgdata)

            # If the image has NO specified width
            else:
                line = generateLineWObar(line, tochange, imgstrclean)

        # Return the replaced line
        return line

    # Get the matches
    mchs = imgSearch.findall(line)
    # In case there is only one image
    if len(mchs) == 1:
        line = processLine(line)

    # If there is more than one image:
    else:
        # Create an iterable list to iterate
        # between matches
        mchlist = mchs.copy()
        for _ in mchlist:
            line = processLine(line)
            print(f"New line update: {line}")

    return line


def convertLinks(line:str, nl:int, contents: List[str], filepath: str, 
        uninotesdir:str, linksearch=LINKSEARCH) -> str:
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
                selffilename = filename, 
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
                uninotesdir:str,
                # Para encontrar imagenes en general
                linksearch: re.Pattern = LINKSEARCH,
                charstoremove: List[str] = CHARSTOREMOVE,
                url: str = ONYXURL,
                contentprefix: str = ONYXCONTENTPREFIX
                ) -> str:
    """
    Funcion que, especificada una linea,
    devolvera la linea con links en formato
    markdown con los endpoints para Onyx
    """

    def getUniNotesInnerFolders(filename:str) -> Union[str,None]:
        """Función que obtiene el path de las carpetas intermedias desde
        la root de uninotes de un archivo especificando su nombre"""

        # Escape space characters
        uninotesdirshell = uninotesdir.replace(" ", "\\ ")
        try:
            output = subprocess.check_output(
                    f'cd {uninotesdirshell} && fd | grep "{filename}"',
                    shell=True).decode()

            if output == "":
                print(f"WARNING, the innerfolders of {filename} could not be found")
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
                        linkpathsplit = [part.strip() for part in linkpath.split("#")]
                        #TODO: Comprobar la transformacion de los nombres de los archivos a links
                        filename = linkpathsplit[0]

                        # If we have a self link
                        if len(filename) == 0:
                            filename = selffilename

                        # Get the inner folders
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        #TODO: Comprobar la transformacion de los nombres de las carpetas a links
                        innerfolderslink = innerfolders.lower().replace(" ", "-")

                        #TODO: Comprobar la transformacion de " " a "-"
                        linkname = filename.lower().replace(" ", "-")
                        # Change the name of the pointer that is being pointed to 
                        # to use HUGO's syntax
                        # ie: https://onyxnotes.netlify.app/en/docs/prologue/test/#heading-1
                        linkheaderpointer = linkpathsplit[1].lower().replace(" ", "-")
                        changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname}/#{linkheaderpointer})'

                    else:
                        filename = linkpath

                        # Get the inner folders
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        #TODO: Comprobar la transformacion de los nombres de las carpetas a links
                        innerfolderslink = innerfolders.lower().replace(" ", "-")

                        #TODO: Comprobar la transformacion de " " a "-"
                        linkname = linkpath.lower().replace(" ", "-")
                        changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname})'

                #No custom text to display
                else:
                    linkpath = linkclean
                    linktext = linkpath.strip()
                    #TODO: Comprobar la transformacion de los nombres de los archivos a links

                    #Check if the link has #
                    if "#" in tochange:
                        linkpathsplit = [part.strip() for part in linkpath.split("#")]
                        #TODO: Comprobar la transformacion de los nombres de los archivos a links
                        filename = linkpathsplit[0]

                        # If we have a self link
                        if len(filename) == 0:
                            filename = selffilename

                        # Get the inner folders
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        #TODO: Comprobar la transformacion de los nombres de las carpetas a links
                        innerfolderslink = innerfolders.lower().replace(" ", "-")
                        #TODO: Comprobar la transformacion de " " a "-"
                        linkname = filename.lower().replace(" ", "-")
                        # Change the name of the pointer that is being pointed to 
                        # to use HUGO's syntax
                        # ie: https://onyxnotes.netlify.app/en/docs/prologue/test/#heading-1
                        linkheaderpointer = linkpathsplit[1].lower().replace(" ", "-")
                        changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname}/#{linkheaderpointer})'

                    else:
                        # Get the inner folders
                        filename = linkpath.strip()
                        innerfolders = getUniNotesInnerFolders(filename)
                        if innerfolders is None:
                            print("WARNING, no innerfolders found!")
                            innerfolders = ""

                        #TODO: Comprobar la transformacion de los nombres de las carpetas a links
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
                #TODO: Comprobar la transformacion de los nombres de los archivos a links

                #Check if the link has #
                if "#" in tochange:
                    linkpathsplit = [part.strip() for part in linkpath.split("#")]
                    #TODO: Comprobar la transformacion de los nombres de los archivos a links
                    filename = linkpathsplit[0]

                    # If we have a self link
                    if len(filename) == 0:
                        filename = selffilename

                    # Get the inner folders
                    innerfolders = getUniNotesInnerFolders(filename)
                    if innerfolders is None:
                        print("WARNING, no innerfolders found!")
                        innerfolders = ""

                    #TODO: Comprobar la transformacion de los nombres de las carpetas a links
                    innerfolderslink = innerfolders.lower().replace(" ", "-")
                    #TODO: Comprobar la transformacion de " " a "-"
                    linkname = filename.lower().replace(" ", "-")
                    # Change the name of the pointer that is being pointed to 
                    # to use HUGO's syntax
                    # ie: https://onyxnotes.netlify.app/en/docs/prologue/test/#heading-1
                    linkheaderpointer = linkpathsplit[1].lower().replace(" ", "-")
                    changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname}/#{linkheaderpointer})'

                else:
                    # Get the inner folders
                    filename = linkpath.strip()
                    innerfolders = getUniNotesInnerFolders(filename)
                    if innerfolders is None:
                        print("WARNING, no innerfolders found!")
                        innerfolders = ""

                    #TODO: Comprobar la transformacion de los nombres de las carpetas a links
                    innerfolderslink = innerfolders.lower().replace(" ", "-")
                    linkname = linkpath.lower().replace(" ", "-")
                    changeby = f'[{linktext}]({url}/{contentprefix}/{innerfolderslink}/{linkname})'

                # Change the line
                line = line.replace(tochange, changeby)

    return line

def checkExtension(filepath, ext) -> bool:
    """
    Check that the file that is going to be
    parsed is of the markdown extension
    """
    if ext != "md":
        print(f"{colorfull('ALERTA', 'magenta', highlight=True)}:\
 El archivo {filepath} no es un archivo de markdown.\n\nIgnorandolo...\n")
        return False
    else:
        return True


def getFileNameAndExt(filepath):
    """
    From a full file path, extract the file's name
    and extension
    """
    filepathsplit = filepath.split("/")
    filesplit = filepathsplit[-1].split(".")
    filename = ".".join(filesplit[:-1])
    ext = filesplit[-1].lower()
    return (filename, ext)


def processFileLines(filepath:str, uninotesdir:str) -> Union[List[str], None]:
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
        with open(filepath, "r") as file:
            # clean unicode, and remove newlines
            contents: List[str] = [line.rstrip() for line in file.readlines()]
    # 2. Barra de progreso
            # Create an iterable with a progress bar
            lineIterable = tqdm(enumerate(contents), desc="Convirtiendo las lineas", unit="lines")

            # Read the file lines
            for nl, line in lineIterable: #nl keeps track of the line number
                # Skip empty lines:
                if len(line):
    # 3. Buscar y convertir imagenes
                    line = convertImages(line, nl, contents)

    # 4. Buscar y convertir links
                    line = convertLinks(line,
                            nl,
                            contents,
                            filename,
                            filepath, 
                            uninotesdir
                            )

        convertedDoc = contents

    # If the extension of the file was not markdown, return None
    else:
        convertedDoc = None

    return convertedDoc




def onyxConvert(target, unidir, onyxdir) -> bool:
    """
    Funcion que discierne entre archivos
    carpetas y los convierte.
    """
    print(target)
    raise NotImplementedError()
    processFileLines(target, unidir)

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
        print(f'\n{colorfull("ERROR", "red", highlight=True)}: No te encuentras \
en ninguna carpeta o subcarpeta de onyx.\nPor favor dirígete a una de ellas y \
vuelve a ejecutar el script.\n')
        sys.exit(2)

    # Get both the root and file/dir arguments
    uninotesroot, argpath = getArguments()

    # Confirmar argumentos
    if not confirmArgs(uninotesroot, argpath):
        sys.exit(1)

    # Obterner el path de la carpeta de onyx para
    # empezar la conversion
    onyxroot = getOnyxRootDir()

    # Empezar a procesar el archivo o las carpetas
    status = onyxConvert(argpath, uninotesroot, onyxroot)
    if status:
        print(f"\n{colorfull('EXITO', 'green', highlight=True)} \
El/los documentos han sido convertidos satisfactoriamente\n")

    else:
        print(f"\n{colorfull('ERROR', 'red', highlight=True)} \
Ha habido un error procesando el/los documentos...\n")
        # Hacer un `git stash`
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Salir del programa con un codigo de error
        sys.exit(2)
