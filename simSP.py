#!/usr/bin/python3

from socket import *
import time



def listToString(s):
    # initialize an empty string
    str1 = ""
    result = str1.join(map(str, s))
    # return string
    return result

def ControlSum(bytebuff):
    x = 0
    for byte_str in bytebuff:
    	x += ord(byte_str)
    result = x and 255
    return chr(result)

def WriteCoM(bytebuff):
    writestr = bytebuff + [ControlSum(bytebuff)]
    return listToString(writestr).encode('raw_unicode_escape')

def SendMess(bytebuff,socket,adr):
    data = WriteCoM(bytebuff)
    socket.sendto(data, adr)

def extract_ip():
    st = socket(AF_INET, SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def ReadMess(socket):
    data = socket.recvfrom(10)
    return data

host = '192.168.1.64'
port = 7777
adr = (host, port)
udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind((extract_ip(),port))

int
while True:
    data = udp_socket.recvfrom(7)[0]
    print('RX: ', data)
    if data == WriteCoM(['#', '\x03', 'E', '\x00']):
        
        tx_data = ['!','5','E',chr(int('00011100',2)),chr(int('00101011',2)),chr(int('01100010',2))]
        print('TX:',WriteCoM(tx_data))
        SendMess(tx_data,udp_socket,adr)
    elif data == WriteCoM(['#', '\x03', 'E', '\x01']):
        
        tx_data = ['!','5','E',chr(int('00011100',2)),chr(int('00100001',2)),chr(int('00101010',2))]
        print('TX:',WriteCoM(tx_data))
        SendMess(tx_data,udp_socket,adr)
    elif data == WriteCoM(['#', '\x03', 'P', '\x00']):
        
        tx_data = 'OK'
        udp_socket.sendto(tx_data.encode('raw_unicode_escape'), adr)
        print('TX:',tx_data)
    else:
    	tx_data = 'E2'
    	udp_socket.sendto(tx_data.encode('raw_unicode_escape'), adr)
    	print('TX:',tx_data)
     	 
        


