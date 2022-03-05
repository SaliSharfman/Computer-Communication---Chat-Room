import tkinter
from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import time
import os
import pickle
# user class
class User:
    """
    Represents a online_user, holds name, socket client and IP address
    """

    def __init__(self, addr, client):
        self.addr = addr
        self.client = client
        self.name = None

    def set_name(self, name):
        """
        sets the users name
        :param name: str
        :return: None
        """
        self.name = name

    def __repr__(self):
        return f"User({self.addr}, {self.name})"
# GLOBAL CONSTANTS
HOST = ''
PORT = 55000
ADDR = (HOST, PORT)
MAX_CONNETIONS = 10
BUFSIZ = 1024
# GLOBAL VARIABLES
users = []
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)  # set up server
# dict of all ports 55000-55015
# (if port is caught his value = False otherwise True)
ports = {}
for i in range(16):
    ports[55000 + i] = True

def download(client, filename):
    SIZE = 1000
    filepath = f"{os.getcwd()}/FILES/{filename}"
    filesize = os.path.getsize(filepath)

    prt = 0
    for port, flag in ports.items():
        if flag:
            prt = port
            ports[port]=False
            break
    if prt == 0:
        print("no port!!!")
        return

    SERVERUDP = socket(AF_INET, SOCK_DGRAM)
    # Bind to address and ip

    SERVERUDP.bind(("", prt))
    print("[UDP STARTED] Waiting for connections...")

    msg = bytes(f"UDP {prt} {filesize} {filename}", "utf8")
    client.send(msg)

    with open(filepath, "rb") as file:
        msg, addr = SERVERUDP.recvfrom(BUFSIZ)
        msg = msg.decode('utf-8')
        while (msg != "finished"):
            msg = msg.split()
            if msg[0] == "part":
                numpart = int(msg[1])
                file.seek(numpart * SIZE)
                data = file.read(SIZE)
                data_size = len(data)
                data = (data,data_size)
                data = pickle.dumps(data)
                SERVERUDP.sendto(data, addr)
            msg, addr = SERVERUDP.recvfrom(BUFSIZ)
            msg = msg.decode('utf-8')
        SERVERUDP.close()
        ports[addr[1]]=True

def show_online(client, name):
    """
    show all online persons/clients
    :param client: (SERVER.accept())[0]
    :param name: str
    :return: None
    """
    names = "ALL "
    for user in users:
        if user.name != name:
            names += user.name
            names += " "
    client.send(bytes(names, "utf8"))

def show_online_to_all(name=""):
    for user in users:
        if user.name!= name:
            show_online(user.client, user.name)

def private_msg(msg, sender_name, getter_name):
    """
    send new messages to specific client (privately)
    :param msg: bytes["utf8"]
    :param sender_name: str
    :param getter_name: str
    :return: None
    """
    for user in users:
        if user.name == getter_name:
            client = user.client
            try:
                client.send(bytes(f"{sender_name}: (PRIVATE) ", "utf8") + msg)
            except Exception as e:
                print("[EXCEPTION]", e)

        elif user.name == sender_name:
            client = user.client
            try:
                client.send(bytes(f"from you to {getter_name}: (PRIVATE) ", "utf8") + msg)
            except Exception as e:
                print("[EXCEPTION]", e)

def broadcast(msg, name):
    """
    send new messages to all clients
    :param msg: bytes["utf8"]
    :param name: str
    :return: None
    """
    for user in users:
        client = user.client
        try:
            client.send(bytes(name, "utf8") + msg)
        except Exception as e:
            print("[EXCEPTION]", e)

def client_communication(user):
    """
    Thread to handle all messages from client
    :param person: Person
    :return: None
    """
    client = user.client

    # first message received is always the persons name
    name = client.recv(BUFSIZ).decode("utf8")
    user.set_name(name)

    msg = bytes(f"{name} has joined the chat!", "utf8")
    broadcast(msg, "")  # broadcast welcome message
    show_online_to_all()
    while True:  # wait for any messages from person
        msg = client.recv(BUFSIZ)

        if msg == bytes("{quit}", "utf8"):  # if message is qut - so disconnect the client
            users.remove(user)
            print(users)
            client.close()
            broadcast(bytes(f"{name} left the chat...", "utf8"), "")
            print(f"[DISCONNECTED] {name} disconnected\n")
            show_online_to_all(name)
            break
        elif msg[0] == 126:  # send it privately (~ sign to send it privately (and after it name: ~Daniel ...msg...))
            getter_name = msg.split()[0]
            msg = msg[len(getter_name):]
            getter_name = getter_name[1:]
            getter_name = getter_name.decode('utf-8')

            private_msg(msg, user.name, getter_name)

        elif msg.split()[0].decode('utf-8') == "show":
            show_online(user.client, user.name)

        elif msg.split()[0].decode('utf-8') == "CHANGENAME":
            m = bytes(f"{name} changed his name to {msg.split()[2].decode('utf-8')}!", "utf8")
            broadcast(m, "")
            name=msg.split()[2].decode("utf8")
            for user in users:
                if user.name == msg.split()[1].decode('utf-8'):
                    user.name = msg.split()[2].decode('utf-8')
            show_online_to_all(name)

        elif msg.split()[0].decode('utf-8') == "get_list_file":
            str_files = "<CHOOSE_FILE> "
            path = f"{os.getcwd()}/FILES"
            files = os.listdir(path)
            for f in files:
                str_files += f
                str_files += " "
            client.send(bytes(str_files, "utf8"))

        elif msg.split()[0].decode('utf-8') == "download_file":
            filename = msg.split()[1].decode('utf-8')
            download(client, filename)


        else:  # otherwise send message to all other clients
            broadcast(msg, name + ": ")

def wait_for_connection():
    """
    Wait for connecton from new clients, start new thread once connected
    :return: None
    """
    while True:
        try:
            client, addr = SERVER.accept()  # wait for any new connections
            user = User(addr, client)  # create new person for connection
            users.append(user)
            print(users)

            print(f"[CONNECTION] {addr} connected to the server at {time.time()}")
            Thread(target=client_communication, args=(user,)).start()
        except Exception as e:
            print("[EXCEPTION]", e)
            break

    print("SERVER CRASHED")

def start_server():
    SERVER.listen(MAX_CONNETIONS)  # open server to listen for connections
    print("[STARTED] Waiting for connections...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

def stop_server():
    SERVER.close()

if __name__ == "__main__":
    start_server()
