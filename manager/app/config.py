# -*- coding: utf-8 -*-

def config_parse(configstr):
    data = []
    
    for line in configstr.split("\n"):
        # Wszystko od # jest komentarzem
        try:
            line = line[0:line.index('#')]
        except:
            pass
     
        args = line.split()

        if args:
            data.append(args)
            
    return data
