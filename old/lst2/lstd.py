#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import signal
import os
import time
from lst.lib.Config import Config

PID_FILE = "/tmp/lstd.pid"

class Controller:
    __modules = { }
    
    def __init__(self):
        c = Config()
    
        modules_conf = c.get("modules.conf")
        self.__modules = { }
        self.__status = { }
        
        # Ładujemy moduły
        for module in modules_conf:
            mod = __import__("lst.modules." + module[0], fromlist = [ 'Module' ])        
            self.__modules[module[0]] = mod.Module(c, module[1:])
    
    def start(self):
        for module in self.__modules:
            self.__status[module] = self.__modules[module].start()
            
    def stop(self):
        for module in self.__modules:            
            if not self.__status[module]:
                continue
            
            self.__status[module] = not self.__modules[module].stop()
    
    def restart(self):
        for module in self.__modules:
            self.__modules[module].restart()

class LstDaemon:    
    
    def __init__(self):
        self.__controller = Controller()
        self.__done = False
        
    def exit_handler(self, signum, frame):
        self.__done = True
    
    def reload_handler(self, signum, frame):
        self.__controller.restart()
    
    def run(self):
        signal.signal(signal.SIGTERM, self.exit_handler)
        signal.signal(signal.SIGHUP, self.reload_handler)
        
        self.__controller.start()
        
        while not self.__done:
            signal.pause()
            
        self.__controller.stop()
    
class LstManager:    
    def __init__(self, argv):
        self.__argv = argv
        
    def __getpid(self):
        try:
            fp = open(PID_FILE, 'r')
        except IOError:
            return False
        
        pid = fp.read()
        fp.close()
        return int(pid.strip())
    
    def __writepid(self):
        try:        
            fp = open(PID_FILE, 'wx')
        except IOError:
            return False
        
        fp.write("%d\n" % os.getpid())
        fp.close()
    
        return True
    
    def __delpid(self):
        try:      
            os.unlink(PID_FILE)
        except OSError:
            return False
        
        return True
    
    def __demonize(self):        
        try:
            pid = os.fork()            
            if pid > 0:
                return pid # Zwracamy PID dziecka            
        except OSError:
            sys.stderr.write("fork failed");
            return False
            
        #os.chdir("/tmp")
        os.setsid()
        os.umask(0)
        
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(os.devnull, 'r')
        so = file(os.devnull, 'a+')
        se = file(os.devnull, 'a+', 0)
        
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
                
        self.__writepid()
        
        d = LstDaemon()
        d.run()
        
        self.__delpid()
        sys.exit(0)
        
    def __start(self):
        pid = self.__getpid()
        
        if pid:
            sys.stderr.write("daemon already running, pid: %d\n" % (pid))
        else:
            sys.stdout.write("Starting LST...")
            sys.stdout.flush()
            pid = self.__demonize()
            sys.stdout.write("DONE, pid: %d\n" % (pid))
    
        return 0
    
    def __stop(self):
        pid = self.__getpid()
        
        if not pid:
            sys.stderr.write("daemon not running, or missing pid file\n")
            return 1
        
        sys.stdout.write("Stopping LST...")
        sys.stdout.flush()
        
        os.kill(pid, signal.SIGTERM)
        
        for i in range(10):
            pid = self.__getpid()
            if pid:
                sys.stdout.write(".")
                sys.stdout.flush()                
                time.sleep(1)
            else:
                break
        
        if not pid:
            sys.stdout.write("DONE\n")
            return 0
        else:
            sys.stdout.write("Timeout\n")
            return 1
            
    def __status(self):
        pid = self.__getpid()
        
        if pid:
            print("status: running (pid=%d)" % (pid))
        else:
            print("status: not running")
    
    def __restart(self):
        pid = self.__getpid()
        
        if not pid:
            sys.stderr.write("daemon not running, or missing pid file\n")
            return 1
        
        print("Reloading LST...DONE")
        os.kill(pid, signal.SIGHUP)
        return 0
    
    def run(self):
        if len(self.__argv) < 2:
            sys.stderr.write("Usage: %s [start | stop | status | restart]\n" % (self.__argv[0]))
            return 1
        
        func = { "start" : self.__start, "stop" : self.__stop, "restart" : self.__restart, "status" : self.__status }
        try:
            return func[self.__argv[1]]()
        except KeyError:
            sys.stderr.write("Usage: %s [start | stop | status | restart]\n" % (self.__argv[0]))
            return 1
        
        return 0
    
if __name__ == '__main__':
    app = LstManager(sys.argv)
    sys.exit(app.run())
        
            
        
    
    