import socket
import select
import Queue
import struct

HOST = ''              # Endereco IP do Servidor
PORT = 55555            # Porta que o Servidor esta

OI = 0
FLW = 1
MSG = 2
OK = 3
ERRO = 4
QEM = 5
OKQEM = 6


# SERVER TODO:
#  - CLEAN CODE - REMOVE ALL UNNECESSARY THINGS FROM EXAMPLES
#  - TABLE TO TRANSLATE ID TO IP ADDRESS - ID IS RECEIVED ON OI MESSAGES
#  - RESPOND WITH ERRO WHEN ID IS TAKEN
#  - SEND MESSAGE TO THE EXIBIDOR

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = (HOST, PORT)
print 'starting up on %s port %s' % server_address
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# Sockets from which we expect to read
inputs = [ server ]

# Sockets to which we expect to write
outputs = [ ]

# Outgoing message queues (socket:Queue)
message_queues = {}



while inputs:
    # Wait for at least one of the sockets to be ready for processing
    print '\nwaiting for the next event'
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    # Handle inputs
    for s in readable:

        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print 'new connection from', client_address 
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = Queue.Queue()
        else:
            fmt_str = "!hhhh"
            msg_size = struct.Struct(fmt_str).size
            data = s.recv(msg_size)
            if data:
                #msg_bytes = struct.pack(fmt_str, *fields_list)
                fields_list = struct.unpack(fmt_str, data) 
                data = fields_list
                if(data[0] == 0):  #received an OI
                    print data[1], s.getpeername()
                print 'received "%s" from %s' % (data, s.getpeername())
                message_queues[s].put(data)
                
                if s not in outputs:
                    outputs.append(s)
            else:
                # Interpret empty result as closed connection
                print 'closing', client_address, 'after reading no data'
                # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

                # Remove message queue
                del message_queues[s]
    # Handle outputs
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except Queue.Empty:
            # No messages waiting so stop checking for writability.
            print 'output queue for', s.getpeername(), 'is empty'
            outputs.remove(s)
        else:
            # if it is OI, FLW or MSG
            if(next_msg[0] == 0 or next_msg[0] == 1 or next_msg[0] == 2):
                print 'sending "OK" to', str(s.getpeername())
                fmt_str = "!hhhh"
                origin_id = 0          # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                destination_id = next_msg[1]   # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                sequence_id = 0         # (4 bytes) mantem estado entre os pares e permite a implementacao da entrega confiavel para-e-espera
                #timestamp = next_msg[4]  # (4 bytes) except for messages of type OK
                msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id)

                s.send(msg_bytes)

    # Handle "exceptional conditions"
    for s in exceptional:
        print  'handling exceptional condition for', s.getpeername()
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        # Remove message queue
        del message_queues[s]
