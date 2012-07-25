#-*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread
from threading import Event
from lst.lib.ping import ping_host

class PingThread(Thread):     
    def __init__(self):
        Thread.__init__(self)
        self.__hosts = []
        self.__interval = 30
        self.__log = open("/tmp/ping.log", "a")
        self.__done = Event()    
        self.__done.clear()    
        
    def setup(self, hosts, interval, logpath):
        self.__log.close()
        self.__hosts = hosts
        self.__interval = interval
        self.__log = open(logpath, "a")
    
    def finish(self):
        self.__done.set()
        
    def run(self):
        while not self.__done.wait(self.__interval):
            for host in self.__hosts:
                err = ping_host(host)
            
                if err != 0:
                    self.__log.write("%s: ping `%s` failed\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), host))
                    self.__log.flush()
    
class Module:
    def __init__(self, config, args = []):
        self.config = config
        self.__ping_thread = PingThread()
        
    def reload_config(self):
        hosts = []
        interval = 30
        logpath = "/tmp/ping.log"
        conf = self.config.get("ping.conf")
        
        for c in conf:
            if c[0] == "interval":
                interval = int(c[1])
            elif c[0] == "logpath":
                logpath = c[1]
            elif c[0] == "host":
                hosts.append(c[1])        
        
        self.__ping_thread.setup(hosts, interval, logpath)
    
    def start(self):
        self.reload_config()
        self.__ping_thread.start()
        return True
    
    def stop(self):
        self.__ping_thread.finish()
        self.__ping_thread.join()
        return True
    
    def restart(self):
        self.reload_config()
        return True
        
    