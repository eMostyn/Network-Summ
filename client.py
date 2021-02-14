import socket as sock
import sys
import select
import tkinter as tk

uName,host,port = sys.argv[1:]
port = int(port)
interface = tk.Tk()
interface.title("Chat Window")

def send_message(userInput,chat,client):
    #Get the contents of the input box
    msg = userInput.get("1.0","end")
    encodedMsg = msg.encode()
    #Split the msg up to access command
    split = msg.split(" ")
    # If there was no space the command is the entire thing
    if(len(split)==1):
        command = split[0][:-1]
    # Else its the first of the split
    else:
        command = split[0]
    # If the msg isnt blank, stops client sending unnecesary messages
    if(not msg.isspace()):
        if(command == "/say"):
            # Send the message and put contents into chat box
            client.send(encodedMsg)
            chat.insert("end","<You> : "+msg[len(command)+1:])

        elif(command == "/msg"):
            if(len(split)>2):
                # Split the message and recipient and send to server
                client.send(encodedMsg)
                recipient = split[1]
                chat.insert("end","<You -> "+recipient+">: "+msg[len(command)+len(recipient)+2:],"whisper")
            # Either recipient or message wasnt specified
            else:
              chat.insert("end","Please enter a username & message \n","error")
        else:
            # Nothing special to be done so send message
            client.send(encodedMsg)
        # Clear the input
        userInput.delete("1.0","end")
            
    

def update_chat(client,chat,interface,userList):
    try:
        # Get sockets
        rSocks,wSocks,eSocks = select.select([client],[],[],1)
        for s in rSocks:
            # Incoming message from server
            data = s.recv(4096)
            if not data :
                print('\nDisconnected from chat server')
                sys.exit()
            else :
                #Decode the data and split it to get command and message part
                data= data.decode()
                split  = data.split(" ")
                command = split[0]
                message = data[len(command)+1:]
                #Another users sent message, print it
                if command == "/say":
                    chat.insert("end",message)
                #Server returned list of other users
                elif command == "/list":
                    #Split the usernames
                    otherUsers = data[len(command)+1:].split(" ")
                    #Update the relevant ui box
                    updateUserList(userList, otherUsers)
                # User messaged client directly
                elif command == "/msg":
                    # Insert it to ui box, with "whisper" tag to make different colour
                    chat.insert("end",message,"whisper")
                # User has joined/left/changed username
                elif command == "/info":
                    #If multiple messages sent quickly they arrive as one data with multiple lines
                    #Split into lines
                    lines = data.split("\n")
                    for i in range(0,len(lines)):
                      # Split the line into words
                      split = lines[i].split(" ")
                      # Get command and message
                      command = split[0]
                      message = lines[i][len(command)+1:]
                      # Insert only the message part
                      chat.insert("end",message,"info")
                      # Add new lines to all except the last line
                      if(i!= len(lines)-1):
                          chat.insert("end","\n")
                # Server returns an error regarding a previous message
                elif command == "/error":
                    # Again, if multiple sent can be multiple lines
                    lines = data.split("\n")
                    # Split the lines and show seperately, as above
                    for i in range(0,len(lines)):
                      split = lines[i].split(" ")
                      command = split[0]
                      message = lines[i][len(command)+1:]
                      chat.insert("end",message,"error")
                      if(i!= len(lines)-1):
                          chat.insert("end","\n")
        # Recall this update every second
        interface.after(1000, lambda: update_chat(client,chat,interface,userList))
    # Error has occured in the client, print the error message and close
    except Exception as e:
        print("Quitting due to: " + str(e))
        client.close()
        sys.exit()
    
def start_client():
    # Open the socket
    cs = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    # Try connect, print error message if cannot connect
    try:
        cs.connect((host,port))
        cs.sendto(uName.encode(), (host,port))
    except Exception as e:
        print("An error has occured: " + str(e)+ ".\nEither the server isn't running or the port/host addresses are incorrect.")
        sys.exit()
    # Create the ui
    interface,chatWindow,userList = createInterface(cs)
    # Update the ui 
    interface.after(1000, lambda: update_chat(cs,chatWindow,interface,userList))
    # Show user help commands
    printCommands()
    # Shows interface on screen
    interface.mainloop()
    update_chat(cs,chatWindow,interface,userList)
    # UI has been closed, quit
    print("Quitting")
    sys.exit()

