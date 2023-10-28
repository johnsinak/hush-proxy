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
        with open(WIREGUARD_CONFIG_LOCATION, "rb") as f:
            data = f.read()
        new_proxy_address = new_proxy_endpoint.split(':')[0]
        new_proxy_socket = new_proxy_endpoint.split(':')[1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((new_proxy_address, new_proxy_socket))
        s.sendall(data)

    def run(self):
        forwarding_server = ForwardingServerThread(self.wireguard_endpoint, self.nat_endpoint)
        migration_handler = MigrationHandler(self.migration_endpoint)
        forwarding_server.daemon = 1
        migration_handler.daemon = 1
        forwarding_server.run()
        migration_handler.run()

        while True:
            # This will eventually listen to the broker instead of stdin
            command = input("> ").strip().lower().split()

            if (command[0] == "migrate" and len(command) > 1):
                self.migrate(command[1])
            else:
                print("ERROR: invalid command")