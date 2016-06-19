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

emissores = {}
exibidores = {}

def get_msg(num):
    return {
        0: "OI",
        1: "FLW",
        2: "MSG",
        3: "OK",
        4: "ERRO",
        5: "QEM",
        6: "OKQEM"
    }[num]


# SERVER TODO:
#  - CLEAN CODE - REMOVE ALL UNNECESSARY THINGS FROM EXAMPLES
#  - CHECK IF ID IS THE CORRECT ONE BEFORE SENDING MESSAGE
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
            fmt_str = "!hhhhh140s"
            msg_size = struct.Struct(fmt_str).size
            data = s.recv(msg_size)
            if data:
                #msg_bytes = struct.pack(fmt_str, *fields_list)
                fields_list = struct.unpack(fmt_str, data) 
                data = fields_list
                print 'received "%s" from %s' % (get_msg(data[0]), s.getpeername()) 

                # received an OI
                if(data[0] == 0):  
                    # add to the exibidores list
                    existe = False
                    if(data[1] > 1000):
                        if data[1] not in exibidores:
                            exibidores[data[1]] = s.getpeername()[0]
                            print exibidores
                        else:
                            existe = True 

                    if(data[1] > 1 and data[1]< 1000):
                        if data[1] not in emissores:
                            emissores[data[1]] = s.getpeername()[0]
                            print emissores
                        else:
                            existe = True   


                    if not existe:

                        fmt_str = "!hhhhh140s"
                        origin_id = 0          # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                        destination_id = data[1]   # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                        sequence_id = 0         # (4 bytes) mantem estado entre os pares e permite a implementacao da entrega confiavel para-e-espera
                        #timestamp = next_msg[4]  # (4 bytes) except for messages of type OK
                        size_msg = 0
                        msg = ""

                        msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, size_msg, msg)

                        message_queues[s].put(msg_bytes)

                    else:
                        print "ja existe esse id" #retornar erro

                        fmt_str = "!hhhhh140s"
                        origin_id = 0          # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                        destination_id = data[1]   # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                        sequence_id = 0         # (4 bytes) mantem estado entre os pares e permite a implementacao da entrega confiavel para-e-espera
                        #timestamp = next_msg[4]  # (4 bytes) except for messages of type OK
                        size_msg = 0
                        msg = ""

                        msg_bytes = struct.pack(fmt_str, ERRO, origin_id, destination_id, sequence_id, size_msg, msg)  

                        message_queues[s].put(msg_bytes)



                # received an FLW
                if(data[0] == 1):   
                    # remove from the exibidores list
                    del exibidores[data[1]]
                    print exibidores

                    print 'closing', client_address, 'after FLW'
                    # Stop listening for input on the connection
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del message_queues[s]

                    msg_byte

                    fmt_str = "!hhhhh140s"
                    origin_id = 0          # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                    destination_id = data[1]   # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                    sequence_id = 0         # (4 bytes) mantem estado entre os pares e permite a implementacao da entrega confiavel para-e-espera
                    #timestamp = next_msg[4]  # (4 bytes) except for messages of type OK
                    size_msg = 0
                    msg = ""

                    msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, size_msg, msg)

                    message_queues[s].put(msg_bytes)


                # received an MSG
                if(data[0] == 2):

                    fmt_str = "!hhhhh140s"
                    origin_id = data[1]          # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                    destination_id = data[2]   # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                    sequence_id = data[3]         # (4 bytes) mantem estado entre os pares e permite a implementacao da entrega confiavel para-e-espera
                    #timestamp = next_msg[4]  # (4 bytes) except for messages of type OK

                    size_msg = data[4]
                    msg = data[5]

                    msg_bytes = struct.pack(fmt_str, MSG, origin_id, destination_id, sequence_id, size_msg, msg)   

                    message_queues[s].put(msg_bytes)

                    fmt_str = "!hhhhh140s"
                    origin_id = 0          # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                    destination_id = data[1]   # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
                    sequence_id = data[3]         # (4 bytes) mantem estado entre os pares e permite a implementacao da entrega confiavel para-e-espera
                    #timestamp = next_msg[4]  # (4 bytes) except for messages of type OK

                    size_msg = 0
                    msg = ""

                    msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, size_msg, msg)

                    message_queues[s].put(msg_bytes)
                
                
                
                if s not in outputs:
                    outputs.append(s)
                
    # Handle outputs
    for s in writable:
        try:
            fmt_str = "!hhhhh140s"
            next_msg2 = message_queues[s].get_nowait()
            next_msg = struct.unpack(fmt_str, next_msg2)
            
        except Queue.Empty:
            # No messages waiting so stop checking for writability.
            print 'output queue for', s.getpeername(), 'is empty'
            outputs.remove(s)
        else:
            # if it is OI, FLW or MSG

            if(next_msg[0] == 0 or next_msg[0] == 1):
                print 'sending "OK" to', str(next_msg[1]), str(s.getpeername())
            if(next_msg[0] == 2):
                print 'sending "MSG" to', str(next_msg[2]), str(s.getpeername())
            if(next_msg[0] == 5): #SE RECEBER UMA QEM
                print 'sending "OKQEM" to', str(s.getpeername())


            print "sending"
            s.send(next_msg2)

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

