from Proxy import Proxy
from settings import *

proxy = Proxy(
    WIREGUARD_ENDPOINT,
    NAT_ENDPOINT,
    BROKER_ENDPOINT,
    MIGRATION_ENDPOINT
)

proxy.run()