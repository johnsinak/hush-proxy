from Proxy import Proxy
from settings import *
import sys

nat_endpoint = NAT_ENDPOINT

if len(sys.argv) > 1:
    nat_endpoint = sys.argv[1]

proxy = Proxy(
    WIREGUARD_ENDPOINT,
    nat_endpoint,
    BROKER_ENDPOINT,
    MIGRATION_ENDPOINT,
    POLLING_ENDPOINT
)

proxy.run()