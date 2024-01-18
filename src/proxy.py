from server_threads import *
from settings import *


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
    
    def migrate(self, new_proxy_endpoint):
        # migrate address:port
        global client_addresses, client_sockets, nat_sockets
        with open(WIREGUARD_CONFIG_LOCATION, "rb") as f:
            data = f.read()
        new_proxy_address, new_proxy_socket = new_proxy_endpoint.split(':')
        new_proxy_socket = int(new_proxy_socket)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((new_proxy_address, new_proxy_socket))
        s.sendall(data)

        print(f'sending migration notice to {len(client_addresses)} clients')
        for i in range(len(client_addresses)):
            address = client_addresses[i]
            cli_sock = client_sockets[i]
            dest_sock = nat_sockets[i]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address[0], 8089))
            s.sendall(f"{new_proxy_address}:{WIREGUARD_PORT}".encode())
            s.close()
            cli_sock.close()
            dest_sock.close()
        client_addresses = []
        client_sockets = []
        nat_sockets = []

    def run(self):
        forwarding_server = ForwardingServerThread(self.wireguard_endpoint, self.nat_endpoint)
        migration_handler = MigrationHandler(self.migration_endpoint)
        polling_handler = PollingHandler(self.polling_endpoint)
        polling_handler.start()
        migration_handler.start()
        forwarding_server.start()

        # TODO: Complete this

        while True:
            # This will eventually listen to the broker instead of stdin
            print("here?")
            command = input("> ").strip().lower().split()

            if (command[0] == "migrate"):
                if len(command) > 1:
                    self.migrate(command[1])
                else:
                    self.migrate(f'172.17.0.{self.my_number + 1}:8089')
            else:
                print("ERROR: invalid command")
