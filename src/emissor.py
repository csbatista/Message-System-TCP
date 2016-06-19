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
	origin_id = id_emissor 		# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	destination_id = 0 			# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	#TIMESTAMP - COMO COLOCAR UNS SHORT DE 4 BYTES NO FORMATO

	fmt_str = "!HHHI"

	msg_bytes = struct.pack(fmt_str, OI, origin_id, destination_id, sequence_id)

	print str(s.getsockname()) + ': sending OI'
	s.send(msg_bytes)


# SEND FLW MESSAGE
def sendFLW(id_emissor, sequence_id):
	origin_id = id_emissor 		# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	destination_id = 0 			# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor
	sequence_id = 0 			# AINDA NAO ESTA SENDO INCREMENTADA
	#TIMESTAMP - COMO COLOCAR UNS SHORT DE 4 BYTES NO FORMATO

	fmt_str = "!HHHI"

	msg_bytes = struct.pack(fmt_str, FLW, origin_id, destination_id, sequence_id)

	print str(s.getsockname()) + ': sending FLW'
	s.send(msg_bytes)

# SEND MSG MESSAGE
def sendMSG(id_emissor, sequence_id):
	origin_id = id_emissor 		# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor

	print "What is the ID of the exibidor? (type 0 to broadcast the message to all exibidores)"
	destination_id = input()
	while(destination_id != 0 and destination_id < 1000):
		print "That is not a valid ID. Exibidor ID's should be bigger than 1000"
		print "What is the ID of the exibidor? (type 0 to broadcast the message to all exibidores)"
		destination_id = input()

	size_msg = 2
	print "Type the message (max 140 characters)"
	msg = raw_input()
	#TIMESTAMP - COMO COLOCAR UNS SHORT DE 4 BYTES NO FORMATO
	fmt_str = "!HHHIH140s"

	msg_bytes = struct.pack(fmt_str, MSG, origin_id, destination_id, sequence_id, size_msg, msg)

	print str(s.getsockname()) + ': sending MSG'
	s.send(msg_bytes)

# SEND QEM MESSAGE
def sendQEM(id_emissor, sequence_id):
	origin_id = id_emissor 		# (2 bytes) 0 for server, 1-999 for emissor and +1000 for exibidor

	print "What is the ID of the exibidor?"
	destination_id = input()
	while(destination_id != 0 and destination_id < 1000):
		print "That is not a valid ID. Exibidor ID's should be bigger than 1000"
		print "What is the ID of the exibidor?"
		destination_id = input()

	size_msg = 0
	msg = ""
	#TIMESTAMP - COMO COLOCAR UNS SHORT DE 4 BYTES NO FORMATO
	fmt_str = "!HHHIH140s"

	msg_bytes = struct.pack(fmt_str, QEM, origin_id, destination_id, sequence_id, size_msg, msg)

	print str(s.getsockname()) + ': sending MSG'
	s.send(msg_bytes)


# RECEIVE RESPONSE FROM OI MESSAGE
def receive():
	fmt_str = "!HHHI"
	data = s.recv(1024)
	#msg_bytes = struct.pack(fmt_str, *fields_list)

	fields_list = struct.unpack(fmt_str, data) 
	data = get_msg(fields_list[0])
	print '%s: received %s' % (s.getsockname(), data)
	return data

# SHOW OPTIONS
def showOptions():
	print "Choose an option:"
	print "(1) Send a message"
	print "(2) Build an QEM message"
	print "(3) Terminate exibidor"
	print "(0) Terminate this"


# CREATE AND CONNECT SOCKET
server_address = (HOST, PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'connecting to %s port %s' % server_address
s.connect(server_address)



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

showOptions()
op = input()
while(op != 0):
	

	if(op == 1):
		sendMSG(id_emissor, sequence_id)
		sequence_id += 1

		data = receive()

	if(op == 2):
		sendQEM(id_emissor, sequence_id)
		sequence_id += 1

		data = receive()

	showOptions()
	op = input()


sendFLW(id_emissor, sequence_id)
sequence_id += 1

data = receive()
if(data == "OK"):
	s.close()

