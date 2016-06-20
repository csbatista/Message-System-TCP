#!/usr/bin/env python
# coding: utf-8

import socket
import select
import Queue
import struct
import time

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



# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = (HOST, PORT)
print 'LOG: Starting up on %s port %s' % server_address
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# Sockets from which we expect to read
inputs = [ server ]

# Sockets to which we expect to write
outputs = [ ]

# Outgoing message queues (socket:Queue)
message_queues = {}



def process_oi(fmt_str, data, data_received, s):
  # add to the exibidores list
  existe = False
  if(data[1] > 999):
    if data[1] not in exibidores:
      exibidores[data[1]] = s
      #print exibidores
    else:
      existe = True 
  
  # add to emissores list
  if(data[1] > 0 and data[1]< 1000):
    if data[1] not in emissores:
      emissores[data[1]] = s
      #print emissores
    else:
      existe = True   
  
  if not existe:
    fmt_str = "!HHHII"
    origin_id = 0          
    destination_id = data[1]  # respond
    sequence_id = data[3]     # use same sequence id 
    timestamp = data[4]   # OK uses the same timestamp

    msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, timestamp)
    
    message_queues[s].put(msg_bytes)
  
  else:
    #print "ja existe esse id" #retornar erro
    
    fmt_str = "!HHHII"
    origin_id = 0          # from server
    destination_id = data[1]   # respond
    sequence_id = data[3]         # use same sequence id
    timestamp = data[4]  # Erro uses the same timestamp
    
    msg_bytes = struct.pack(fmt_str, ERRO, origin_id, destination_id, sequence_id, timestamp)  
    
    message_queues[s].put(msg_bytes)



def process_flw(fmt_str, data, data_received, s):
  
  if (data[2] == 0):
    # remove from the emissores list
    if(data[1] > 1 and data[1] < 1000):
      del emissores[data[1]]
      #print emissores
    if(data[1] > 999):
      del exibidores[data[1]]
      #print exibidores
    
    print 'LOG: Closing', data[1], 'after FLW'
    
    fmt_str = "!HHHII"
    origin_id = 0              # from server
    destination_id = data[1]   # respond
    sequence_id = data[3]      # use same sequence id
    timestamp = data[4]  # OK uses te same timestamp
    
    msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, timestamp)
    
    message_queues[s].put(msg_bytes)
  else:
    if(data[2] in exibidores and data[1] in emissores and emissores[data[1]] == s):
        origin_id = data[1]          # origin is the same
        destination_id = data[2]     # destination is the same
        sequence_id = data[3]        # sequence number is the same
        timestamp = (int(time.time()))
        
        msg_bytes = struct.pack(fmt_str, FLW, origin_id, destination_id, sequence_id, timestamp)   
        
        socket_exibidor = exibidores[data[2]]
        message_queues[socket_exibidor].put(msg_bytes)
        if socket_exibidor not in outputs:
          outputs.append(socket_exibidor)
        
        
        fmt_str = "!HHHII"
        origin_id = 0               # from server
        destination_id = data[1]    # respond
        sequence_id = data[3]       # same sequence id
        timestamp = data[4]  # OK uses the same timestamp

        msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, timestamp)

        message_queues[s].put(msg_bytes)
    else:
        fmt_str = "!HHHII"
        origin_id = 0              # from server
        destination_id = data[1]   # respond
        sequence_id = data[3]      # same sequence_id
        timestamp = data[4]  # Erro uses same timestamp

        msg_bytes = struct.pack(fmt_str, ERRO, origin_id, destination_id, sequence_id, timestamp)
        message_queues[s].put(msg_bytes)

          

