#-*- coding: utf-8 -*-
from base64 import b64decode
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib2

def redirect(url):
    return ( 301, { 'Location' : url}, '')

class ModuleHTTPHandler:      
    def __init__(self):
        self.urltable = { '/link1' : self.__link1, '/link2' : self.__link2 }
    
    def __link2(self, method, get, post, cookie):
        data = "GET: " + str(get) + "<br />"
        return ( 200, { 'Content-type' : 'text/html' }, data)
    
    def __link1(self, method, get, post, cookie):
        return ( 200, { 'Content-type' : 'text/html' }, 'Hello, world!<br /><a href="/link2">link2</a>')
    
    
def params_decode(data):
    result = { }
    
    for param in data.split('&'):  
        tmp = param.split('=')
        if len(tmp) > 1:
            result[urllib2.unquote(tmp[0])] = urllib2.unquote(tmp[1])
        else:
            result[urllib2.unquote(tmp[0])] = ''
            
    return result

def path_decode(url):
    tmp = url.split('?')
    data = { }
    
    if len(tmp) > 1:
        data = params_decode(tmp[1])
        
    return ( tmp[0], data )
    
# Ta klasa obsługuje jedynie autoryzacje, pozosrtale funcke przekazywane sa do innych modulow
class LstHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        auth = self.headers.get("Authorization")
        if auth:
            data = auth.split(" ")
            if data[0] == "Basic":
                authinfo = b64decode(data[1]).partition(':')
                
                # TODO: Sprawdz haslo w konfigu
                if authinfo[0] == "admin" and authinfo[2] == "admin":
                    tmp = path_decode(self.path)
                    if self.command == 'POST':
                        post = params_decode(self.rfile.read())
                    else:
                        post = ''
                        
                    cookie = params_decode(self.headers.get("Cookie", ""))                    
                    
                    path = tmp[0].split('/')
                    
                    try:
                        mod = __import__("lst.modules." + path[1], fromlist = [ 'ModuleHTTPHandler' ])
                        m = mod.ModuleHTTPHandler()
                        ( stat, headers, data ) = m.urltable[tmp[1]](self.command, tmp[1], post, cookie)
                    except KeyError:
                        self.send_error(404, 'Page not found')
                        return
                    except ImportError:
                        self.send_error(404, 'Module not found')
                        return
                    
                    self.send_response(stat)
                    for h in headers:
                        self.send_header(h, headers[h])
                    self.end_headers()
                    self.wfile.write(data)
                    return                    
                    
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="LST"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("401 | Unauthorized")

    def do_POST(self):
        pass
                        
if __name__ == '__main__':
    try:
        server = HTTPServer(('', 8080), LstHTTPRequestHandler)
        server.serve_forever()
    except:
        server.socket.close()
        