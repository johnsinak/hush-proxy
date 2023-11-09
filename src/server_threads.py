import threading
import socket
import subprocess
from settings import WIREGUARD_CONFIG_LOCATION

client_addresses = []
client_sockets = []
nat_sockets = []

class ForwardThread(threading.Thread):
    def __init__(self, source_socket: socket.socket, destination_socket: socket.socket, description: str):
        threading.Thread.__init__(self)
        self.source_socket = source_socket
        self.destination_socket = destination_socket
        self.description = description
        global client_sockets, nat_sockets
        client_sockets.append(source_socket)
        nat_sockets.append(destination_socket)

    def run(self):
        data = ' '
        try:
            while data:
                data = self.source_socket.recv(1024)
                # print (f"==== {self.description}: {data}")
                if data:
                    try:
                        self.destination_socket.sendall(data)
                    except:
                        print('connection closed')
                        try:
                            self.destination_socket.shutdown(socket.SHUT_WR)
                        except:
                            pass
                        try:
                            self.source_socket.shutdown(socket.SHUT_WR)
                        except:
                            pass
                        break
                else:
                    try:
                        self.source_socket.shutdown(socket.SHUT_RD)
                        self.destination_socket.shutdown(socket.SHUT_WR)
                    except:
                        print('connection closed')
                        break
        except:
            print('connection closed')


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
        peers = migration_string.split('Peer')
        if len(peers) == 1:
            print("ERROR: Migrated data was empty!")
            return
        peers = peers[1:]

        # Update wireguard w0
        for peer in peers:
            lines_in_peer = peer.split('\n')
            public_key = ''
            allowed_ips = ''
            for line in lines_in_peer:
                if 'PublicKey' in line:
                    public_key = line[line.find('=') + 1:].strip()
                if 'AllowedIPs' in line:
                    allowed_ips = line[line.find('=') + 1:].strip()

            print(f'INFO: adding {public_key}|{allowed_ips}')
            subprocess.run(f'wg set wg0 peer "{public_key}" allowed-ips {allowed_ips}', shell=True)
            subprocess.run(f'ip -4 route add {allowed_ips} dev wg0', shell=True)
            print("SUCCESS: migrated peer")

        # Update config file
        new_peers = ['[']
        new_peers.extend(peers)
        new_peers_string = '\n' + 'Peer'.join(new_peers)
        with open(WIREGUARD_CONFIG_LOCATION, 'a') as f:
            f.write(new_peers_string)
        print("SUCCESS: updated config file")


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
