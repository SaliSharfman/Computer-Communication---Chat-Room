import sys
import time
from threading import Thread
from client import Client


name=input(f"Enter your name:\n")
def legal(name):
    if name==""or name is None:
        print("No input!")
        return False
    if name =="ALL":
        print("ALL is not a legal name")
        return False
    for c in name:
        if not c.isalpha() and not c.isnumeric() and not c in "_-.":
            print("Use only letters, numbers or _ - .")
            return False
    return True
while not legal(name):
    name = input(f"Enter your name:\n")
c1= Client(name,False)
def update_messages():
    """
    updates the local list of messages
    :return: None
    """
    msgs = []
    run = True
    while run:
        time.sleep(0.1)  # update every 1/10 of a second
        new_messages = c1.get_messages()  # get any new messages from client
        msgs.extend(new_messages)  # add to local list of messages


Thread(target=update_messages).start()
print(f"---------------welcome {name}!---------------\n")
print("The input you will type will send message to the server\n")
print("The next inputs (inside the <>) will help you to make some activities with the server:\n")
print("input:<~><name> <msg> to send a private message to client. (name- the name of the received client, msg- your message)\n")
print("input: <show> to get the names of the connected clients. (every list starts with ALL, its not a client)\n")
print("input: <get_list_file> to get the names of the files that you can download from the server.(every list starts with CHOOSE_FILE, its not a file name)\n")
print("input: <download_file> <filename> to download a file from the server. (<filename>- the name of the file that you want to download)\n")
print("input: <{quit}> to disconnect and exit.")
print("any other input will be sent from you to all the connected clients as a public message.\n")
print("---------------sali&yosef chatroom---------------\n")


while True:
    msg=input()
    if msg == '{quit}':
        c1.disconnect()
        sys.exit()
    else:
        c1.send_message(msg)
