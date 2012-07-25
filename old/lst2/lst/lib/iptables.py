#-*- coding: utf-8 -*-
import os

IPT_PATH = "/sbin/iptables"

class Zone:
    def __init__(self):
        self.name = None
        self.iface = None
        self.cidr = None
        
class Rule:    
    def __init__(self):
        self.params = []
        self.action = None
        self.dest = None
        self.source = None
        
class IPTables:
    __config = { }
    __zones = { }
    __rules = [ ]
    __nat = [ ]
    
    def __init__(self):
        self.__config = { }
        self.__zones = { }
        self.__rules = [ ]
        self.__nat = [ ]
    
    def get_value(self, name, default = None):
        try:
            return self.__config[name]
        except KeyError:
            return default 
    
    def set_value(self, name, value):
        self.__config[name] = value
        
    def __call(self,args, table = "filter"):
        os.system(IPT_PATH + " -t " + table + " " + " ".join(args))
        
    def add_zone(self, zone):
        self.__zones[zone.name] = zone
        
    def add_rule(self,rule):        
        self.__rules.append(rule)

    def add_nat(self,nat):
        self.__nat.append(nat)
        
    def lookup_zone(self,zone):
        try:
            return self.__zones[zone]
        except KeyError:
            return None
        
    def clean(self):
        self.__call(["-F"])
        self.__call(["-X"])
        self.__call(["-F"], "nat")
        self.__call(["-X"], "nat")
        self.__call(["-F"], "mangle")
        self.__call(["-X"], "mangle")
        self.__call(["-P INPUT", "ACCEPT"])
        self.__call(["-P OUTPUT", "ACCEPT"])
        self.__call(["-P FORWARD", "ACCEPT"])
    
    def init(self):
        # Domyślna polityka
        self.__call(["-P INPUT", "DROP"])
        self.__call(["-P OUTPUT", "ACCEPT"])
        self.__call(["-P FORWARD", "DROP"])
        # Połączenia nawiązane
        self.__call(["-A INPUT", "-m state", "--state RELATED,ESTABLISHED", "-j ACCEPT"])
        self.__call(["-A FORWARD", "-m state", "--state RELATED,ESTABLISHED", "-j ACCEPT"])
        
        # Połączenia lokalne
        self.__call(["-A INPUT", "-i lo", "-m state", "--state NEW", "-j ACCEPT"])
        
        # Strefy
        for zone in self.__zones:
            # Łańcuchy serwer <-> strefa
            self.__call(["-N " + zone + "2self"])
            self.__call(["-A INPUT", "-s " + self.__zones[zone].cidr, "-i " + self.__zones[zone].iface, "-m state", "--state NEW", "-j " + zone + "2self"])
            self.__call(["-N self2" + zone])
            self.__call(["-A OUTPUT", "-d " + self.__zones[zone].cidr, "-o " + self.__zones[zone].iface, "-m state", "--state NEW", "-j " + "self2" + zone])
            
            # Łańcuchy strefa1<->strefa2
            for zone2 in self.__zones:
                if zone2 == zone:
                    continue
                
                self.__call(["-N " + zone + "2" + zone2])
                self.__call(["-A FORWARD", "-s " + self.__zones[zone].cidr, "-i " + self.__zones[zone].iface, "-d " + self.__zones[zone2].cidr, "-o " + self.__zones[zone2].iface, "-m state", "--state NEW", "-j " + zone + "2" + zone2])

        # Reguły
        for rule in self.__rules:
            chain = ""
            args = []
            
            if not rule.source:
                chain = "self"
            else:
                chain = rule.source.name
                
            chain = chain + "2"
            
            if not rule.dest:
                chain = chain + "self"
            else:
                chain = chain + rule.dest.name
                
            args = args + ["-A " + chain, "-j " + rule.action]            
            
            for param in rule.params:
                args.append("--" + param)
            
            self.__call(args)
            
        # NAT
        for nat in self.__nat:
            args = []
            if nat.action == "DNAT":
                args.append("-A PREROUTING")
            else:
                args.append("-A POSTROUTING")                
            
            if nat.source:
                args.append("-s " + nat.source.cidr)
                if nat.action == "DNAT":
                    args.append("-i " + nat.source.iface)                
                
            if nat.dest:
                args.append("-d " + nat.dest.cidr)
                if nat.action != "DNAT":                    
                    args.append("-o " + nat.dest.iface)                
                
            args.append("-j " + nat.action)
            
            for param in nat.params:
                args.append("--" + param)
            
            self.__call(args, "nat")
        