import socket
import requests
import os

from nat_threads import *


def echo_server(host, port):
    nat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nat_socket.bind((host, port))
    nat_socket.listen(5)

    print(f"yes")

    while True:
        client_socket, client_address = nat_socket.accept()
        print(f"Accepted connection from {client_address}")

        thr = EchoThread(client_socket, client_address)
        thr.start()


def nat_server(host, port):
    nat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nat_socket.bind((host, port))
    nat_socket.listen(5)

    print(f"yes")

    while True:
        client_socket, client_address = nat_socket.accept()
        print(f"Accepted connection from {client_address}")

        thr = NATThread(client_socket, client_address)
        thr.start()


def nat_server_with_bulk_downloads(host, port, beeg_file_path):
    nat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nat_socket.bind((host, port))
    nat_socket.listen(5)

    print('going beeg')

    while True:
        client_socket, client_address = nat_socket.accept()
        print(f"Accepted connection from {client_address}")

        thr = BEEGThread(client_socket, client_address)
        thr.start()


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    beeg_file_path = '../../random.img'
    pub_ip = get_public_ip()
    print(f"Nat server is listening on {pub_ip}:{port}")

    choice = int(input('input 0 for echo, 1 for wikipedia, 2 for beeg file: ').strip())

    if choice == 0:
        print('echo server...', end=' ')
        echo_server(host, port)
    elif choice == 1:
        print('nat server...', end=' ')
        nat_server(host, port)
    elif choice == 2:
        print('beeg server...', end=' ')
        nat_server_with_bulk_downloads(host, port, beeg_file_path)
    else:
        print('incorrect choice!')
