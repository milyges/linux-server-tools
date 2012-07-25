#-*- coding: utf-8 -*-

HOSTS_PATH = "/etc/hosts"

class Module:    
    def __init__(self, config, args = []):
        self.__config = config        
        
    def __gen_hosts(self):
        try:
            hosts = open(HOSTS_PATH, "w")
        except IOError:
            return False
        
        hosts.write("# /etc/hosts: Local Host Database\n")
        hosts.write("#\n")
        hosts.write("# This file describes a number of aliases-to-address mappings for the for\n") 
        hosts.write("# local hosts that share this file.\n")
        hosts.write("#\n")
        hosts.write("# In the presence of the domain name service or NIS, this file may not be\n") 
        hosts.write("# consulted at all; see /etc/host.conf for the resolution order.\n")
        hosts.write("#\n\n")

        hosts.write("# IPv4 and IPv6 localhost aliases\n")
        hosts.write("127.0.0.1\tlocalhost\n")
        hosts.write("::1\t\tlocalhost\n\n")
    
        for host in self.__config.get("hosts.conf"):
            hosts.write("%s\t%s\n" % (host[2], host[1]))
            
        hosts.close()
        return True
    
    def start(self):        
        return self.__gen_hosts()
    
    def stop(self):
        return True
    
    def restart(self):
        return self.__gen_hosts()
    