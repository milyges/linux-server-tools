#-*- coding: utf-8 -*-
import string

class Config:
    __path = None
    __func = { }
    
    def __init__(self,path,func):
        self.__path = path     
        self.__func = func   
    
    def parse(self):
        # Otwieramy plik
        try:
            config = open(self.__path)
        except IOError:
            return False
    
        i = 0
        for line in config.readlines():
            i = i + 1
            # Wszystko od # jest komentarzem
            try:
                line = line[0:line.index('#')]
            except:
                pass
                                    
            args = string.split(line)
            
            if not len(args):
                continue
            
            try:
                self.__func[args[0]](args[1:])
            except KeyError:
                print("%s: line %d: unknown command: %s" % (self.__path, i, args[0]))
                config.close()
                return False
            
        config.close()
        return True