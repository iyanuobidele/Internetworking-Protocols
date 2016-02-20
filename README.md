# Internetworking-Protocols
A Single Server, Multi-Client IRC implementation

Server {s.py}
Client {c.py}
Some important function Implementations {others.py, communication.py}

This IRC, allows creating rooms, joining rooms, leaving rooms, sending broadcast, posting messages to rooms and private message between clients. The clients are gracefully exited on a server crash. Also the server, can gracefully attend to a client disconnection by freeing up all the resources.

I have used the select.select threading method, which doesn't work well on windows OS because of the limitation of the Winsock library.

The code is pretty clear and intuitive, I believe.
