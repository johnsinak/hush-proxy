import socket

def tcp_client(host, port):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        while True:
            message = input("Enter a message (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break

            # Send the message to the server
            client_socket.send(message.encode('utf-8'))

            # Receive and print the server's response
            data = client_socket.recv(1024)
            print(f"Received from server: {data.decode('utf-8')}")

    except ConnectionRefusedError:
        print("Connection to the server failed. Make sure the server is running.")

    finally:
        # Close the client socket
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    host, port = input('enter server <address>:<port>\n').strip().split(':')

    tcp_client(host, port)
