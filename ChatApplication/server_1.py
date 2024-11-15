'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util


class Server:
    '''
    This is the main Server Class. You will  write Server code inside this class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        self.clients = {}
        self.MAX_NUM_CLIENTS = 10

    # start server
    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it.

        '''
        while True:
            data, addr = self.sock.recvfrom(1024)
            if util.validate_checksum(data.decode()):
                msg_type, seqno, message, checksum = util.parse_packet(data.decode())
                self.handle_message(msg_type, message, addr)
            else:
                print("Checksum error: Message corrupted")

    # sort message and apply function
    def handle_message(self, msg_type, message, addr):
        if msg_type == 'data':
            command, length, content = util.parse_message(message)
            if command == 'join':
                self.handle_join(content, addr)
            elif command == 'request_users_list':
                self.handle_request_users_list(addr)
            elif command == 'disconnect':
                self.handle_disconnect(content, addr)
            elif command == 'msg':
                self.forward_message(content, addr)
            else:
                self.send_error_message(addr, 'err_unknown_message', "unknown command")

    # server handle join
    def handle_join(self, username, addr):
        if len(self.clients) >= util.MAX_NUM_CLIENTS:
            self.send_error_message(addr, 'err_server_full', username)
        elif username in self.clients:
            self.send_error_message(addr, 'err_username_unavailable', username)
        else:
            self.clients[username] = addr
            print(f"Join: {username}")

    # server handling errors
    def send_error_message(self, addr, error_type, username):
        message = ""
        if error_type == 'err_unknown_message':
            message = f"{error_type} 0"
            print(f"Disconnected: {username} sent unknown command")
        elif error_type == 'err_server_full':
            message = f"{error_type} 0"
            print("Disconnected: server full")
        elif error_type == 'err_username_unavailable':
            message = f"{error_type} 0"
            print("Disconnected: username not available")
        
        packet = util.make_packet('data', 0, message)
        self.sock.sendto(packet.encode(), addr)

    # server handle list request
    def handle_request_users_list(self, addr):
        if addr in self.clients.values():
            usernames = ' '.join(sorted(self.clients.keys()))
            response = util.make_message('RESPONSE_USERS_LIST', 3, usernames)
            packet = util.make_packet('data', 0, response)
            self.sock.sendto(packet.encode(), addr)
            print("request_users_list: " + str(self.clients.keys()[self.clients.values().index(addr)]))

    # server disconnect client
    def handle_disconnect(self, username, addr):
        if username in self.clients:
            del self.clients[username]
            print(f"Disconnected: {username}")

    # server handle msg from client
    def forward_message(self, content, addr):
        sender, recipients_info = content.split(' ', 1)
        recipients, message = recipients_info.split(' ', 1)
        recipient_list = recipients.split(',')
        existent_recipients = []

        for recipient in recipient_list:
            if recipient in self.clients:
                existent_recipients.append(recipient)
                forward_packet = util.make_packet('data', self.next_seqno(), f"forward_message {sender}: {message}")
                self.sock.sendto(forward_packet.encode(), self.clients[recipient])
            else:
                print(f"msg: {sender} to non-existent user {recipient}")

        if existent_recipients:
            print(f"msg: {sender}")

# Do not change below part of code

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
