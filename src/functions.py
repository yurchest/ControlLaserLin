from PyQt5.QtCore import QThread
from socket import *
from datetime import datetime


def get_current_time():
    now = datetime.now()
    current_time = now.strftime("[%H:%M:%S] ")
    return current_time

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


def binary_converted(data):
    datadec = []
    for x in data:
        datadec += [x]

    bin_conv = []
    for binx in data:
        bin_conv.append(bin(binx)[2:].zfill(8))
    return bin_conv


def strToBin(data):
    # data_arr = [None] * len(data)
    #
    # for i in range(len(data)):
    #     data_arr[i] = data[i]

    data_arr = bytearray(data)
    data_out = [0] * len(data)
    if len(data) > 6:
        data_out[0] = data_arr[0]
        data_out[1] = data_arr[1]
        data_out[2] = data_arr[2]
        data_out[3] = bin(data_arr[3])[2:].zfill(8)
        data_out[4] = bin(data_arr[4])[2:].zfill(8)
        data_out[5] = bin(data_arr[5])[2:].zfill(8)
        data_out[6] = data_arr[6]
        # data_out[6] = ord(ControlSum(str(data_arr)))
    return data_out


def listToString(s):
    # initialize an empty string
    str1 = ""
    result = str1.join(map(str, s))
    return result


def ControlSum(bytebuff):
    x = 0
    for byte_str in bytebuff:
        x += ord(byte_str)
    result = x
    return chr(result)


def WriteCoM(bytebuff):
    writestr = bytebuff + [ControlSum(bytebuff)]
    return listToString(writestr).encode('raw_unicode_escape')


def SendMess(bytebuff, socket, adr):
    data = WriteCoM(bytebuff)
    socket.sendto(data, adr)


def ReadMess(socket):
    data = socket.recvfrom(7)
    return data

def SendRead(bytebuff, socket, adr):
    SendMess(bytebuff, socket, adr)
    data = ReadMess(socket)[0]
    return data


