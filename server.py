import socket as sock, sys, select
port = int(sys.argv[1])
conns = {}
host = "127.0.0.1"
def start_server():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as s:
        #s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
        print("Started")
        s.bind((host,port))
        print("Server Ready")
        s.listen(5)
        print('listening on', (host, port))
        conns["SERVER"] =  s
        while True:
            rSocks,wSocks,eSocks = select.select(conns.values(),[],[])
            for rSock in rSocks:
                if rSock == s:
                    newSock,addr = s.accept()
                    uName = newSock.recv(1024).decode()
                    conns[uName] = newSock
                    print(addr)
                    print(uName + " has connected to the server. With IP: "+addr[0] + " At Port: "+str(addr[1])) 


def newClient(sock,addr):
    print(sock,addr)




if __name__ == '__main__':
    start_server()
