import socket as sock, sys,select, msvcrt

uName,host,port = sys.argv[1:]
port = int(port)
print(uName,host,port)
def getMsg():
    print("You:")
    
def start_client():
    print("started")
    cs = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    cs.connect((host,port))
    cs.sendto(uName.encode(), (host,port))
    while(True):
        read_sockets, write_sockets, error_sockets = select.select([cs] , [], [],0)	
        for s in read_sockets:
            data = s.recv(4096)
            print(data.decode())
        num = 0
        done = False
        while not done and num<500:
            num += 1

            if msvcrt.kbhit():
                msg = input("You:")
                done = True
                msg = msg.encode()
                cs.send(msg)


if __name__ == "__main__":
    start_client()



