import socket as sock, sys

uName,host,port = sys.argv[1:]
port = int(port)
print(uName,host,port)
def start_client():
    print("started")
    cs = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    cs.connect((host,port))
    cs.sendto(uName.encode(), (host,port))


if __name__ == "__main__":
    start_client()
