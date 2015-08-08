#coding=utf-8 
import socket 
import select 
import sys 
import threading
import time
import logging
import time
import os
logsDir = "logs"
if not os.path.isdir(logsDir):
    os.mkdir(logsDir)
    
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='logs/logs.log',
                filemode='a+')
   
#target ip & port
to_addr = ('127.0.0.1', 9999)

class Proxy: 
    def __init__(self, addr): 
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.proxy.bind(addr) 
        self.proxy.listen(10) 
        self.inputs = [self.proxy] 
        self.route = {} 
   
    def serve_forever(self): 
        logging.info('proxy listen...')
        while True: 
            readable, _, _ = select.select(self.inputs, [], [])
            if len(readable) == 0:
                logging.info("no readable, sleep 3 seconds")
                time.sleep(3)
            for self.sock in readable: 
                try:
                    if self.sock == self.proxy: 
                        self.on_join() 
                    else:
                        try:
                            data = self.sock.recv(8192)
                        except Exception, e:
                            logging.error(str(e))
                            self.on_quit()
                            continue
                        
                        if not data: 
                            self.on_quit() 
                        else:
                            try:
                                self.route[self.sock].send(data)
                            except Exception, e:
                                logging.error(str(e))
                                self.on_quit()
                                continue
                except Exception, e:
                        logging.error(str(e))
                        #restart proxy
                        self.inputs = [self.proxy]
                        self.route = {}
   
    def on_join(self): 
        client, addr = self.proxy.accept() 
        logging.info("proxy client " + str(addr) + 'connect')
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        forward.connect(to_addr) 
        self.inputs += [client, forward] 
        self.route[client] = forward 
        self.route[forward] = client 
   
    def on_quit(self):
        ls = [self.sock]
        if self.sock in self.route:
            ls.append(self.route[self.sock])
        for s in ls:
            if s in self.inputs:
                self.inputs.remove(s)
            if s in self.route:
                del self.route[s] 
            s.close() 
            
def runProxy(port):
    try: 
        Proxy(('', port)).serve_forever()
    except KeyboardInterrupt: 
        logging.error("KeyboardInterrupt")
        return

#for threading
def start():
    t = threading.Thread(target=runProxy)
    t.start()
    return t
    pass

if __name__ == "__main__":
    #listen port
    port = 8192
    runProxy(port)
    pass
