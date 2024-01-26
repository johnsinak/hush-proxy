from server_threads import *
from settings import *
import requests

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

class Proxy:
    def __init__(self, wireguard_endpoint, nat_endpoint, broker_endpoint, migration_endpoint, polling_endpoint) -> None:
        """
        endpoints are tuples of: (address, port)
        """
        self.my_number = int(socket.gethostbyname(socket.gethostname()).split('.')[-1])
        self.wireguard_endpoint = wireguard_endpoint
        self.nat_endpoint = nat_endpoint
        self.broker_endpoint = broker_endpoint
        self.migration_endpoint = migration_endpoint
        self.polling_endpoint = polling_endpoint
    
    def migrate(self, new_proxy_ip):
        # migrate address
        global client_addresses, client_sockets, nat_sockets
        with open(WIREGUARD_CONFIG_LOCATION, "rb") as f:
            data = f.read()
        new_proxy_address = new_proxy_ip
        new_proxy_socket = MIGRATION_PORT
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((new_proxy_address, new_proxy_socket))
        s.sendall(data)

        print(f'sending migration notice to {len(client_addresses)} clients')
        for i in range(len(client_addresses)):
            address = client_addresses[i]
            cli_sock = client_sockets[i]
            dest_sock = nat_sockets[i]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address[0], MIGRATION_PORT))
            s.sendall(f"{new_proxy_address}:{WIREGUARD_PORT}".encode())
            s.close()
            cli_sock.close()
            dest_sock.close()
        client_addresses = []
        client_sockets = []
        nat_sockets = []

    def run(self):
        ip = get_public_ip()
        print(f'my endpoint is: {ip}:51820')

        forwarding_server = ForwardingServerThread(self.wireguard_endpoint, self.nat_endpoint)
        migration_handler = MigrationHandler(self.migration_endpoint)
        polling_handler = PollingHandler(self.polling_endpoint)
        polling_handler.start()
        migration_handler.start()
        forwarding_server.start()

        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind((self.broker_endpoint[0], self.broker_endpoint[1]))
        dock_socket.listen(5)

        while True:
            broker_socket, broker_address = dock_socket.accept()
            data = broker_socket.recv(1024)
            
            command = data.decode().strip().lower().split()
            broker_socket.close()

            if (command[0] == "migrate"):
                if len(command) > 1:
                    self.migrate(command[1])
                else:
                    self.migrate(f'172.17.0.{self.my_number + 1}:8089')

