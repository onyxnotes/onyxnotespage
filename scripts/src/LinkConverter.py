'''
Created on Thu Sep 15 09:17:42 PM CEST 2022

@file: LinkConverter.py

@author: Yoquec
'''
import numpy as np
from typing import List, Union
from src.funcs import removeChars
from src.URLtools import Dir
from src.GlobalVars import CHARSTOREMOVEIMG
from src.Patterns import LINKSEARCH
from src.GlobalVars import ONYXBASEURL, ONYXCONTENTPREFIX


class OnyxLinkConverter(object):

    """ Clase que se encargará de implementar el parsing 
    de los links 

    ALERTA:
        Esta clase toma el contenido en líneas, para
        evitar lidiar con callouts y comentarios
    """

    def __init__(self, contentLines: List[str], 
            uni_notes_folder: Dir, verbose=False) -> None:
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


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # helper functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def changeToRedirectLink(self, line: str, tochange:str, text: str | None = None,
            toHeader: bool = False, toSelfPage: bool = False) -> str:
        """Function that changes an obsidian link to be a
        redirection link"""
        if toSelfPage:
            chaneby = f"{{< >}}"
            parsed = line.replace()




    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # main functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def parseLine(self, line: str, tochange: str) -> str:
        " Method that parses a line in search for links "
        #TODO: Process links to specific sites (the ones with `^`) of 
        # the page as pseudo-links in a new shortcode and css class
        if "^" in tochange:
            # If it has text to display, display that text as a pseudo-link 
            if "|" not in tochange:
                # Clean the link from special characters
                clean_link = removeChars(tochange, self.chars_to_remove)
                _, link_text = [p.strip() for p in  clean_link.split("|")]
                changeby = f'{{< pseudolink text="{link_text}" >}}'
                line = line.replace(tochange, changeby)

        else:
            # If link has text to display
            if "|" in tochange:
                pass

            # If link has NO text to display
            else:
                # if it is a preview link, just redirect
                # to the page
                if "!" in tochange:
                    pass
                else:
                    pass

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
        
