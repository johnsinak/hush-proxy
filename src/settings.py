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


# TESTING_MIGRATION_TIMES = [10, 40, 70, 100, 130, 160, 190, 220, 250, 280]
TESTING_MIGRATION_TIMES = [10,110,180,230,260,280,290]
# NOTE: The first entry is always the main proxy
TESTING_MIGRATION_DESTS = ['54.81.201.249', '100.24.126.168', '34.204.173.200', '44.221.65.148', '44.220.42.99', '34.239.168.128', '44.222.69.5', '3.95.139.236']
# WHERE_TO_MIGRATE_NEXT = ["18.209.112.152","107.22.46.154","34.203.220.142","50.17.27.77","3.80.252.224","34.238.160.70","3.91.13.148"]


MIGRATION_DURATION_LOG_PATH = 'miglog.txt'
CONTROLLER_IP_ADDRESS = "3.91.73.130"