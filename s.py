import socket, string, sys
import os
import re, signal
import select, tempfile, time
from datetime import datetime
from optparse import OptionParser
from communication import send,receive
from others import *
 
    

class Server(object):

    # self.all = 'Global'    
    def __init__(self, portNo=6530, backlog=5):
        self.clients = 0
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('localhost',portNo))
        print 'Server is on Port ' + str(portNo) + '.....awaiting connection'
        self.server.listen(backlog)
        signal.signal(signal.SIGINT, self.interruptFromKeyboard)

    def interruptFromKeyboard(self, signum, frame):
        # Close the server
        print 'Shutting down server...'
        # Close existing client sockets
        for o in self.outputs:
            o.close()
        self.server.close()
        
        # return appropriate action
        # ceck aliveness, issue ping and pong messages, reset timer after every pong.
        # Parse all commands, and direct to appropriate functions.
        # implement maps proper and sending it and updating it etc.

    def changeNick(self, conn, name):
        addr = self.getaddr(conn)
        new_name = str(name) + str(addr)
        temp = list(self.clientMap[conn])
        temp[1] = new_name
        self.clientMap[conn] = tuple(temp)

    def send_alive(self, channelMap):
        self.channelMap = channelMap
        alive = 'PING'
        for key,[value1,value2] in self.channelMap:
            send(value2,alive)
        return 1
                         
    def getaddr(self, conn):
        # Return the printable name of the
        # client, given its socket...
        info = self.clientMap[conn]
        host, name = info[0], info[1]
        return host
    
    def connection(self):
        inputs = [self.server,sys.stdin]
        self.outputs = []
        running = 1
        now = time.time()
        channelMap = {'Global':[]} #declaring a map (Channel->[[name,socket],[name,socket]]) data structure such that it is accessible accross the class
        completeMap = {}
        while running:
            try:
                readingready,writingready,waitingexception = select.select(inputs, self.outputs, [])
            except select.error, e:
                break
            except socket.error, e:
                break
            for s in readingready:
                if s == self.server:
                    conn, addr = self.server.accept()
                    cname = receive(conn).split('NAME: ')[1]
                    print 'New connection from %s@%s' % (cname, addr[1])
                    self.clients += 1
                    send(conn, 'Client: ' + str(addr[1]))
                    inputs.append(conn)

                    can_name = cname + str(addr[1])
                    channelMap['Global'].append([can_name,conn])
                    completeMap = channelMap
                    
                    broadcast = 'Newbie Alert. %s just joined this IRC' % (can_name)                    
                    for o in self.outputs:
                        send(o, broadcast)
                    self.outputs.append(conn)

                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    if junk == 'DISCONNECT':
                        # Close the server
                        print 'Shutting down server...'
                        # Close existing client sockets
                        for o in self.outputs:
                            o.close()
                        self.server.close()
                    else:
                        running = 0
                
                else:
                    try:
                        data = receive(s)
                        if data:
                            if data == 'DISCONNECT':
                                print 'Client: %s just disconnected' % return_user_name(s, completeMap)
                                self.clients -= 1
                                s.close()
                                inputs.remove(s)
                                self.outputs.remove(s)
                                name = return_user_name(s, completeMap)
                                
                                exitbroadcast = '\n(%s just left the IRC)' % return_user_name(s, completeMap)
                                for o in self.outputs:
                                    send(o, exitbroadcast)
                                for key,values in completeMap.items():
                                    completeMap[key].remove([name,s])
                                for key,values in completeMap.items():
                                    if not values:
                                        completeMap.pop(key)
                            else:
                                parse(data, s, completeMap)
                        else:
                            print 'Client: %s just disconnected' % return_user_name(s, completeMap)
                            self.clients -= 1
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)
                            exitbroadcast = '\n(%s just left the IRC)' % return_user_name(s, completeMap)
                            for o in self.outputs:
                                send(o, exitbroadcast)

                    except socket.error, e:
                        inputs.remove(s)
                        self.outputs.remove(s)

                    
                                     
                        
                        

        self.server.close()

if __name__ == '__main__':
    Server().connection()
