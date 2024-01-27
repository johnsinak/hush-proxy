import subprocess
import threading
import socket
from time import time

from settings import *


def run_script_in_background(script_path='../scripts/measure.sh'):
    try:
        process = subprocess.Popen(['bash', script_path])

        print(f"Shell script '{script_path}' is running in the background.")
        return process
    except Exception as e:
        print(f"Error running the shell script: {e}")
        return None


class TestingMigrationSenderThread(threading.Thread):
    def __init__(self, start_time, duration):
        threading.Thread.__init__(self)
        self.start_time = start_time
        self.duration = duration

    def run(self):
        print(f"==== test migration sender running...")
        counters = [0] * len(TESTING_MIGRATION_TIMES)
        is_done = 0
        while True:
            right_now = time() - self.start_time

            for i in range(len(TESTING_MIGRATION_TIMES) - 1, -1, -1):
                if TESTING_MIGRATION_TIMES[i] < right_now and counters[i] == 0:
                    # TESTING_MIGRATION_DESTS
                    print(f'sending to {i} to migrate to {i+1}')
                    ip_src = TESTING_MIGRATION_DESTS[i]
                    ip_dest = TESTING_MIGRATION_DESTS[i+1]

                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((ip_src, BROKER_PORT))

                    message = f"migrate {ip_dest}"
                    client_socket.send(message.encode('utf-8'))
                    client_socket.close()

                    counters[i] = 1
                    is_done += 1
            if is_done == len(TESTING_MIGRATION_TIMES):break
        print('migation work is done.')