def createInterface(cs):
    #Creates the scrollbar for the chat window
    scrollbarY = tk.Scrollbar(interface)
    scrollbarY.grid(row=0,column=4,sticky='ns')

    #Creates the chat window, sets it to top of screen
    chatWindow = tk.Text(interface, bd=1,width="50", height="8", font=("Gill Sans MT", 23),background = "#363194", foreground="#00ffe5",yscrollcommand=scrollbarY.set,wrap="word")
    chatWindow.grid(row=0, column=0,columnspan = 3)
    #Adds some different text colours for different types of messages
    chatWindow.tag_config('info', foreground="yellow")
    chatWindow.tag_config('whisper', foreground= "white")
    chatWindow.tag_config('error', foreground= "red")

    #Sets the scrollbar to work on the chat window
    scrollbarY.config(command=chatWindow.yview)
    
    #Top menu bar
    menubar = tk.Menu(interface)
    #Adds the option dropdown
    optionMenu = tk.Menu(menubar, tearoff=0)
    #Adds the options of the dropdown
    optionMenu.add_command(label="Help", command=printCommands)
    optionMenu.add_command(label="Disconnect",command = leaveChat)
    menubar.add_cascade(label="Options", menu=optionMenu)
    #Sets the menu to the menubar
    interface.config(menu=menubar)

    #Create user input box
    userInput = tk.Text(interface,bd=1,width="50", height="8",font=("Gill Sans MT", 16))
    userInput.grid(row=1, column=1,sticky = "sw",rowspan = 3)

    #Creates submit button
    submitButton = tk.Button(interface, text ="Submit", command= lambda: send_message(userInput,chatWindow,cs),width = "20",height= "2",font=("Gill Sans MT",12))
    submitButton.grid(row = 1,column=2,sticky = "ew")

    #Creates label for userlist
    userListLabel = tk.Label(interface,text="Current Users",height ="2",font=("Gill Sans MT",12))
    userListLabel.grid(row = 1,column = 0,sticky = "n")

    #Adds button to update the user list
    updateUsersButton = tk.Button(interface, text="Update Users",command = lambda:getUsers(cs),height = "1",font=("Gill Sans MT",12))
    updateUsersButton.grid(row = 1, column =0,sticky = "s")
    
    #User list which updates to show connected users
    userList = tk.Label(interface,text = "",font=("Gill Sans MT",12))
    userList.grid(row=2,column = 0,sticky = "n",rowspan = 2)

    #Create the change username label 
    changeUsernameLabel = tk.Label(interface,text="Change Username",height ="2",font=("Gill Sans MT",12))
    changeUsernameLabel.grid(row = 2,column = 2,sticky = "n")
    changeUsernameInput = tk.Text(interface,bd=1,height="1",width = "25",font=("Gill Sans MT",12))
    changeUsernameInput.grid(row=2,column = 2,sticky = "s")

    #Button to update username to contents of input
    userNameupdateButton = tk.Button(interface,text= "Update Name",width = "20",height= "2",font=("Gill Sans MT",12),command = lambda:updateUsername(cs,changeUsernameInput))
    userNameupdateButton.grid(row=3,column = 2)
    
    return interface,chatWindow,userList



def getUsers(cs):
    #Send relevant message to get users
    message = "/list"
    encodedMsg = message.encode()
    cs.send(encodedMsg)
    
    

def updateUserList(userList, otherUsers):
    #Gets the list of users and updates the list
    toSet = ""
    for user in otherUsers:
        toSet += user + "\n"
    userList['text']  = toSet


def updateUsername(cs,nameInput):
    #Set the relevant message and send to server
    message = "/info " + nameInput.get("1.0","end")
    cs.send(message.encode())
    #Clear input
    nameInput.delete("1.0","end")

def printCommands():
    #Create the help window
    helpWindow = tk.Tk()
    helpWindow.title("Help")
    #Always on top of chat window
    helpWindow.attributes("-topmost", True)
    #Lines represent help about commands
    lines = []
    lines.append("/say [msg] - Broadcasts message to all users \n")
    lines.append("/msg [recipient] [msg] - Whisper the message to one user \n")
    lines.append("/info [new name] - Change your username to a new name \n")
    lines.append("/list - List all currently connected users (excluding yourself)")
    #Create the text box to print text to
    helpText = tk.Text(helpWindow,bd=1,height = "4",width = "50",background = "#363194",foreground = "yellow",font=("Gill Sans MT",16))
    #For each of the line print it
    for line in lines:
        helpText.insert("end",line)
    helpText.grid(row=0,column = 0)
    helpWindow.mainloop()

def leaveChat():
    #Disconnected so close program
    sys.exit()
    
if __name__ == "__main__":
    start_client()



