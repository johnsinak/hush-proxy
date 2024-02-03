import subprocess
from src.settings import *
import os

server_ip = TESTING_MIGRATION_DESTS[0]
peers_with_publickeys = []

# peer template needs: num1.num2 private_key server_endpoint

for peer_number in range(3,5000):
    folder = f'key_store/peer{peer_number}/'
    try:
        os.system(f'rm -rf {folder}')
    except Exception as e:
        print(e)
    os.mkdir(folder)
    os.system(f'wg genkey | tee key_store/peer{peer_number}/privatekey | wg pubkey > key_store/peer{peer_number}/publickey')
    with open(f'{folder}privatekey') as f:
        private_key = f.read().strip()
    
    with open(f'{folder}publickey') as f:
        publickey = f.read().strip()

    with open(f'./templates/singlepeer_for_server_template.txt') as f:
        peer_template = f.read()

    peers_with_publickeys.append(peer_template.format(publickey))

    with open('./templates/peertemplate.txt') as f:
        template = f.read()
    
    num1 = peer_number//200
    num2 = (peer_number % 200) + 22

    filetowrite = template.format(num1,num2, private_key, server_ip)
    
    with open(f'{folder}wg0.conf', 'w') as f:
        f.write(filetowrite)
    
    # if peer_number > 5: break

with open('./templates/serverbase.txt') as f:
    server_base = f.read()

with open(f'key_store/server/wg0.conf', 'w') as f:
    f.write(server_base)
    f.write('\n'.join(peers_with_publickeys))
