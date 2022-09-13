'''
Created on Mon Sep 12 12:39:19 PM CEST 2022

@file: URLtools.py

@author: Yoquec

@desc:
    Archivo para manejar URLs
'''
from src.GlobalVars import HOME
from typing import Callable, List, Union
import functools


def compose(*functions: Callable) -> Callable:
    """
    Function composition gracias a Arjaan codes :)
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions)

class Link:
    """
    Clase para preprocesar links y asegurarse de
    que tienen el formato correcto
    """
    def __init__(self, link: Union[str, None]) -> None:
        if link is not None:
            self.link = link.replace("\\", r"\\")
        else:
            self.link = None

    def __str__(self) -> str:
        return str(self.link)



class Dir(Link):
    """
    Clase para procesar directorios
    """

    def __init__(self, link: Union[str, None]) -> None:
        super().__init__(link)
        # Eliminar el ~ por la carpeta home
        if self.link is not None:
            self.link = self.link.replace("~", HOME)
        return

    def split(self, char:str) -> List[str]:
        return self.link.split(char)



class URLname(Link):
    """
    Clase que preprocesa una string para que tenga
    el formato apropiado en una string de URL de
    HUGO
    """

    def __init__(self, link: str) -> None:
        super().__init__(link)
        #TODO: Comprobar la transformacion de los nombres de los archivos a links
        #TODO: Comprobar la transformacion de los nombres de las carpetas a links
        #TODO: Comprobar la transformacion de " " a "-"
        """
        Llevar a cabo todas las transformaciones
        con una function composition con la funcion
        compose()
        """

        # Una vez cumplido, borrar el resto de TODOs


# Check if the module has problems
if __name__ == "__main__":
    print("Everything OK!")
