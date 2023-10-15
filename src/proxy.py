import socket
import sys
import threading


class ForwardingServerThread(threading.Thread):
    def __init__(self, listen_endpoint: tuple, forward_endpoint: tuple):
        threading.Thread.__init__(self)
        self.listen_endpoint = listen_endpoint
        self.forward_endpoint = forward_endpoint

    def run(self):
        try:
            dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dock_socket.bind((self.listen_endpoint[0], self.listen_endpoint[1])) # listen
            dock_socket.listen(5)
            print(f"==== listening on {self.listen_endpoint[0]}:{self.listen_endpoint[1]}")
            while True:
                client_socket, client_address = dock_socket.accept()

                print (f"==== from {client_address}:{self.listen_endpoint[1]} to {self.forward_endpoint[0]}:{self.forward_endpoint[1]}")
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((target_host, target_port))
                threading.start_new_thread(forward, (client_socket, server_socket, "client -> server" ))
                threading.start_new_thread(forward, (server_socket, client_socket, "server -> client" ))
        finally:
            threading.start_new_thread(server, () )


class Proxy:
    def __init__(self, wireguard_endpoint, nat_endpoint, broker_endpoint) -> None:
        """
        end points are tuples of: (address, port)
        """
        self.wireguard_endpoint = wireguard_endpoint
        self.nat_endpoint = nat_endpoint
        self.broker_endpoint = broker_endpoint

