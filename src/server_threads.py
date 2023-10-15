import threading
import socket

class ForwardThread(threading.Thread):
    def __init__(self, source_socket: socket.socket, destination_socket: socket.socket, description: str):
        threading.Thread.__init__(self)
        self.source_socket = source_socket
        self.destination_socket = destination_socket
        self.description = description

    def run(self):
        data = ' '
        while data:
            data = self.source_socket.recv(1024)
            print (f"==== {self.description}: {data}")
            if data:
                self.destination_socket.sendall(data)
            else:
                self.source_socket.shutdown(socket.SHUT_RD)
                self.destination_socket.shutdown(socket.SHUT_WR)


class ForwardingServerThread(threading.Thread):
    def __init__(self, listen_endpoint: tuple, forward_endpoint: tuple):
        threading.Thread.__init__(self)
        self.listen_endpoint = listen_endpoint
        self.forward_endpoint = forward_endpoint

    def run(self):
        try:
            dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dock_socket.bind((self.listen_endpoint[0], self.listen_endpoint[1]))
            dock_socket.listen(5)
            print(f"==== listening on {self.listen_endpoint[0]}:{self.listen_endpoint[1]}")
            while True:
                client_socket, client_address = dock_socket.accept()

                print (f"==== from {client_address}:{self.listen_endpoint[1]} to {self.forward_endpoint[0]}:{self.forward_endpoint[1]}")
                nat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                nat_socket.connect((self.forward_endpoint[0], self.forward_endpoint[1]))
                way1 = ForwardThread(client_socket, nat_socket, "client -> server")
                way1.daemon = True
                way2 = ForwardThread(nat_socket, client_socket, "server -> client")
                way2.daemon = True
                way1.start()
                way2.start()
        finally:
            new_server = ForwardingServerThread()
            new_server.start()