def process_msg(fmt_str, data, data_received, s):
  fmt_str = "!HHHIIH140s"
  fields_list = struct.unpack(fmt_str, data_received) 
  data = fields_list


  if(data[2] == 0 or (data[2] in exibidores and (data[1] in emissores and emissores[data[1]] == s))):
  
      if(data[2] > 0): # if it is only for one exibidor
        origin_id = data[1]          # same origin
        destination_id = data[2]     # same dest
        sequence_id = data[3]        # keep seq id
        timestamp = (int(time.time()))
        
        size_msg = data[5]
        msg = data[6]
        
        msg_bytes = struct.pack(fmt_str, MSG, origin_id, destination_id, sequence_id, timestamp, size_msg, msg)   
        
        socket_exibidor = exibidores[data[2]]
        message_queues[socket_exibidor].put(msg_bytes)
        if socket_exibidor not in outputs:
          outputs.append(socket_exibidor)
      
      else: # if it is for all exibidores
        #print len(exibidores)
        for id_exibidor in exibidores:
          origin_id = data[1]          
          destination_id = id_exibidor # each dest  
          sequence_id = data[3]        # keep seq id    
          timestamp = (int(time.time()))
          
          size_msg = data[5]
          msg = data[6]
          
          msg_bytes = struct.pack(fmt_str, MSG, origin_id, destination_id, sequence_id, timestamp, size_msg, msg)   
          
          socket_exibidor = exibidores[id_exibidor]
          message_queues[socket_exibidor].put(msg_bytes)
          if socket_exibidor not in outputs:
            outputs.append(socket_exibidor)

      fmt_str = "!HHHII"
      origin_id = 0             # from server
      destination_id = data[1]  # respond
      sequence_id = data[3]     # keep seq id
      timestamp = data[4]  # OK uses same timestamp

      msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, timestamp)
      message_queues[s].put(msg_bytes)

  else:
    fmt_str = "!HHHII"
    origin_id = 0             # from server
    destination_id = data[1]  # respond
    sequence_id = data[3]     # keep seq id
    timestamp = data[4]  # ERRO uses same timestamp

    msg_bytes = struct.pack(fmt_str, ERRO, origin_id, destination_id, sequence_id, timestamp)
    message_queues[s].put(msg_bytes)


  



def process_qem(fmt_str, data, data_received, s):
    if(data[2] in exibidores and data[1] in emissores and emissores[data[1]] == s):
      if(data[2] > 0): # if it is only for one exibidor
        origin_id = data[1]          # same origin
        destination_id = data[2]     # same dest
        sequence_id = data[3]        # keep seq id
        timestamp = data[4]  # OKQEM uses same timestamp

        fmt_str = "!HHHIIH" 

        size_msg = len(exibidores) + len(emissores)

        msg_bytes = struct.pack(fmt_str, OKQEM, origin_id, destination_id, sequence_id, timestamp, size_msg)   
        
        for id_emissor in emissores:
          msg_bytes += struct.pack('!H', id_emissor)
          print 'LOG: Adding', id_emissor

        for id_exibidor in exibidores:
          msg_bytes += struct.pack('!H', id_exibidor)
          print 'LOG: Adding', id_exibidor

        socket_exibidor = exibidores[data[2]]
        message_queues[socket_exibidor].put(msg_bytes)
        if socket_exibidor not in outputs:
          outputs.append(socket_exibidor)

      else: # if it is for all exibidores
        #print len(exibidores)
        for id_exibidor in exibidores:
          origin_id = data[1]          
          destination_id = id_exibidor   
          sequence_id = data[3] 
          timestamp = data[4]  # OKQEM uses same timestamp        

          fmt_str = "!HHHIIH" 

          size_msg = len(exibidores) + len(emissores)
      
          msg_bytes = struct.pack(fmt_str, OKQEM, origin_id, destination_id, sequence_id, timestamp, size_msg)   
          
          for id_emi in emissores:
            msg_bytes += struct.pack('!H', id_emi)

          for id_exi in exibidores:
            msg_bytes += struct.pack('!H', id_exi)

          socket_exibidor = exibidores[id_exibidor]
          message_queues[socket_exibidor].put(msg_bytes)
          if socket_exibidor not in outputs:
            outputs.append(socket_exibidor)
      
      fmt_str = "!HHHII"
      origin_id = 0             # from server
      destination_id = data[1]  # respond
      sequence_id = data[3]     # keep seq id
      timestamp = data[4]  # OK uses same timestamp

      msg_bytes = struct.pack(fmt_str, OK, origin_id, destination_id, sequence_id, timestamp)

      message_queues[s].put(msg_bytes)
    else:
        fmt_str = "!HHHII"
        origin_id = 0            # from server
        destination_id = data[1] # respond
        sequence_id = data[3]    # keep seq id
        timestamp = data[4]  # ERRO uses same timestamp

        msg_bytes = struct.pack(fmt_str, ERRO, origin_id, destination_id, sequence_id, timestamp)
        message_queues[s].put(msg_bytes)





