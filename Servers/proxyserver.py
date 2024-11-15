from socket import *
import hashlib


# start the proxy server, same as regular except has cache
def start_proxy_server(host, port):
    cache = {}  # initialize the cache
    proxy_socket = socket(AF_INET, SOCK_STREAM)
    proxy_socket.bind((host, port))
    proxy_socket.listen(1)
    print("The server is ready to receive")  # check
    print(f"Proxy server listening on {host}:{port}")

    while True:
        client_socket, client_address = proxy_socket.accept()
        print(f"Accepted connection from {client_address}")
        handle_client(client_socket, client_address, cache)


def handle_client(client_socket, client_address, cache):
    request = client_socket.recv(2048).decode('utf-8')
    print(f"Received request from {client_address}:\n{request}")  # check
    first_line = request.split('\n')[0]  # breaks the HTTP request down, sets first_line to GET request
    method, url, http_version = first_line.split()  # breaks up request line
    url = url.lstrip('/')
    hostname, path = format_url(url)
    cache_key = hashlib.md5(url.encode('utf-8')).hexdigest()  # generate a cache key based on the URL

    # check if the request is already in cache
    if cache_key in cache:
        print("Found in cache. Returning cached content.")
        response = cache[cache_key]
    else:
        print("Not found in cache. Fetching from server.")
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.connect((hostname, 80))
        server_request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
        server_socket.sendall(server_request.encode('utf-8'))

        response_parts = []  # get the response from the web server

        while True:
            part = server_socket.recv(4096)
            if not part:
                break
            response_parts.append(part)
        response = b''.join(response_parts)
        cache[cache_key] = response  # cache the response
        server_socket.close()

    client_socket.sendall(response)
    client_socket.close()


def format_url(url):
    if url.startswith("http://"):
        url = url[7:]

    path_index = url.find("/")

    if path_index == -1:
        hostname = url
        path = "/"
    else:
        hostname = url[:path_index]
        path = url[path_index:]

    return hostname, path


if __name__ == '__main__':
    start_proxy_server('localhost', 8888)
