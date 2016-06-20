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



# GET EXIBIDOR ID
def getExibidorID():
  print "Enter exibidor ID: "
  id_exibidor = input()
  while (id_exibidor < 1000):
    print "Enter exibidor ID: "
    id_exibidor = input()
  return id_exibidor


# SEND OI MESSAGE
def sendOI(id_exibidor, sequence_id):
  origin_id = id_exibidor     # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  destination_id = 0       # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  timestamp = (int(time.time()))

  fmt_str = "!HHHII"

  msg_bytes = struct.pack(fmt_str, OI, origin_id, destination_id, sequence_id, timestamp)

  print 'LOG: Sending OI to', destination_id
  s.send(msg_bytes)



# SEND FLW MESSAGE
def sendFLW(id_exibidor, sequence_id):
  origin_id = id_exibidor     # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  destination_id = 0       # (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
  timestamp = (int(time.time()))

  fmt_str = "!HHHII"

  msg_bytes = struct.pack(fmt_str, FLW, origin_id, destination_id, sequence_id, timestamp)

  print 'LOG: Sending FLW to', destination_id
  s.send(msg_bytes)




# RECEIVE RESPONSE FROM MESSAGE
def receive():
  fmt_str = "!HHHIIH140s"
  data_received = s.recv(1024)
  #msg_bytes = struct.pack(fmt_str, *fields_list)

  fields_list = struct.unpack_from("!HHHII", data_received) 
  data = get_msg(fields_list[0])

  print 'LOG: Received', data, 'from', fields_list[1]

  if(data == "MSG"):
    fields_list = struct.unpack(fmt_str, data_received) 
    print "-------------------------------------------------------"
    print "|   Message from", str(fields_list[1]).zfill(3), "                                 |"
    print "-------------------------------------------------------"
    print "|  ", fields_list[6].ljust(47)[0:46]
    print "|  ", fields_list[6].ljust(47)[47:93]
    print "|  ", fields_list[6].ljust(47)[94:]
    print "-------------------------------------------------------"
    print


  if(data == "OKQEM"):
    fmt_str = "!HHHIIH"
    fields_list = struct.unpack_from(fmt_str, data_received) 

    print "-------------------------------------------------------"
    print "|   QEM message requested by", str(fields_list[1]).zfill(3), "                     |"
    print "-------------------------------------------------------"

    for i in xrange(fields_list[5]):
      fmt_str += "H"
      fields_list = struct.unpack_from(fmt_str, data_received) 
      print "|   ID:",  fields_list[i+6]

    print "-------------------------------------------------------"
    print
  return data



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
  id_exibidor = getExibidorID()

  sequence_id = 0
  sendOI(id_exibidor, sequence_id)
  sequence_id += 1

  data = receive()

  # TODO: SERVER RETURN ERRO WHEN ID IS TAKEN
  while (data == "ERRO"): # Error with id, ask for a new one
    id_exibidor = getExibidorID()

    sendOI(id_exibidor, sequence_id)
    sequence_id += 1

    data = receive()

  while(data != "FLW"):
    data = receive()

  sendFLW(id_exibidor, sequence_id)
  sequence_id += 1

  data = receive()
  if(data == "OK"):
    s.close()

