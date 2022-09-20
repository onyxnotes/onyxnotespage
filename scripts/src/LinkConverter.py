'''
Created on Thu Sep 15 09:17:42 PM CEST 2022

@file: LinkConverter.py

@author: Yoquec
'''
import numpy as np
from typing import List, Union
from src.funcs import printWarning, removeChars
from src.URLtools import Dir, HUGOuri
from src.GlobalVars import CHARSTOREMOVEIMG
from src.Patterns import LINKSEARCH
from src.GlobalVars import ONYXBASEURL, ONYXCONTENTPREFIX
import subprocess


class OnyxLinkConverter(object):

    """ Clase que se encargará de implementar el parsing 
    de los links 

    ALERTA:
        Esta clase toma el contenido en líneas, para
        evitar lidiar con callouts y comentarios
    """

    def __init__(self, contentLines: Union[List[str], np.ndarray], uni_notes_folder: Dir, 
            file: Dir, verbose=False) -> None:
        self.currentFile = file.link
        self.contents = contentLines
        self.processed = np.empty(
            len(self.contents),
            dtype=object
        )
        self.uni_notes_folder = uni_notes_folder
        self.chars_to_remove = CHARSTOREMOVEIMG
        self.verbose = verbose
        # Patterns
        self.linkPattern = LINKSEARCH
        self.OnyxURL = ONYXBASEURL
        self.contentPrefix = ONYXCONTENTPREFIX


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # helper functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getUniNotesInnerFolders(self, filename: str) -> Union[str, None]:
        """Función que obtiene el path de las carpetas intermedias desde
        la root de uninotes de un archivo especificando su nombre"""

        # Escape space characters
        uninotesdirshell = self.uni_notes_folder.link
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


    def changeToRedirectLink(self, line: str, tochange:str, text: bool = False) -> str:
        """Function that changes an obsidian link to be a
        redirection link"""
        # clean link
        tochange_clean = removeChars(tochange, self.chars_to_remove)

        # Check if the link is a self link
        if tochange_clean.split("#")[0] == '' and "#" in tochange:
            toSelfPage = True
        else:
            toSelfPage = False

        try:
        # decision logic
            if toSelfPage:

                if text:
                    obsidian_link, link_text = [part.strip() for part in tochange_clean.split("|")]
                    # if it has link
                    _, header = obsidian_link.split("#")
                    changeby = f'[{link_text}](#{HUGOuri(header)})'

                else:
                    obsidian_link = tochange_clean.strip()
                    _, header = obsidian_link.split("#")
                    changeby = f'[{header}](#{HUGOuri(header)})'
            else:
                if text:
                    obsidian_link, link_text = [part.strip() for part in tochange_clean.split("|")]
                    # if it has link
                    link, header = [p.rstrip() for p in obsidian_link.split("#")]
                    full_file_loc = self.OnyxURL + "/" + str(self.getUniNotesInnerFolders(link)) + "/" +\
                            link + ".md" + "/#" + str(HUGOuri(header))
                    changeby = f'[{link_text}]({HUGOuri(full_file_loc)})'

                # if it has no display text
                else:
                    obsidian_link = tochange_clean.strip()

                    if "#" in obsidian_link:
                        link, header = [p.rstrip() for p in obsidian_link.split("#")]
                        full_file_loc = self.OnyxURL + "/" + str(self.getUniNotesInnerFolders(link)) + "/" +\
                                link + ".md" + "/#" + str(HUGOuri(header))
                        changeby = f'[{header}]({HUGOuri(full_file_loc)})'

                    else:
                        full_file_loc = self.OnyxURL + "/" + str(self.getUniNotesInnerFolders(obsidian_link)) + "/" +\
                                obsidian_link + ".md"
                        changeby = f'[{obsidian_link}](full_file_loc)'
        except:
            changeby = f'LINK_ERROR: {tochange}'
            printWarning(f"Error al procesar el link {tochange} en el archivo {self.currentFile}")

        return line.replace(tochange, changeby)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # main functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def parseLine(self, line: str, tochange: str) -> str:
        " Method that parses a line in search for links "
        #TODO: Process links to specific sites (the ones with `^`) of 
        # the page as pseudo-links in a new shortcode and css class
        if "^" in tochange:
            # If it has text to display, display that text as a pseudo-link 
            clean_link = removeChars(tochange, self.chars_to_remove)
            if "|" not in tochange:
                # Clean the link from special characters
                _, link_text = [p.strip() for p in  clean_link.split("|")]
                changeby = f'{{< pseudolink text="{link_text}" >}}'
                line = line.replace(tochange, changeby)
            else:
                changeby = f"PSEUDOLINK ROTO: {tochange}"
                printWarning(f"PSEUDOLINK ROTO: {tochange} en el archivo {self.currentFile}")
                line = line.replace(tochange, changeby)

        else:
            # If link has text to display
            if "|" in tochange:
                line = self.changeToRedirectLink(line, tochange, text=True)

            # If link has NO text to display
            else:
                # if it is a preview link, just redirect
                # to the page
                line = self.changeToRedirectLink(line, tochange, text=False)


        return line

    def process(self) -> Union[List[str], np.ndarray]:
        """ Method that processes all the lines of the file
        and returns the processed contents"""
        # For each of the lines in the contents
        for nl, line in enumerate(self.contents):
            # if line is not empty
            if len(line) != 0:
                # Get the matches in the line using Regex
                link_matches: List[str] = self.linkPattern.findall(line)
                # for each of the image matches
                for tochange in link_matches:
                    if self.verbose:
                        print(f"Link/s found in line {nl + 1}!:")
                        print(tochange, "\n")
                    line = self.parseLine(line, tochange)

                self.processed[nl] = line
            else:
                # If original line was empty, just add empty string
                self.processed[nl] = ''

        return self.processed
        
