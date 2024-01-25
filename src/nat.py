import socket
import threading
import requests

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

    print(f"yes")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        thr = EchoThread(client_socket, client_address)
        thr.start()

class NATThread(threading.Thread):
    def __init__(self, client_socket: socket.socket, client_address:str):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        data = self.client_socket.recv(1024)
        url = data.decode()
        response = requests.get(url)

        self.client_socket.sendall(response.text.encode())

        self.client_socket.close()

def nat_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"yes")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        thr = NATThread(client_socket, client_address)
        thr.start()


def get_public_ip():
    try:
        response = requests.get('https://httpbin.org/ip')

        if response.status_code == 200:
            public_ip = response.json()['origin']
            return public_ip
        else:
            print(f"Failed to retrieve public IP. Status code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request error: {e}")

    return None


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    pub_ip = get_public_ip()
    print(f"Nat server is listening on {pub_ip}:{port}")

    nat_server(host, port)
