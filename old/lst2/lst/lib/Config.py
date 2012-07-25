#-*- coding: utf-8 -*-
import sys
import os

CONFIG_PATH = os.path.dirname(sys.argv[0]) + '/conf/'
    
class Config:
    __data = { }
    
    def __init__(self):
        self.__data = { }
        
    def __read(self,path):
        data = [ ]
            
        # Otwieramy plik
    
        config = open(path)
        
        for line in config.readlines():
            # Wszystko od # jest komentarzem
            try:
                line = line[0:line.index('#')]
            except:
                pass
     
            args = line.split()                               
            
            if not len(args):
                continue
            
            data.append(args)
            
        config.close()
        return data

    def get(self, name):        
        try:
            data = self.__data[name]
        except KeyError:
            data = self.__read(CONFIG_PATH + name)
            self.__data[name] = data
            
        return data
        
    def reset(self):
        self.__data = { }
