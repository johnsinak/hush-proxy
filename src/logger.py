def log(message, pr=True):
    if pr:
        print(message)
    with open('log.txt', '+a') as f:
        f.write(message)
        f.write('\n')