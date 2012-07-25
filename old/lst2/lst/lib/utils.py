#-*- coding: utf-8 -*-
import re

# Funkcja zamienia adres w postaci 10.0.0.0/8 na postać 10.0.0.0 255.0.0.0.0
def cidr_unpack(cidr):
    data = cidr.split("/")
    mask = int(data[1])
    tmp = ((1 << (mask + 1)) - 1) << (32 - mask)
    
    mask = "%d.%d.%d.%d" % ((tmp >> 24) & 0xFF, (tmp >> 16) & 0xFF, (tmp >> 8) & 0xFF, tmp & 0xFF)
    
    return (data[0], mask)


# Sprawcza czy s jest adresem MAC
def is_mac(s):
    if re.match("[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}", s):
        return True
    else:
        return False 
    