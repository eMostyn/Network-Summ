import socket as sock, sys, select
port = int(sys.argv[1])
conns = {}
host = "127.0.0.1"
welcomeMessage = "Welcome to the chat server!"
def start_server():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as s:
        #s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
        print("Started")
        s.bind((host,port))
        print("Server Ready")
        s.listen(5)
        print('listening on', (host, port))
        conns[s] =  "SERVER"
        while 1:
            rSocks,wSocks,eSocks = select.select(conns.keys(),[],[])
            for rSock in rSocks:
                if rSock == s:
                    newSock,addr = s.accept()
                    uName = newSock.recv(1024).decode()
                    conns[newSock] = uName
                    newSock.send(welcomeMessage.encode())
                    print(uName + " has connected to the server. With IP: "+addr[0] + " At Port: "+str(addr[1]))
                    joinMessage(uName,newSock,s)
                else:
                    data = rSock.recv(1024).decode()
                    if data:
                        print(data)
                        sendMessage(conns[rSock],data,rSock,s)
                    else:
                        uName = conns[rSock]
                        print(uName + " has left")
                        leaveMessage(uName,s)
                        rSock.close()
                        del conns[rSock]

def joinMessage(uName,sock,server):
    message = "["+uName+"]"+" has joined!"
    for client in conns.keys():
        if((client != server)&(client!=sock)):
            client.send(message.encode())

def leaveMessage(uName,server):
    message = "["+uName+"]"+" has left!"
    for client in conns.keys():
        if((client != server)):
            client.send(message.encode())
            
def sendMessage(uName,message,sock,server):
    message = uName +": " + message
    for client in conns.keys():
        if((client != server)&(client!=sock)):
            client.send(message.encode())
        




if __name__ == '__main__':
    start_server()
