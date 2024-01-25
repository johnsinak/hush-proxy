import subprocess
import threading
import socket
from settings import *

class MigrationHandler(threading.Thread):
    def __init__(self, listen_endpoint: tuple):
        threading.Thread.__init__(self)
        self.listen_endpoint = listen_endpoint

    def run(self):
        print(f"==== client migration handler listening on {self.listen_endpoint[0]}:{self.listen_endpoint[1]}")
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind((self.listen_endpoint[0], self.listen_endpoint[1]))
        dock_socket.listen(5)
        
        while True:
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


def run_script_in_background(script_path='../scripts/measure.sh'):
    try:
        process = subprocess.Popen(['bash', script_path])

        print(f"Shell script '{script_path}' is running in the background.")
        return process
    except Exception as e:
        print(f"Error running the shell script: {e}")
        return None


def send_migration_request_for_testing(start):
    #TODO: fix this
    pass