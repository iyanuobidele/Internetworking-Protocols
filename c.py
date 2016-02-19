import socket
import sys
import select
from communication import send, receive

BUFSIZ = 1024

class Client(object):
    """ A simple command line chat client using select """

    def __init__(self, name, host='127.0.0.1', port=6530):
        self.name = sys.argv[1]
        self.flag = False
        self.port = int(port)
        self.host = host
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print 'Connected to chat server@%d' % self.port
            send(self.sock,'NAME: ' + self.name) 
            data = receive(self.sock)
            addr = data.split('Client: ')[1]
            self.prompt = '[' + '@'.join((self.name, addr)) + ']> '
        except socket.error, e:
            print 'Could not connect to chat server @%d' % self.port
            sys.exit(1)

    def connection(self):

        while not self.flag:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                # Wait for input from stdin & socket
                inputready, outputready,exceptrdy = select.select([0, self.sock], [],[])
                
                for i in inputready:
                    if i == 0:
                        data = sys.stdin.readline().strip()
                        if data: send(self.sock, data)
                    elif i == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print 'Shutting down!'
                            self.flag = True
                            break
                        else:
                            sys.stdout.write(data + '\n')
                            sys.stdout.flush()
                    else:
                        print 'Interrupted....Goodbye !'
                        self.sock.close()
                        break
                            
            except KeyboardInterrupt:
                print 'Interrupted....Goodbye !'
                self.sock.close()
                break

              

                       
            
if __name__ == "__main__":
    import sys

    if len(sys.argv)<2:
        sys.exit('Usage: %s Connect with your Nickname...e.g \"Drake_fan\"' % sys.argv[0])
        
    client = Client(sys.argv[1])
    client.connection()
