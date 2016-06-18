import socket


HOST = '10.0.0.3'     # Endereco IP do Servidor
PORT = 55555            # Porta que o Servidor esta

messages = [ 'This is the second message. ',
             'It will be second sent ',
             'in second parts.',
             ]
server_address = (HOST, PORT)

# Create a TCP/IP socket
socks = [ socket.socket(socket.AF_INET, socket.SOCK_STREAM),
          socket.socket(socket.AF_INET, socket.SOCK_STREAM),
          ]

# Connect the socket to the port where the server is listening
print 'connecting to %s port %s' % server_address
for s in socks:
    s.connect(server_address)

for message in messages:

    # Send messages on both sockets
    for s in socks:
        print '%s: sending "%s"' % (s.getsockname(), message)
        s.send(message)

    # Read responses on both sockets
    for s in socks:
        data = s.recv(1024)
        print '%s: received "%s"' % (s.getsockname(), data)
        if not data:
            print 'closing socket', s.getsockname()
            s.close()



'''
tcp.connect(dest)
print 'Para sair use CTRL+X\n'
msg = raw_input()
while msg <> '\x18':
    tcp.send (msg)
    msg = tcp.recv(1024)
    print msg
    msg = raw_input()
tcp.close()
'''
