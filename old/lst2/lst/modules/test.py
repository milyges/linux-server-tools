#-*- coding: utf-8 -*-

class Module:    
    def __init__(self, config, args = []):
        print("test module init! args=%s" % (str(args)))
        
    def start(self):
        print("test module start")
    
    def stop(self):
        print("test module stop")
    
    def restart(self):
        print("test module restart")
   
        