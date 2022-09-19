'''
Created on Mon Sep 12 12:12:24 PM CEST 2022

@file: Patterns.py

@author: Yoquec

@desc:
    Archivo donde se declaran los patrones de busqueda
    para OnyxConvert.py
'''
import re

########################
# Imágenes
########################
# Patrón de regex para encontrar imágenes
IMGSEARCHTXT =  r"\!\[\[[\w\s]+\.[jsp][pvn][e]*g[\w\s\|]*\]\]"
IMGSEARCH = re.compile(IMGSEARCHTXT)

# Patrón de regex para encontrar imágenes centradas
IMGSEARCHCT = re.compile(
        rf'\<span\s+class=\"*centerImg\"*\s*\>\s*{IMGSEARCHTXT}\s*\<\/span\>'
)

########################
# Enlaces
########################
# NOTE: Solo se puede usar después de haber buscado imágenes,
# sino encontrará ciertas imagenes como jpg o jpegs o otros si hay
# un espacio antes de la "|"

# Patrón de regex para encontrar enlaces a otros apuntes
LINKSEARCH = re.compile(
        r'\!*\[\[[\w\.\-\s]*\#*[\w\.\-\s\^]*(?<!\.png)\|*[\w\.\-\s]*(?<!\.png)\]\]'
        )
