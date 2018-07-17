import socket

s = socket.socket()
s.bind(('10.0.0.7', 30000))
s.listen(5)
c, addr = s.accept()
print(addr)
while(True):
    m = c.recv(1024)
    print(m.decode('UTF-8'))
##    m = c.send('hello'.encode('UTF-8'))
