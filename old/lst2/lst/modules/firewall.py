#-*- coding: utf-8 -*-

from lst.lib.iptables import IPTables, Zone, Rule

class Module:    
    def __init__(self, config, args = []):
        self.__config = config        
        self.__ipt = IPTables()
    
    def __ipt_setup(self):
        # Dodajemy strefy
        for zone in self.__config.get("zones.conf"):
            z = Zone()
            z.name = zone[0]
            z.iface = zone[1]
            z.cidr = zone[2]
            self.__ipt.add_zone(z)
        
        for rule in self.__config.get("rules.conf"):
            r = Rule()
            r.action = rule[0]
            r.source = self.__ipt.lookup_zone(rule[1])
            r.dest = self.__ipt.lookup_zone(rule[2])
            r.params = rule[3:]
            self.__ipt.add_rule(r)
            
        for nat in self.__config.get("nat.conf"):
            r = Rule()
            r.action = nat[0]
            r.source = self.__ipt.lookup_zone(nat[1])
            r.dest = self.__ipt.lookup_zone(nat[2])
            r.params = nat[3:]
            self.__ipt.add_nat(r)
            
        self.__ipt.init()

    def start(self):
        self.__ipt_setup()
        return True    
    
    def stop(self):
        self.__ipt.clean()
        return True
    
    def restart(self):
        self.__ipt.clean()
        self.__ipt_setup()
        return True
    