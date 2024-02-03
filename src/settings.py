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


TESTING_MIGRATION_TIMES = [20,40,60,80,100,120,140,160,180,200]
# NOTE: The first entry is always the main proxy
TESTING_MIGRATION_DESTS = ['54.81.201.249', '44.204.203.249', '3.80.142.120', '3.237.175.236', '34.200.241.13', '3.239.162.205', '44.211.53.131', '44.222.236.9', '44.201.18.33', '34.232.44.72', '35.172.110.165']
# WHERE_TO_MIGRATE_NEXT = ["18.209.112.152","107.22.46.154","34.203.220.142","50.17.27.77","3.80.252.224","34.238.160.70","3.91.13.148"]


MIGRATION_DURATION_LOG_PATH = 'miglog.txt'
CONTROLLER_IP_ADDRESS = "3.91.73.130"