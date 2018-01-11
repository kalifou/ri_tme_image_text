# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 11:43:45 2017

@author: kalifou
"""

from ParserCLEF08 import *
from Parser import Parser
from Document import Document

if __name__ == "__main__":
#===============================================================================
     a=ParserCLEF08()
     a.initFile("easyCLEF08/easyCLEF08_text.txt")
     x1=a.nextDocument()
     print x1
     x2=a.nextDocument()
     print x2
     x3=a.nextDocument()
     print x3
     x4=a.nextDocument()
     print x4
     x1=a.nextDocument()
     print x1
     x2=a.nextDocument()
     print x2
     x3=a.nextDocument()
     print x3
     x4=a.nextDocument()
     print x4
#===============================================================================