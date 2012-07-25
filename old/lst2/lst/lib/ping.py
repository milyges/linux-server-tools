import subprocess
import os

def ping_host(host, iface = None):
    args = ['ping', '-c1', '-q']
    if iface:
        args.append("-I %s" % (iface))
    args.append(host)
    fnull = open(os.devnull, 'w') 
    code = subprocess.call(args, stdout = fnull, stderr = fnull)
    fnull.close()
    return code
