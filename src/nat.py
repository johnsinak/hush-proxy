import socket
import threading

class EchoThread(threading.Thread):
    def __init__(self, client_socket: socket.socket, client_address:str):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        data = self.client_socket.recv(1024)
        while data:
            self.client_socket.send(data)
            data = self.client_socket.recv(1024)
        
        print(f"Connection from {self.client_address} closed.")
        self.client_socket.close()

def echo_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Echo server is listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        thr = EchoThread(client_socket, client_address)
        thr.start()


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000  

    echo_server(host, port)
