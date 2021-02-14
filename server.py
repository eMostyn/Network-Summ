import socket as sock
import sys
import select
import time

port = int(sys.argv[1])
conns = {}
host = "127.0.0.1"
welcomeMessage = "/info Welcome to the chat server!" + "\n"


def start_server():
    #Creates the log file if not existing, opens if for reading if it does
    logFile = open("server.log.", "w")
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as s:
        #Start the server, bind it to the specified port and address and listen out for any connections
        print("Started")
        s.bind((host, port))
        print("Server Ready")
        logFile.write("[" + getTime() + "] " + "Server Opened \n")
        s.listen()
        print('listening on', (host, port))
        conns[s] = "SERVER"
        while 1:
            #Get sockets
            try:
                rSocks, wSocks, eSocks = select.select(conns.keys(), [], [], 1)
            # Server Closed
            except KeyboardInterrupt:
                print("Server Closed")
                logFile.write("[" + getTime() + "] " + "Server Closed \n")
                logFile.close()
                sys.exit()

            # In the case the server closes unexpectedly/crashes
            except Exception as e:
                #Print error to console & log file
                print("[" + getTime() + "] " + str(e) + "\n")
                logFile.write("[" + getTime() + "] " + str(e) + "\n")
                logFile.close()
                #Attempt to close all remaining sockets
                for socket in conns.keys():
                    socket.close()
                sys.exit()
            #For each listening socket
            for rSock in rSocks:
                #New connection 
                if rSock == s:
                    #Accept the connection, add the username to the dictionary of connections
                    newSock, addr = s.accept()
                    uName = newSock.recv(1024).decode()
                    conns[newSock] = uName
                    #Makes sure username cannot initally be blank "" or " " etc
                    if(not uName.isspace()):
                        #Send the welcome message and then print the new user message to console & logfile
                        newSock.send(welcomeMessage.encode())
                        print(uName + " has connected to the server. With IP: " + addr[0] + " At Port: " + str(addr[1]))
                        logFile.write("[" + getTime() + "] " + uName + " has connected to the server. With IP: " + addr[0] + " At Port: " + str(addr[1]) + "\n")
                        #Inform other users of new user
                        joinMessage(uName, newSock, s)
                    #Send an error message 
                    else:
                        errorMessage = "/error Please set a valid username"
                        newSock.send(errorMessage.encode())
                #Existing user sends message
                else:
                    try:
                        data = rSock.recv(1024)
                        #Data is valid
                        if data:
                            #Get the data, from that the username
                            data = data.decode()
                            uName = conns[rSock]
                            #Split the data to get command & message
                            split = (data.strip()).split(" ")
                            command = split[0]
                            message = data[len(command)+1:]
                            #Send the list of users
                            if(command == "/list"):
                                sendUsers(uName, rSock)
                            #User is updating username
                            elif(command == "/info"):
                                    #Gets the new username
                                    newUser = message.split("\n")[0]
                                    # If the username is not currently in use
                                    if(newUser not in conns.values()):
                                        #Inform the users of the change and update dict
                                        updateUsers(uName, newUser, rSock, s)
                                        logFile.write("[" + getTime() + "] " + uName + " is now " + newUser + "\n")
                                        conns[rSock] = newUser                                       
                                        #Tell user 
                                        rSock.send("/info Username changed successfully \n".encode())
                                    #Cant change
                                    else:
                                        rSock.send("/error Username already in use \n".encode())
                            #Username is blank 
                            elif uName.isspace() or uName == "":
                                rSock.send("/error Please set a username first \n".encode())          
                            else:
                                if(command == "/say"):
                                    #Write the message to logfile + send to all users
                                    logFile.write("[" + getTime() + "] " + uName + ": " + data[len(command)+1:])
                                    sendMessage(conns[rSock], message, rSock, s)
                                elif(command == "/msg"):
                                    #Find the recipients name from the data
                                    recipientName = split[1]
                                    message = message[len(recipientName)+1:]
                                    #If valid user
                                    if recipientName in conns.values():
                                        #Message to specified user + write to log file
                                        whisper(recipientName, message, uName)
                                        logFile.write("[" + getTime() + "] <" + uName + " ->" + recipientName + ">: "+message)
                                    else:
                                        rSock.send("/error No user connected with that name\n".encode())
                                else:
                                    rSock.send("/error Command not valid \n".encode())               
                    #Error with data
                    except Exception as e:
                        #Print on the error & left message
                        print(str(e))
                        uName = conns[rSock]
                        print(uName + " has left")
                        logFile.write("["+getTime()+"] " + uName + " has left"+"\n")
                        #Delete the socket from dict and close it
                        del conns[rSock]
                        rSock.close()
                        #Inform other users
                        leaveMessage(uName, s)
                        
def joinMessage(uName,sock,server):
    #Specify the message and print to console
    message = "/info ["+uName+"]"+" has joined!"+"\n"
    print(message)
    #For every other user, send the message
    for client in conns.keys():
        if((client != server)&(client!=sock)):
            client.send(message.encode())

def leaveMessage(uName, server):
    #Specify message and send to all clients
    message = "/info ["+uName+"]"+" has left!"+"\n"
    for client in conns.keys():
        if((client != server)):
            client.send(message.encode())
            
            
def sendMessage(uName, message, sock, server):
    #Add the senders username and sent to all other clients
    message = "/say <" + uName + "> " + ": " + message
    for client in conns.keys():
        if((client != server) & (client != sock)):
            client.send(message.encode())


def whisper(recipient, message, sender):
    message = "/msg <"+sender+" -> You>"+": "+message
    # In the list of usernames (conn values), find the index of the recipient's username, then the socket with be the corresponding index in keys
    recipientSocket = list(conns.keys())[list(conns.values()).index(recipient)]
    recipientSocket.send(message.encode())

    
def getTime():
    #Use time module to get system time for logging 
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time  
    

def sendUsers(uName, sock):
    #Sends list of all usernames not in invalid
    invalid = [uName, "SERVER"]
    otherUsers = ""
    for userName in conns.values():
        if(userName not in invalid):
            #Space seperated list
            otherUsers += " "+userName
    message = "/list"+str(otherUsers)
    sock.send(message.encode())


def updateUsers(oldUser, newUser, sock, server):
    #Send message about username change to all other clients
    message = "/info " + oldUser + " is now " + newUser + "\n"
    for client in conns.keys():
        if((client != server)&(client!=sock)):
            client.send(message.encode())


if __name__ == '__main__':
    start_server()
