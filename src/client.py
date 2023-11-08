import socket
import threading
from settings import *
import subprocess

class MigrationHandler(threading.Thread):
    def __init__(self, listen_endpoint: tuple):
        threading.Thread.__init__(self)
        self.listen_endpoint = listen_endpoint

    def run(self):
        print(f"==== migration handler listening on {self.listen_endpoint[0]}:{self.listen_endpoint[1]}")
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind((self.listen_endpoint[0], self.listen_endpoint[1]))
        dock_socket.listen(5)
        
        while True:
            # TODO: Clean code

            mig_socket, mig_address = dock_socket.accept()
            print (f"==== migration request from {mig_address}:{self.listen_endpoint[1]}")
            data = mig_socket.recv(1024)
            print(f"migration info: {data}")
            new_endpoint = data.decode()
            new_endpoint_address, new_endpoint_port = new_endpoint.split(':')
            new_endpoint_port = int(new_endpoint_port) 

            with open(WIREGUARD_CONFIG_LOCATION, "rb") as f:
                old_config = f.read()
            
            splitted_config = old_config.decode().split('Peer')
            lines_in_peer = splitted_config[1].split('\n')
            for i in range(len(lines_in_peer)):
                line = lines_in_peer[i]
                if 'PublicKey' in line:
                    pass
                    # NOTE: We can add public key replacement here as well.
                if 'Endpoint' in line:
                    splitted_line = line.split('=')
                    splitted_line[1] = new_endpoint
                    lines_in_peer[i] = '= '.join(splitted_line)
            new_config = 'Peer'.join([splitted_config[0], '\n'.join(lines_in_peer)])
            with open(WIREGUARD_CONFIG_LOCATION, "w") as f:
                f.write(new_config)

            # subprocess.run(f'wg syncconf {WIREGUARD_INTERFACE_NAME} <(wg-quick strip {WIREGUARD_INTERFACE_NAME})', shell=True)
            subprocess.run(f'wg-quick down wg0', shell=True)
            subprocess.run(f'wg-quick up wg0', shell=True)
            global client_socket, host, port
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(f"Connected to {new_endpoint_address}:{new_endpoint_port}")
            


def tcp_client(host, port):
    try:
        global client_socket
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        while True:
            message = input("Enter a message (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break

            client_socket.send(message.encode('utf-8'))

            data = client_socket.recv(1024)
            print(f"Received from server: {data.decode('utf-8')}")

    except ConnectionRefusedError:
        print("Connection to the server failed. Make sure the server is running.")

    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    migration_endpoint = ("10.27.0.2", 8089)
    handler = MigrationHandler(listen_endpoint=migration_endpoint)
    handler.start()
    # host, port = input('enter server <address>:<port>\n').strip().split(':')
    # port = int(port)
    host = '10.27.0.20'
    port = 8088
    input('start? ')
    tcp_client(host, port)
