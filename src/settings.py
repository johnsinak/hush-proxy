WIREGUARD_INTERFACE_NAME = "wg0"
WIREGUARD_CONFIG_LOCATION = f"/etc/wireguard/{WIREGUARD_INTERFACE_NAME}.conf"
MIGRATION_PORT = 8089
POLLING_PORT = 8120
BROKER_PORT = 8121
POLLING_ENDPOINT = ("0.0.0.0", POLLING_PORT)

WIREGUARD_ENDPOINT = ("10.27.0.20", 8088)
NAT_ENDPOINT =       ("172.17.0.6", 8000)
BROKER_ENDPOINT =    ("0.0.0.0", BROKER_PORT)
MIGRATION_ENDPOINT = ("0.0.0.0", MIGRATION_PORT)
WIREGUARD_PORT = 51820
