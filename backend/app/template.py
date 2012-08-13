# -*- coding: utf-8 -*-

import re

class Template:
    
    def __init__(self):
        self._vars = { }
        
    def assign(self, name, val):
        self._vars[name] = val
    
    def _repl(self, m):        
        try:
            return self._vars[m.group(1)]
        except KeyError:
            return ""
    
    def generate(self, path):
        tplfile = open(path, 'r')
        out = ""
        
        ifcount = 0
        ifarr = [ ]
        
        for line in tplfile.readlines():
            tmp = re.match("(.*)\{IF \$([A-Z_-]+)\}(.*)", line)
            if tmp:
                ifcount = ifcount + 1 
                try:
                    ifarr.append(self._vars[tmp.group(2)])
                except KeyError:
                    ifarr.append(False)
                
                continue
            
            tmp = re.match("(.*)\{ENDIF\}(.*)", line)
            if tmp:
                if ifcount > 0:
                    ifcount = ifcount - 1
                    del ifarr[ifcount]
                continue
            
            line = re.sub('\{\$([A-Z0-9_]+)\}', self._repl, line)
            
            if ifcount <= 0 or ifarr[ifcount - 1]: 
                out = out + line                
            
        tplfile.close()
        
        return out
        