import socket
ip_address = '127.0.0.1'
port_number = 5555
hostname = socket.gethostname()

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect((ip_address,port_number))
client_socket.send(hostname.encode())
msg = ""
while msg!='bye':
    print('waiting for input from SRV')
    msg = client_socket.recv(1024).decode()
    print(msg)
    client_socket.send(msg.encode())
    

client_socket.close()