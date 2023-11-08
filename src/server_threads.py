import threading
import socket
import subprocess


client_addresses = []

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
                break


class ForwardingServerThread(threading.Thread):
    def __init__(self, listen_endpoint: tuple, forward_endpoint: tuple):
        threading.Thread.__init__(self)

        self.listen_endpoint = listen_endpoint
        self.forward_endpoint = forward_endpoint

    def run(self):
        global client_addresses
        try:
            dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dock_socket.bind((self.listen_endpoint[0], self.listen_endpoint[1]))
            dock_socket.listen(5)
            print(f"==== listening on {self.listen_endpoint[0]}:{self.listen_endpoint[1]}")
            while True:
                client_socket, client_address = dock_socket.accept()
                client_addresses.append(client_address)

                print (f"==== from {client_address}:{self.listen_endpoint[1]} to {self.forward_endpoint[0]}:{self.forward_endpoint[1]}")
                nat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                nat_socket.connect((self.forward_endpoint[0], self.forward_endpoint[1]))
                way1 = ForwardThread(client_socket, nat_socket, "client -> server")
                way2 = ForwardThread(nat_socket, client_socket, "server -> client")
                way1.start()
                way2.start()
        finally:
            new_server = ForwardingServerThread(self.listen_endpoint, self.forward_endpoint)
            new_server.start()


class MigratingAgent(threading.Thread):
    def __init__(self, client_socket: socket.socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def run(self):
        data = ' '
        full_file_data = b''
        while data:
            data = self.client_socket.recv(1024)
            print (f"==== recieved data")
            if data:
                full_file_data += data
            else:
                self.client_socket.shutdown(socket.SHUT_RD)
                break
        print (f"==== Done! full migration data:\n{full_file_data}")
        migration_string = full_file_data.decode()
        peers = data.split('Peer')
        if len(peers) == 1:
            print("ERROR: Migrated data was empty!")
            return
        peers = peers[1:]
        for peer in peers:
            lines_in_peer = peer.split('\n')
            public_key = ''
            allowed_ips = ''
            for line in lines_in_peer:
                if 'PublicKey' in line:
                    public_key = line.split('=')[1]
                if 'AllowedIPs' in line:
                    allowed_ips = line.split('=')[1]
            print(f'INFO: adding {public_key}|{allowed_ips}')
            subprocess.run(f'wg set wg0 peer "{public_key}" allowed-ips {allowed_ips}')
            subprocess.run(f'ip -4 route add {allowed_ips} dev wg0')
            print("INFO: migrated peer")


class MigrationHandler(threading.Thread):
    def __init__(self, listen_endpoint: tuple):
        threading.Thread.__init__(self)
        self.listen_endpoint = listen_endpoint

    def run(self):
        try:
            print(f"==== migration handler listening on {self.listen_endpoint[0]}:{self.listen_endpoint[1]}")
            dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dock_socket.bind((self.listen_endpoint[0], self.listen_endpoint[1]))
            dock_socket.listen(5)
            
            while True:
                client_socket, client_address = dock_socket.accept()
                print (f"==== migration request from {client_address}:{self.listen_endpoint[1]}")
                agent = MigratingAgent(client_socket)
                agent.start()
        finally:
            dock_socket.close()
            new_server = MigrationHandler(self.listen_endpoint)
            new_server.start()
