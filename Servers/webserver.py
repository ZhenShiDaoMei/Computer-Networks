from socket import *
import os


# see what we type of file we need to give client
def get_file_type(filename):
    if filename.endswith(".html"):
        return "text/html"
    elif filename.endswith(".jpeg"):
        return "image/jpeg"
    elif filename.endswith(".png"):
        return "image/png"
    else:
        return "text/plain"


# start the server (basically same as slides)
def start_webserver(host, port):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("The server is ready to receive")  # check
    print(f"Web server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        handle_request(client_socket)


def handle_request(client_socket):
    request = client_socket.recv(2048).decode('utf-8')  # receives data from client_socket, reads 2048 bytes
    print(f"Received request: {request}")  # check
    lines = request.split('\n')  # breaks the HTTP request down
    request_line = lines[0]  # request_line = first line in HTTP request
    method, requested_file, http_version = request_line.split()  # breaks up request line
    filename = requested_file.lstrip('/')  # remove the '/'

    if os.path.exists(filename):  # if file exists, return, else return 404
        with open(filename, 'rb') as file:
            content = file.read()
            content_type = get_file_type(filename)
            # constructs HTTP response
            response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode('utf-8')
            response += content  # lastly adds content to the end of HTTP response
    else:
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFile not found.".encode('utf-8')

    client_socket.sendall(response)
    client_socket.close()


if __name__ == '__main__':
    start_webserver('localhost', 6789)  # ran on port 6789
