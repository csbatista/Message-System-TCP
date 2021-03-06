import socket
import struct
import time

HOST = '10.0.0.3'     # Endereco IP do Servidor
PORT = 55555            # Porta que o Servidor esta

OI = 0
FLW = 1
MSG = 2
OK = 3
ERRO = 4
QEM = 5
OKQEM = 6

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



# GET EMISSOR ID
def getEmissorID():
  print "Enter emissor ID: "
  id_emissor = input()
  while (id_emissor < 1 or id_emissor > 999):
    print "Enter emissor ID: "
    id_emissor = input()
  return id_emissor



# SEND OI MESSAGE
def sendOI(id_emissor, sequence_id):
  origin_id = id_emissor     # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  destination_id = 0       # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  timestamp = (int(time.time()))

  fmt_str = "!HHHII"

  msg_bytes = struct.pack(fmt_str, OI, origin_id, destination_id, sequence_id, timestamp)

  print 'LOG: Sending OI to', destination_id
  s.send(msg_bytes)



# SEND FLW MESSAGE
def sendFLW(id_emissor, sequence_id):
  origin_id = id_emissor     # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  destination_id = 0       # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  sequence_id = 0       # AINDA NAO ESTA SENDO INCREMENTADA
  timestamp = (int(time.time()))

  fmt_str = "!HHHII"

  msg_bytes = struct.pack(fmt_str, FLW, origin_id, destination_id, sequence_id, timestamp)

  print 'LOG: Sending FLW to', destination_id
  s.send(msg_bytes)



def sendExibidorFLW(id_emissor, sequence_id):
  origin_id = id_emissor     # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  sequence_id = 0       # AINDA NAO ESTA SENDO INCREMENTADA
  timestamp = (int(time.time()))

  print "What is the ID of the exibidor?"
  destination_id = input()
  while(destination_id != 0 and destination_id < 1000):
    print "That is not a valid ID. Exibidor ID's should be bigger than 1000"
    print "What is the ID of the exibidor?"
    destination_id = input()
  
  fmt_str = "!HHHII"
  
  msg_bytes = struct.pack(fmt_str, FLW, origin_id, destination_id, sequence_id, timestamp)
  
  print 'LOG: Sending FLW to', destination_id
  s.send(msg_bytes)



# SEND MSG MESSAGE
def sendMSG(id_emissor, sequence_id):
  origin_id = id_emissor     # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  
  print "What is the ID of the exibidor? (type 0 to broadcast the message to all exibidores)"
  destination_id = input()
  while destination_id != 0 and destination_id < 1000:
    print "That is not a valid ID. Exibidor ID's should be bigger than 1000"
    print "What is the ID of the exibidor? (type 0 to broadcast the message to all exibidores)"
    destination_id = input()


  timestamp = (int(time.time()))
  
  size_msg = 2
  while True:
    print "Type the message (max 140 characters)"
    msg = raw_input()
    if len(msg) > 140:
      print 'Message too big.'
    elif len(msg) == 0:
      print 'Write something'
    else:
      break
  
  #TIMESTAMP - COMO COLOCAR UNS SHORT DE 4 BYTES NO FORMATO
  fmt_str = "!HHHIIH140s"
  
  size_msg = len(msg)
  msg_bytes = struct.pack(fmt_str, MSG, origin_id, destination_id, sequence_id, timestamp, size_msg, msg)

  print 'LOG: Sending MSG to', destination_id
  s.send(msg_bytes)



# SEND QEM MESSAGE
def sendQEM(id_emissor, sequence_id):
  origin_id = id_emissor     # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor

  print "What is the ID of the exibidor?"
  destination_id = input()
  while(destination_id != 0 and destination_id < 1000):
    print "That is not a valid ID. Exibidor ID's should be bigger than 1000"
    print "What is the ID of the exibidor?"
    destination_id = input()

  timestamp = (int(time.time()))

  fmt_str = "!HHHII"

  msg_bytes = struct.pack(fmt_str, QEM, origin_id, destination_id, sequence_id, timestamp)

  print 'LOG: Sending MSG to', destination_id
  s.send(msg_bytes)




