#-*- coding: utf-8 -*-

import os
from lst.lib.utils import cidr_unpack

DHCPD_CONF = "/etc/dhcp/dhcpd.conf"
DHCPD_CONTROL = "/etc/init.d/dhcpd"

class Module:
    def __init__(self, config, args = []):
        self.__config = config        
        
    def __gen_dhcpd_conf(self):
        try:
            conf = open(DHCPD_CONF, "w")
        except IOError:
            return False
        
        conf.write("#\n")
        conf.write("# This file is autogenerated, please DON'T EDIT!\n")
        conf.write("#\n")

        conf.write("default-lease-time 6000;\n")
        conf.write("max-lease-time 7200;\n\n")

        conf.write("ddns-update-style none;\n\n")

        conf.write("authoritative;\n\n")
    
        for dhcp in self.__config.get("dhcp.conf"):  
            zone = [ zone for zone in self.__config.get("zones.conf") if zone[0] == dhcp[0] ]            
            if len(zone) < 1:
                print("dhcpd_setup: zone %s not exist!" % (dhcp[0]))
                continue
            
            zone = zone[0]
            subnet = cidr_unpack(zone[2])
            conf.write("\nsubnet %s netmask %s {\n" % (subnet[0], subnet[1]))
            conf.write("\trange %s %s;\n" % (dhcp[1], dhcp[2]))
            
            for opt in dhcp[3:]:
                tmp = opt.split("=")
                conf.write("\toption %s %s;\n" % (tmp[0], tmp[1]))
            
            for host in self.__config.get("hosts.conf"):
                if host[0] != dhcp[0]:
                    continue
                
                conf.write("\n\thost %s {\n" % (host[1]))
                conf.write("\t\tfixed-address %s;\n" % (host[2]))
                conf.write("\t\thardware ethernet %s;\n" % (host[3]))
                conf.write("\t}\n")
            
            conf.write("}\n")
            
        conf.close()
        return True
    
    def start(self):
        self.__gen_dhcpd_conf()        
        os.system("%s start" % (DHCPD_CONTROL))
        return True
    
    def stop(self):
        os.system("%s stop" % (DHCPD_CONTROL))
        return True
    
    def restart(self):
        self.__gen_dhcpd_conf()        
        os.system("%s restart" % (DHCPD_CONTROL))
    