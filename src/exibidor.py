import socket
import struct

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
	origin_id = id_exibidor 		# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	destination_id = 0 			# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	#TIMESTAMP - COMO COLOCAR UNS SHORT DE 4 BYTES NO FORMATO


	fmt_str = "!HHHI"

	msg_bytes = struct.pack(fmt_str, OI, origin_id, destination_id, sequence_id)

	print str(s.getsockname()) + ': sending OI'
	s.send(msg_bytes)


# SEND FLW MESSAGE
def sendFLW(id_exibidor, sequence_id):
	origin_id = id_exibidor 		# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	destination_id = 0 			# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	#TIMESTAMP - COMO COLOCAR UNS SHORT DE 4 BYTES NO FORMATO

	fmt_str = "!HHHI"

	msg_bytes = struct.pack(fmt_str, FLW, origin_id, destination_id, sequence_id)

	print str(s.getsockname()) + ': sending FLW'
	s.send(msg_bytes)



# RECEIVE RESPONSE FROM MESSAGE
def receive():
	fmt_str = "!HHHIH140s"
	data_received = s.recv(1024)
	#msg_bytes = struct.pack(fmt_str, *fields_list)

	fields_list = struct.unpack_from("!HHHI", data_received) 
	data = get_msg(fields_list[0])


	print '%s: received %s' % (s.getsockname(), data)

	if(data == "MSG"):
		fields_list = struct.unpack(fmt_str, data_received) 
		print "Message from", str(fields_list[1]) + ':', fields_list[5]

	if(data == "MSG" and fields_list[5] == 'flw'):
		return "FIM"
	return data


# CREATE AND CONNECT SOCKET
server_address = (HOST, PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'connecting to %s port %s' % server_address
s.connect(server_address)



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

while(data[0] != "FIM"):
	data = receive()

	


sendFLW(id_exibidor, sequence_id)
sequence_id += 1

data = receive()
if(data == "OK"):
	s.close()

