import socket
import threading

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
                mig_socket, mig_address = dock_socket.accept()
                print (f"==== migration request from {mig_address}:{self.listen_endpoint[1]}")
                data = mig_socket.recv(1024)
                print(f"migration info: {data}")
                # TODO: Mangle wireguard config to address this
        finally:
            dock_socket.close()
            new_server = MigrationHandler(self.listen_endpoint)
            new_server.start()

def tcp_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
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
    migration_endpoint = ("10.27.0.2", 8089)
    handler = MigrationHandler(listen_endpoint=migration_endpoint)
    handler.start()
    host, port = input('enter server <address>:<port>\n').strip().split(':')
    port = int(port)

    tcp_client(host, port)