# RECEIVE RESPONSE FROM OI MESSAGE
def receive():
  fmt_str = "!HHHII"
  data = s.recv(1024)
  #msg_bytes = struct.pack(fmt_str, *fields_list)

  fields_list = struct.unpack(fmt_str, data) 
  data = get_msg(fields_list[0])

  print 'LOG: Received', data, 'from', fields_list[1]
  return data



# SHOW OPTIONS
def showOptions():
  print 
  print "-------------------------------------------------------"
  print "|    MENU                                             |"
  print "-------------------------------------------------------"
  print "|   (1) Send a message                                |"
  print "|   (2) Build an QEM message                          |"
  print "|   (3) Terminate exibidor                            |"
  print "|   (0) Terminate this                                |"
  print "-------------------------------------------------------"
  print "| Your option?", 





# CREATE AND CONNECT SOCKET
server_address = (HOST, PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'LOG: Connecting to %s port %s' % server_address

try:
  s.connect(server_address)
except socket.error, exc:
  print 'LOG: Exception caught, socket.error: %s' % exc
else:
  # GET ID EMISSOR AND START LOOP
  id_emissor = getEmissorID()

  sequence_id = 0
  sendOI(id_emissor, sequence_id)
  sequence_id += 1

  data = receive()

  # TODO: SERVER RETURN ERRO WHEN ID IS TAKEN
  while (data == "ERRO"): # Error with id, ask for a new one
    id_emissor = getEmissorID()

    sendOI(id_emissor, sequence_id)
    sequence_id += 1

    data = receive()
    if (data == "ERRO"):
      print
      print "-------------------------------------------------------"
      print "|   ERROR                                             |"
      print "-------------------------------------------------------"
      print "|   Error sending OI. Possible causes are:            |"
      print "|   - Chosen ID already in use                        |"
      print "|                                                     |"
      print "|   Please check and try again                        |"
      print "-------------------------------------------------------"
      print

  showOptions()
  op = input()
  while op != 0:
    if op == 1:
      sendMSG(id_emissor, sequence_id)
      sequence_id += 1
      data = receive()

      if(data == "ERRO"):
        print
        print "-------------------------------------------------------"
        print "|   ERROR                                             |"
        print "-------------------------------------------------------"
        print "|   Error sending message. Possible causes are:       |"
        print "|   - Incorrect exibidor ID                           |"
        print "|   - Incorrect origin ID                             |"
        print "|                                                     |"
        print "|   Please check and try again                        |"
        print "-------------------------------------------------------"
        print

    if op == 2:
      sendQEM(id_emissor, sequence_id)
      sequence_id += 1
      data = receive()

      if(data == "ERRO"):
        print
        print "-------------------------------------------------------"
        print "|   ERROR                                             |"
        print "-------------------------------------------------------"
        print "|   Error sending message. Possible causes are:       |"
        print "|   - Incorrect exibidor ID                           |"
        print "|   - Incorrect origin ID                             |"
        print "|                                                     |"
        print "|   Please check and try again                        |"
        print "-------------------------------------------------------"
        print

    if op == 3:
      sendExibidorFLW(id_emissor, sequence_id)
      sequence_id += 1
      data = receive()

      if(data == "ERRO"):
        print
        print "-------------------------------------------------------"
        print "|   ERROR                                             |"
        print "-------------------------------------------------------"
        print "|   Error sending message. Possible causes are:       |"
        print "|   - Incorrect exibidor ID                           |"
        print "|   - Incorrect origin ID                             |"
        print "|                                                     |"
        print "|   Please check and try again                        |"
        print "-------------------------------------------------------"
        print

    showOptions()
    op = input()

  sendFLW(id_emissor, sequence_id)
  sequence_id += 1

  data = receive()
  if(data == "OK"):
    s.close()

