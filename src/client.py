import socket
import threading
from settings import *
from utils import *
import subprocess
from time import sleep, time
from struct import unpack


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


def continuous_test(host, port, test_duration=300):
    last_ack = -1
    global client_socket
    client_socket.connect((host, port))
    print(f"Connected to {host}:{port}")
    is_open = True
    start = time()
    process = run_script_in_background()

    while time() - start < test_duration:
        try:
            while time() - start < test_duration:
                message = "https://www.wikipedia.org/"
                client_socket.send(message.encode('utf-8'))

                bs = client_socket.recv(8)
                (length,) = unpack('>Q', bs)
                data = b''
                while len(data) < length:
                    # doing it in batches is generally better than trying
                    # to do it all in one go, so I believe.
                    to_read = length - len(data)
                    data += client_socket.recv(
                        4096 if to_read > 4096 else to_read)

                sleep(0.1)
                try:
                    is_open = True
                    # print(f"Received: {data.decode('utf-8')}")
                except:
                    print('Received: EOF')
                    break
        except ConnectionRefusedError:
            print("Connection to the server failed. Make sure the server is running.")

        except ConnectionResetError:
            print('migrating...')
        
        except:
            print('the pipe is not ready yet, sleeping for 0.001 sec')
            sleep(0.001)
        finally:
            if is_open:
                client_socket.close()
                is_open = False
                print("Connection closed.")
    print(f'test is done, total time was: {time() - start} secs')
    process.terminate()


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #TODO: fix this
    migration_endpoint = ("10.27.0.2", 8089)
    handler = MigrationHandler(listen_endpoint=migration_endpoint)
    handler.start()
    host = '10.27.0.20'
    port = 8088
    choice = input('start? ').strip()
    if choice == '0':
        continuous_test(host, port)
    else:
        tcp_client(host, port)
