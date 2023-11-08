from server_threads import *
from settings import *


class Proxy:
    def __init__(self, wireguard_endpoint, nat_endpoint, broker_endpoint, migration_endpoint) -> None:
        """
        endpoints are tuples of: (address, port)
        """
        self.wireguard_endpoint = wireguard_endpoint
        self.nat_endpoint = nat_endpoint
        self.broker_endpoint = broker_endpoint
        self.migration_endpoint = migration_endpoint
    
    def migrate(self, new_proxy_endpoint):
        # migrate address:port
        global client_addresses
        with open(WIREGUARD_CONFIG_LOCATION, "rb") as f:
            data = f.read()
        new_proxy_address, new_proxy_socket = new_proxy_endpoint.split(':')
        new_proxy_socket = int(new_proxy_socket)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((new_proxy_address, new_proxy_socket))
        s.sendall(data)

        print(f'sending migration notice to {len(client_addresses)} clients')
        print(client_addresses)
        for address in client_addresses:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address[0], 8089))
            s.sendall(f"{new_proxy_address}:{WIREGUARD_PORT}".encode())
            s.close()


    def run(self):
        forwarding_server = ForwardingServerThread(self.wireguard_endpoint, self.nat_endpoint)
        migration_handler = MigrationHandler(self.migration_endpoint)
        print("here?")
        migration_handler.start()
        print("here?")
        forwarding_server.start()
        print("here?")

        while True:
            # This will eventually listen to the broker instead of stdin
            print("here?")
            command = input("> ").strip().lower().split()

            if (command[0] == "migrate"):
                if len(command) > 1:
                    self.migrate(command[1])
                else:
                    self.migrate('172.17.0.4:8089')
            else:
                print("ERROR: invalid command")