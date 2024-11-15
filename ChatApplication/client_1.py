'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util


'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''

class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.username = username

    # join
    def send_join_request(self):
        message = util.make_message('join', 1, self.username)
        packet = util.make_packet('data', 0, message)
        self.sock.sendto(packet.encode(), (self.server_addr, self.server_port))

    def start(self):
        self.send_join_request()
        Thread(target=self.receive_handler, daemon=True).start()

        while True:
            user_input = input("Enter command: ")
            user_input = user_input.lower()
            self.handle_command(user_input)

    # sort user input and apply function
    def handle_command(self, command):
        parts = command.split()
        cmd = parts[0].lower()

        if cmd =='msg' and len(parts) > 3:
            self.handle_message(parts)
        elif cmd == 'list':
            self.request_list()
        elif cmd == 'help':
            self.print_help()
        elif cmd == "quit":
            self.quit()
        else:
            print("Incorrect user input format")

    # send_message
    def handle_message(self, parts):
        num_recipients = int(parts[1])
        recipients = parts[2:2 + num_recipients]
        message_text = ' '.join(parts[2 + num_recipients:])
        message = util.make_message('msg', 4, ' '.join([str(num_recipients)] + recipients + [message_text]))
        packet = util.make_packet('data', 0, message)
        self.sock.sendto(packet.encode(), (self.server_addr, self.server_port))

    # request_users_list
    def request_list(self):
        message = util.make_message('request_users_list', 2)
        packet = util.make_packet('data', 0, message)
        self.sock.sendto(packet.encode(), (self.server_addr, self.server_port))
    
    # help
    def print_help(self):
        print("Available commands:")
        print("msg <number_of_users> <username1> <username2> … <message>")
        print("list - Lists all the usernames of clients connected to the application-server")
        print("help - Prints all the possible user-inputs and their format input")
        print("quit - Close the connection and quit the application-server")

    # disconnect
    def quit(self):
        message = util.make_message('disconnect', 1, self.username)
        packet = util.make_packet('data', 0, message)
        self.sock.sendto(packet.encode(), (self.server_addr, self.server_port))
        print("Quitting the application...")
        self.sock.close()
        sys.exit()
        
        
    # response_user_list
    # client forward_message receive
    def receive_handler(self):
        while True:
            data, _ = self.sock.recvfrom(1024)
            if util.validate_checksum(data.decode()):
                msg_type, seqno, message, checksum = util.parse_packet(data.decode())
                command, length, content = util.parse_message(message)
                if command in ['err_unknown_message', 'err_server_full', 'err_username_unavailable']:
                    print(f"disconnected: {content}")
                    self.sock.close()
                    sys.exit(0)
                elif command == 'RESPONSE_USERS_LIST':
                    print(f"list: {content}")
                elif command == 'forward_message':
                    sender, msg_content = content.split(': ', 1)
                    print(f"msg: {sender}: {msg_content}")
            else:
                print("Checksum error: Message corrupted")



# Do not change below part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
