import socket
import threading
from settings import *
from utils import *
import subprocess
from time import sleep, time
from struct import unpack
from logger import log


class MigrationHandler(threading.Thread):
    def __init__(self, listen_endpoint: tuple):
        threading.Thread.__init__(self)
        self.listen_endpoint = listen_endpoint

    def run(self):
        log(f"==== client migration handler listening on {self.listen_endpoint[0]}:{self.listen_endpoint[1]}")
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind((self.listen_endpoint[0], self.listen_endpoint[1]))
        dock_socket.listen(5)
        
        while True:
            mig_socket, mig_address = dock_socket.accept()
            print (f"==== migration request from {mig_address}:{self.listen_endpoint[1]}")
            data = mig_socket.recv(1024)
            log(f"migration info: {data}")
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
            log(f"Connected to {new_endpoint_address}:{new_endpoint_port}")


def tcp_client(host, port):
    try:
        global client_socket
        client_socket.connect((host, port))
        log(f"Connected to {host}:{port}")

        while True:
            message = input("Enter a message (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break

            client_socket.send(message.encode('utf-8'))

            data = client_socket.recv(1024)
            log(f"Received from server: {data.decode('utf-8')}")

    except ConnectionRefusedError:
        log("Connection to the server failed. Make sure the server is running.")

    finally:
        client_socket.close()
        log("Connection closed.")


def efficacy_test_bulk_download(host, port, migration, test_duration=300):
    global client_socket
    client_socket.connect((host, port))
    log(f"Connected to {host}:{port}")
    start_time = time()
    measure_thread = TrafficGetterThread(start_time=start_time, duration=300)
    measure_thread.start()
    if migration:
        testing_migration_senderr = TestingMigrationSenderThread(start_time=start_time, duration=300)
        testing_migration_senderr.start()
    i = 0
    amount_of_data_gathered = 0
    while time() - start_time < test_duration:
        try:
            while time() - start_time < test_duration:
                message = f"BEEGMode {amount_of_data_gathered}"
                client_socket.send(message.encode('utf-8'))
                bs = client_socket.recv(8)
                (length,) = unpack('>Q', bs)
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    new_data = client_socket.recv(
                        4096 if to_read > 4096 else to_read)
                    data += new_data
                    amount_of_data_gathered += len(new_data)
                    
                    if time() - start_time > i * 5:
                        log(f'here at {5*i}s, got {len(data)}data', pr=True)
                        i += 1
                # Note: We might have to add this back later
                # sleep(0.1)
        except ConnectionRefusedError:
            log("Connection to the server failed. Make sure the server is running.")

        except ConnectionResetError:
            log('migrating...')
        
        except Exception as e:
            log('the pipe is not ready yet, sleeping for 0.01 sec')
            log(f'error: {e}')
            sleep(0.01)
    log(f'test is done, total time was: {time() - start_time} secs')


def efficacy_test_wikipedia(host, port, migration, test_duration=300):
    last_ack = -1
    global client_socket
    client_socket.connect((host, port))
    log(f"Connected to {host}:{port}")
    start_time = time()
    measure_thread = TrafficGetterThread(start_time=start_time, duration=300)
    measure_thread.start()
    if migration:
        testing_migration_senderr = TestingMigrationSenderThread(start_time=start_time, duration=300)
        testing_migration_senderr.start()
    i = 0
    while time() - start_time < test_duration:
        try:
            while time() - start_time < test_duration:
                message = "https://www.wikipedia.org/"
                client_socket.send(message.encode('utf-8'))
                bs = client_socket.recv(8)
                (length,) = unpack('>Q', bs)
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    new_data = client_socket.recv(
                        4096 if to_read > 4096 else to_read)
                    data += new_data
                    
                    if time() - start_time > i * 20:
                        log(f'here at {20*i}s, got {len(data)}data')
                        i += 1

                sleep(0.1)
        except ConnectionRefusedError:
            log("Connection to the server failed. Make sure the server is running.")

        except ConnectionResetError:
            log('migrating...')
        
        except Exception as e:
            log('the pipe is not ready yet, sleeping for 0.01 sec')
            log(f'error: {e}')
            sleep(0.01)
    log(f'test is done, total time was: {time() - start_time} secs')


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    migration_endpoint = ("10.27.0.2", 8089)
    handler = MigrationHandler(listen_endpoint=migration_endpoint)
    handler.start()
    host = '10.27.0.20'
    port = 8088
    choice = input('start? ').strip()
    if choice == '0':
        efficacy_test_wikipedia(host, port, migration=False)
    elif choice == '1':
        efficacy_test_wikipedia(host, port, migration=True)
    elif choice == '2':
        efficacy_test_bulk_download(host, port, migration=False)
    elif choice == '3':
        efficacy_test_bulk_download(host, port, migration=True)
    else:
        tcp_client(host, port)

