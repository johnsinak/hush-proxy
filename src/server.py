from pro import Proxy
from settings import *
import sys

nat_endpoint = NAT_ENDPOINT

if len(sys.argv) > 1:
    nat_host, nat_port = sys.argv[1].split(':')
    nat_endpoint = (nat_host, int(nat_port))
    print(f'nat endpoint set to: {nat_host}:{nat_port}')

proxy = Proxy(
    WIREGUARD_ENDPOINT,
    nat_endpoint,
    BROKER_ENDPOINT,
    MIGRATION_ENDPOINT,
    POLLING_ENDPOINT
)

proxy.run()