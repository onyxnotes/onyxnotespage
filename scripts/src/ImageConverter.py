'''
Created on Mon Sep 13 14:03:04 PM CEST 2022

@file: ImageConverter.py

@author: Yoquec

@desc:
    Clase que implementará el comportamiento del parser
    de imágenes
'''
from typing import List, Union
import numpy as np
from src.Patterns import IMGSEARCH, IMGSEARCHCT
from src.GlobalVars import CHARSTOREMOVEIMG, ONYXIMAGEFOLDER
from src.funcs import removeChars, printWarning, printError

# TODO: Implement a protocol in order to be able to use
# different parsers
# class ImageConverter(Protocol):
#     def addImgToQueue(self, image: str, queue: List[str]):
#         "Method that ads an image to the print queue"


class OnyxImageConverter():
    """
    Clase que convierte imágenes a formato HUGO

    ALERTA:
        Esta clase toma el contenido en líneas, para
        evitar lidiar con callouts y comentarios
    """

    def __init__(self, contentLines: List[str], verbose=False) -> None:
        self.contents = contentLines
        self.processed = np.empty(
            len(self.contents),
            dtype=object
        )
        self.verbose = verbose
        self.chars_to_remove = CHARSTOREMOVEIMG
        # Patterns
        self.imgPattern = IMGSEARCH
        self.centeredImgPattern = IMGSEARCHCT
        # Onyx folder
        self.imgFolder = ONYXIMAGEFOLDER
        # Image queue
        self.queue: List[str] = []

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Helper functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addImgToQueue(self, image: str) -> None:
        " Method that ads an image to the print queue "
        self.queue.append(image)
        return

    def convertSizedImage(self, line: str, tochange: str, imgdata: List[str], centered: bool = False) -> str:
        """
        Generates the string for an image with width information
        """
        imgname = imgdata[0]

        if self.verbose:
            print(f"Img data centrado: {imgdata}")

        # Choose proper shortcode name
        if centered:
            shortcode = "globalimgsinaltct"
        else:
            shortcode = "globalimgsinalt"

        # Create the final image format
        changeby = f'{{< {shortcode}  imgpath="{self.imgFolder}/{imgname}" res="{imgdata[1]}x" >}}'
        # Add the image name to the queue
        self.addImgToQueue(imgname)
        # Substitute the old format by the new
        return line.replace(tochange, changeby)

    def convertUnsizedImage(self, line: str, tochange: str, imgstr: str, centered: bool = False) -> str:
        """
        Generates the string for an image without
        width information
        """
        # Get the name of the file
        imgname = imgstr.strip()
        if self.verbose:
            print(f'Nombre de la imagen sin width pero centrada: "{imgname}"')
        # Choose proper shortcode name
        if centered:
            shortcode = "globalimgsinaltctww"
        else:
            shortcode = "globalimgsinaltww"
        # Create the final image format
        changeby = f'{{< {shortcode} imgpath="{self.imgFolder}/{imgname}" >}}'
        # Add the image name to the queue
        self.addImgToQueue(imgname)
        # Substitute the old format by the new
        return line.replace(tochange, changeby)

    def parseCenteredImage(self,
                           line: str,
                           tochange: str,
                           cent_image_matches: List[str]) -> str:
        " Parses centered obsidian image"
        # Go through the centered image matches
        for cent_image in cent_image_matches:
            try:  # Try get just  the image: `![[image data]]`
                obsidian_img = self.imgPattern.search(cent_image).group()
            except AttributeError as e:
                printWarning(
                    f"Wasn't able to parse information about {cent_image}\n{e}"
                )
                continue

            # Clean borders
            img_str = removeChars(obsidian_img, CHARSTOREMOVEIMG)

            # If image is to be resized
            if "|" in img_str:
                imgdata = [
                    data.strip() for data
                    in img_str.split("|")
                ]
                line = self.convertSizedImage(
                    line, cent_image, imgdata, centered=True)

            # If the image does not have to be resized
            else:
                line = self.convertUnsizedImage(
                    line, cent_image, img_str, centered=True)

        return line

    def parserUncenteredImages(self, line: str, tochange: str) -> str:
        " Parses normal obsidian images"
        img_str = removeChars(tochange, CHARSTOREMOVEIMG)
        # If image is sized
        if "|" in img_str:
            imgdata = [
                    data.strip() for data \
                    in img_str.split("|")
                    ]
            return self.convertSizedImage(line, tochange, imgdata)

        # If image is unsized
        else:
            return self.convertUnsizedImage(line, tochange, img_str) 

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # main functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def parseLine(self, line: str, tochange: str) -> str:
        " Method that parses a line in search for images "
        # check if the match must be centered
        cent_images = self.centeredImgPattern.findall(line)
        cent_image_match = [
            centmatch for centmatch in cent_images if tochange in centmatch
            ]
        try:
            assert len(cent_image_match) < 2
        except AssertionError as e:
            printError(f"There were found two centered images in the same line\n{e}")

        # If the image is centered
        if len(cent_image_match):
            if self.verbose:
                print(f"Centered images found: {cent_image_match}")
            return self.parseCenteredImage(line, tochange, cent_image_match)

        # If the image is not centered
        else:
            return self.parserUncenteredImages(line, tochange)

    def process(self) -> Union[List[str], np.ndarray]:
        """ Method that processes all the lines of the file
        and returns the processed contents"""
        # NOTE: maybe add tqdm
        # For each of the lines in the contents
        for nl, line in enumerate(self.contents):
            # if line is not empty
            if len(line) != 0:
                # Get the matches in the line using Regex
                image_matches: List[str] = self.imgPattern.findall(line)
                # for each of the image matches
                for tochange in image_matches:
                    if self.verbose:
                        print(f"Image/s found in line {nl + 1}!:")
                        print(tochange, "\n")
                    line = self.parseLine(line, tochange)
                self.processed[nl] = line
            else:
                # If original line was empty, just add empty string
                self.processed[nl] = ''

        return self.processed
