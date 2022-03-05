import os
import sys
import threading
import time
import tkinter
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread, Lock
import pickle
from tkinter import simpledialog, Button, Menu, HORIZONTAL, scrolledtext
from tkinter.ttk import Entry, Progressbar

class Client:
    """
    for communication with server
    """
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    else:
        HOST = '127.0.0.1'
    PORT = 55000
    ADDR = (HOST, PORT)
    BUFSIZ = 1024
    def __init__(self,name:str,isgui=True):
        """
        Init object and send name to server
        :param name: str
        """
        self.name=name
        self.isconnected = True
        self.isgui = isgui
        if self.isgui:
            self.Gui_Constractor()

        # open tcp socket for client
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)

        # open UDP with rdt for file transfer
        self.client_socketUDP = socket(AF_INET, SOCK_DGRAM)
        self.client_socketUDP.connect(self.ADDR)

        self.messages_log=f"{self.name}`s messages log:\n\n"
        self.messages = []
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()

        # sends name of client to the server
        self.send_message(self.name)
        self.lock = Lock()

        # start GUI
        if isgui:
            self.Window.mainloop()

    def Gui_Constractor(self):

        # create the chat room window
        self.Window = tkinter.Tk()
        self.Window.withdraw()
        self.Window = tkinter.Toplevel()

        # set the title
        self.Window.title(f"{self.name}'s chat")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=600, height=700)

        # set messages
        self.msgST = tkinter.scrolledtext.ScrolledText(self.Window)
        self.msgST.place(relheight=0.8, relwidth=1)
        self.msgST.config(state='disabled')

        # create the menu bar
        self.menubar = Menu(self.Window)
        self.usermenu = Menu(self.menubar, tearoff=0)
        self.usermenu.add_command(label="Add User", command=run)
        self.usermenu.add_command(label="Change Name", command=self.renameClient)
        self.usermenu.add_command(label="Save", command=self.save_log)
        self.usermenu.add_separator()
        self.usermenu.add_command(label="Disconnect", command=self.disconnect)
        self.menubar.add_cascade(label="User", menu=self.usermenu)
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=self.about)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.Window.config(menu=self.menubar)

        # set connects list
        self.others = ['ALL']
        self.varconn = tkinter.StringVar(self.Window)
        self.setOthers()

        # set files list
        self.files = ['<CHOOSE_FILE>']
        self.varfiles = tkinter.StringVar(self.Window)
        self.setFiles()

        # create a entry box for the messages
        self.entryMsg = Entry(self.Window, font="Helvetica 14")
        self.entryMsg.place(relheight=0.05, relx=0.1, rely=0.75, relwidth=0.9)

        # set the focus of the cursor
        self.entryMsg.focus()

        # set refresh files button
        self.refreshButton = Button(self.Window, text="refresh files", font="Helvetica 14 bold",
                                    command=lambda: self.send_message("get_list_file") in ())
        self.refreshButton.place(rely=0.8, relx=0, relheight=0.05)

        # set download file button
        self.downloadButton = Button(self.Window, text="Download", font="Helvetica 14 bold",
                                     command=lambda: self.download_btn() in ())
        self.downloadButton.place(rely=0.8, relx=0.6, relheight=0.05)

        # set send message button
        self.sendButton = Button(self.Window, text="send", font="Helvetica 14 bold",
                                 command=lambda: self.send_from_GUI() in ())
        self.sendButton.place(rely=0.75, relx=0.9, relheight=0.05)
        self.Window.bind('<Return>', self.send_from_GUI())

        # set the download bar
        self.progress = Progressbar(self.Window, orient=HORIZONTAL, length=100, mode='determinate')
        self.progress.place(rely=0.87, relx=0, relwidth=1, relheight=0.05)

        # set percents of download
        self.percent_text = tkinter.StringVar()
        self.percents = tkinter.Label(self.Window, textvariable=self.percent_text, font="Helvetica 14 bold")
        self.percents.place(rely=0.82, relx=0.9)
        self.percent_text.set("")

        #set down title
        self.downtitle = tkinter.Label(self.Window, text="Sali&Yosf Chat Room", font="Helvetica 14 bold")
        self.downtitle.place(rely=0.95,relx=0.3)

    def send_from_GUI(self):
        if self.isgui:
            dest=self.varconn.get()
            if dest=='ALL':
                self.send_message(self.entryMsg.get())
            else:
                self.send_message(f"~{dest} {self.entryMsg.get()}")
            self.entryMsg.delete(0,len(self.entryMsg.get()))
            self.entryMsg.focus()

    # set the pull down of the connected users
    def setOthers(self):
        if self.isgui and self.isconnected:
            self.varconn.set(self.others[0])  # default value
            self.ow = tkinter.OptionMenu(self.Window, self.varconn, *self.others)
            self.ow.place(rely=0.75, relx=0, relwidth=0.1, relheight=0.052)

    # set the pull down of the files
    def setFiles(self):
        if self.isgui:
            self.varfiles.set(self.files[0])  # default value
            self.fw = tkinter.OptionMenu(self.Window, self.varfiles, *self.files)
            self.fw.place(rely=0.8, relx=0.2, relwidth=0.4, relheight=0.052)

    def download(self, port, size, path):
        try:
            with open(path, "wb") as file:
                size = (size // 1000) + 1
                ADDRESS_SERVER = (self.HOST, port)
                CLIENTUDP = socket(AF_INET, SOCK_DGRAM)
                for i in range(size):
                    done = False
                    while not done:
                        CLIENTUDP.sendto(bytes(f"part {i}", "utf-8"), ADDRESS_SERVER)
                        msg, addr = CLIENTUDP.recvfrom(self.BUFSIZ)
                        # filter messages that are not from our server
                        while (addr != ADDRESS_SERVER):
                            msg, addr = CLIENTUDP.recvfrom(self.BUFSIZ)
                        msg,msg_size =pickle.loads(msg)
                        if type(msg_size) == int and len(msg)==msg_size:
                            done = True
                        else:
                            print("lost a packet, send again.")
                    file.write(msg)
                    percent=round(i / size * 100, 2)
                    print(f"{percent}% downloaded")
                    if self.isgui:
                        self.percent_text.set(f"{percent}%")
                        self.progress['value'] = percent
            print("File was downloaded 100%\n")
            if self.isgui:
                self.percent_text.set("100%")
                self.pushMSG(f"{path.split('/')[-1]} downloaded successfully.\n")
                self.progress['value'] =100
                time.sleep(2)
                self.percent_text.set("")
                self.progress['value'] = 0

        finally:
            CLIENTUDP.sendto(bytes("finished", "utf-8"), ADDRESS_SERVER)
            CLIENTUDP.close()

    def download_btn(self):
        if self.varfiles.get() == '<CHOOSE_FILE>':

            tkinter.messagebox.showerror(title=None, message="choose file to download!")
        else:
            self.send_message(f"download_file {self.varfiles.get()}")

    def receive_messages(self):
        """
        receive messages from server
        :return: None
        """
        while self.isconnected:
            try:
                msg = self.client_socket.recv(self.BUFSIZ).decode('utf-8')
                print(f"client {self.name} received message:{msg}")
                if self.isgui:
                    self.pushMSG(f"{msg}\n")
                if msg.split()[0] == "UDP":
                    port = int(msg.split()[1])
                    filesize = int(msg.split()[2])
                    path = os.path.join(os.getcwd(), 'Downloads')
                    try:
                        os.mkdir(path)
                    except:
                        pass
                    download_thread = threading.Thread(target =self.download, args =(port, filesize, f"{os.getcwd()}/Downloads/{msg.split()[3]}") )
                    download_thread.start()
                    #self.download(port, filesize, f"{os.getcwd()}/Downloads/{msg.split()[3]}")
                elif msg.split()[0] == "ALL":
                    self.others= msg.split()
                    self.setOthers()
                elif msg.split()[0] == "<CHOOSE_FILE>":
                    self.files= msg.split()
                    self.setFiles()

                # make sure memory is safe to access
                self.lock.acquire()
                self.messages.append(msg)
                self.lock.release()
            except Exception as e:
                print("[EXCPETION]", e)

                break

    def pushMSG(self,msg):
        if msg.split()[0]=='UDP':
            msg=f"downloading {msg.split()[3]}...\n"
        if msg.split()[0] != 'ALL' and msg.split()[0] !='<CHOOSE_FILE>':
            self.msgST.config(state='normal')
            self.msgST.insert('end',msg)
            self.msgST.yview('end')
            self.msgST.config(state='disabled')
            self.messages_log+=msg

    def send_message(self, msg):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        try:
            self.client_socket.send(bytes(msg, "utf8"))
        except Exception as e:
            print(e)

    def get_messages(self):
        """
        :returns a list of str messages
        :return: list[str]
        """
        messages_copy = self.messages[:]

        # make sure memory is safe to access
        self.lock.acquire()
        self.messages = []
        self.lock.release()

        return messages_copy

    #saving the chat to a text file
    def save_log(self):
        if not self.isconnected:
            tkinter.messagebox.showerror(title=None, message="You Are Disconnected!")
            return
        path = os.path.join(os.getcwd(), 'logs')
        try:
            os.mkdir(path)
        except:
            pass
        file_name=f"logs/{self.name}_messages_log"
        with open(file_name+ ".txt", "w") as f:
            f.write(self.messages_log)
        print(file_name,"saved.")
        tkinter.messagebox.showinfo(title=None, message=f"{file_name} saved.")
        return True

    def renameClient(self):
        if not self.isconnected:
            if self.isgui:
                tkinter.messagebox.showerror(title=None, message="You Are Disconnected!")
            return
        newname = ask_for_username()
        oldname=self.name
        self.name = newname
        self.send_message(f"CHANGENAME {oldname} {newname}")
        self.Window.title(f"{newname}'s chat")

    def disconnect(self):
        if not self.isconnected:
            if self.isgui:
                tkinter.messagebox.showerror(title=None, message="You Are disconnected!")
            return
        self.send_message("{quit}")
        self.isconnected=False
        if self.isgui:
            self.pushMSG("you left the chat...\n")
            self.Window.title(f"{self.name} Disconnected!")
            self.disconnectedlbl = tkinter.Label(self.Window, text='YOU ARE OUT OF THE CHAT', font="Helvetica 14 bold")
            self.disconnectedlbl.place(rely=0, relx=0,relwidth=1,relheight=0.8)
            self.disconnectedbutton = Button(self.Window, text="back to the chat", font="Helvetica 14 bold",
                                     command=lambda: self.back_to_the_chat() in ())
            self.disconnectedbutton.place(rely=0.8, relx=0,relwidth=1,relheight=0.2)
            tkinter.messagebox.showinfo(title=None, message=f"bye {self.name}!")
        self.client_socket.close()

    #after disconnecting from gui you can back to chat
    def back_to_the_chat(self):
        self.Window.title(f"{self.name}'s chat")
        self.disconnectedbutton.destroy()
        self.disconnectedlbl.destroy()
        log=self.messages_log
        self.__init__(self.name,False)
        self.messages_log=log
        self.isgui=True

    #open help.pdf on a web browser
    def about(self):
        webbrowser.open_new(f"{os.getcwd()}/about.pdf")

def legal(name):
    if name==""or name is None:
        tkinter.messagebox.showerror(title=None, message="No input!")
        return False
    if name =="ALL":
        tkinter.messagebox.showerror(title=None, message="ALL is not a legal name")
        return False
    for c in name:
        if not c.isalpha() and not c.isnumeric() and not c in "_-.":
            tkinter.messagebox.showerror(title=None, message="Use only letters, numbers or _ - .")
            return False
    return True

#create a dialog to input name
def ask_for_username():
    name = simpledialog.askstring("Log In", "Enter your name")
    while not legal(name):
        name = simpledialog.askstring("Log In", "Enter your name")
        print("Not legal name!\n")
    print(f"Welcome {name}!\n")
    tkinter.messagebox.showinfo(title=None, message=f"Welcome {name}!")
    return name

def run():
    name=ask_for_username()
    Client(name)

if __name__=='__main__':
    run()

