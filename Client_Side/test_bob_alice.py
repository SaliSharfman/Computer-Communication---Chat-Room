import unittest
import time
from threading import Thread
from client import Client

# create client for bob without gui
bob = Client("Bob", False)
# create client for bob without gui
alice = Client("Alice", False)

bobmsg=[]
alicemsg=[]

def update_messages():
    """
    updates the local list of messages
    :return: None
    """
    run = True
    while run:
        # get any new messages from bob
        bobmsg.extend(bob.get_messages())

        # get any new messages from alice
        alicemsg.extend(alice.get_messages())

        # update every 1/10 of a second
        time.sleep(0.1)

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # start thread for receive messages
        Thread(target=update_messages).start()

    def test_bob_alice(self):
        time.sleep(2)
        self.assertEqual('Bob has joined the chat!',bobmsg[0])
        self.assertEqual('Alice has joined the chat!', alicemsg[0])

        # Bob sends message to all
        bob.send_message("hello")
        time.sleep(2)
        self.assertEqual("Bob: hello", bobmsg[-1])
        self.assertEqual("Bob: hello", alicemsg[-1])

        # Alice sends message to all
        alice.send_message("hello")
        time.sleep(2)
        self.assertEqual("Alice: hello", alicemsg[-1])
        self.assertEqual("Alice: hello", bobmsg[-1])

        # Bob sends message to all
        bob.send_message("whats up")
        time.sleep(2)
        self.assertEqual("Bob: whats up", bobmsg[-1])
        self.assertEqual("Bob: whats up", alicemsg[-1])

        # Alice sends message to all
        alice.send_message("Nothing much")
        time.sleep(2)
        self.assertEqual("Alice: Nothing much", alicemsg[-1])
        self.assertEqual("Alice: Nothing much", bobmsg[-1])

        # Bob sends message privately to Alice
        bob.send_message("~Alice Hello Alice")
        time.sleep(2)
        self.assertEqual("from you to Alice: (PRIVATE)  Hello Alice", bobmsg[-1])
        self.assertEqual("Bob: (PRIVATE)  Hello Alice", alicemsg[-1])

        # Bob wants to know who is connected to the server
        bob.send_message("show")
        time.sleep(2)
        self.assertEqual('ALL Alice ', bobmsg[-1])

        # Alice wants to know who is connected to the server
        alice.send_message("show")
        time.sleep(2)
        self.assertEqual('ALL Bob ', alicemsg[-1])

        # Alice wants to know which files the server has for download
        alice.send_message("get_list_file")
        time.sleep(2)
        self.assertEqual('<CHOOSE_FILE>', alicemsg[-1].split()[0])

        # Alice download a file
        alice.send_message("download_file alice.jpg")
        time.sleep(3)
        self.assertEqual('UDP', alicemsg[-1].split()[0])

        # Bob wants to know which files the server has for download
        bob.send_message("get_list_file")
        time.sleep(2)
        self.assertEqual('<CHOOSE_FILE>', bobmsg[-1].split()[0])

        # Bob download a file
        bob.send_message("download_file bob.jpg")
        time.sleep(3)
        self.assertEqual('UDP', bobmsg[-1].split()[0])


        # Bob disconnect
        bob.disconnect()
        time.sleep(2)
        self.assertEqual('Bob left the chat...', alicemsg[-2])
        self.assertEqual('ALL ',alicemsg[-1])


        # Alice disconnect
        alice.disconnect()
        print('Alice left the chat...')




if __name__ == '__main__':
    unittest.main()



