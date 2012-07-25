#-*- coding: utf-8 -*-
import string

from lst.lib.config import Config
from lst.lib.iptables import IPTables, Rule, NatRule, Zone

# TODO: Sprawdzanie poprawności danych
class Firewall:
    __iptables = None
    
    def __add_zone(self, args):
        z = Zone()
        z.name = args[0]
        z.iface = args[1]
        z.cidr = args[2]            
        self.__iptables.add_zone(z)
        
    def __add_host(self,args):
        z = Zone()
        z.name = args[0]
        z.iface =  
        
    def __make_rule(self, args):
        r = Rule()
        r.source = self.__iptables.lookup_zone(args[0])
        r.dest = self.__iptables.lookup_zone(args[1])
        r.action = args[2]
        
        if len(args) > 3:
            for param in args[3:]:
                r.params.append(string.replace(param, "=", " "))
        else:
            r.params = []
            
        return r
    def __add_nat_rule(self, args):
        r = self.__make_rule(args)
        self.__iptables.add_nat(r)
    
    def __add_rule(self, args):
        r = self.__make_rule(args)
        self.__iptables.add_rule(r)
    
    def __init__(self):
        self.__iptables = IPTables()
            
    def enable(self):
        func = { "zone" : self.__add_zone, "rule" : self.__add_rule, "nat" : self.__add_nat_rule }
        
        c = Config("test.conf", func)
        c.parse()
        
        self.__iptables.clean()
        self.__iptables.setup()        

f = Firewall()
f.enable()