def handle_inputs(readable):
  '''
    Handle the sockets select returned as ready to be read.
  '''
  
  for s in readable:
    if s is server:
      # A "readable" server socket is ready to accept a connection
      connection, client_address = s.accept()
      print 'LOG: New connection from', client_address 
      connection.setblocking(0)
      inputs.append(connection)

      # Give the connection a queue for data we want to send
      message_queues[connection] = Queue.Queue()
    else:
      fmt_str = "!HHHII"
      data_received = s.recv(1024)
      if data_received:
        fields_list = struct.unpack_from(fmt_str, data_received) 
        data = fields_list
        print 'LOG: Received %s from %s' % (get_msg(data[0]), data[1]) 
        
        # received an OI
        if data[0] == 0:  
          process_oi(fmt_str, data, data_received, s)
        
        # received an FLW
        if data[0] == 1:
          process_flw(fmt_str, data, data_received, s)
        
        # received an MSG
        if data[0] == 2:
          process_msg(fmt_str, data, data_received, s)
        
        # received and QEM
        if(data[0] == 5):
          process_qem(fmt_str, data, data_received, s)
        
        if s not in outputs:
            outputs.append(s)
      else:
        # Interpret empty result as closed connection
        # print 'LOG: Closing after reading no data'
        # Stop listening for input on the connection
        if s in outputs:
          outputs.remove(s)
        inputs.remove(s)
        s.close()
        
        # Remove message queue
        del message_queues[s]



def handle_outputs(writable):
  '''
    Handle the sockets select returned as ready to be written.
  '''
  
  for s in writable:
    try:
      fmt_str = "!HHHII"
      next_msg2 = message_queues[s].get_nowait()
      next_msg = struct.unpack_from(fmt_str, next_msg2)  
    except Queue.Empty:
      # No messages waiting so stop checking for writability.
      #print 'LOG: Output queue for', s.getpeername(), 'is empty'
      outputs.remove(s)
    else:
      # if it is OI, FLW or MSG
      if next_msg[0] == 3:
        print 'LOG: Sending OK to', str(next_msg[2])
      if next_msg[0] == 2:
        print 'LOG: Sending MSG to', str(next_msg[2])
        #print message_queues
      if next_msg[0] == 5 : #SE RECEBER UMA QEM
        print 'LOG: Sending OKQEM to', str(next_msg[2])     

      s.send(next_msg2)



def handle_exceptions(exceptional):
  '''
    Handle the sockets that raised an exception or some errror occurred.
  '''
  for s in exceptional:
    print  'LOG: Handling exceptional condition for', s.getpeername()
    # Stop listening for input on the connection
    inputs.remove(s)
    if s in outputs:
      outputs.remove(s)
    s.close()
    
    # Remove message queue
    del message_queues[s]




def main():
  while inputs:
    # Wait for at least one of the sockets to be ready for processing
    #print 'LOG: Waiting for the next event'
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    
    handle_inputs(readable)
    handle_outputs(writable)
    handle_exceptions(exceptional)



if __name__ == '__main__':
  main()
