KEYS_DIR=key_store


all: full

full: build
	wg --version 

restart: dockerrm build
	docker run -dit --cap-add=NET_ADMIN --name=peer1 wg-peer
	docker run -dit --cap-add=NET_ADMIN --name=server wg-peer
	docker run -dit --cap-add=NET_ADMIN --name=server2 wg-peer


build:
	docker build -t wg-peer .
	docker build -t nat-server -f NATDockerfile .

keys:
	wg genkey | tee ${KEYS_DIR}/peer1/privatekey | wg pubkey > ${KEYS_DIR}/peer1/publickey
	wg genkey | tee ${KEYS_DIR}/peer2/privatekey | wg pubkey > ${KEYS_DIR}/peer2/publickey
	wg genkey | tee ${KEYS_DIR}/server/privatekey | wg pubkey > ${KEYS_DIR}/server/publickey
	wg genkey | tee ${KEYS_DIR}/server2/privatekey | wg pubkey > ${KEYS_DIR}/server2/publickey

ready:
	cp ${KEYS_DIR}/${name}/wg0.conf etc/wireguard/
	wg-quick up wg0

mk:
	mkdir ./${BUILD_DIR}

dockerrm:
	-docker rm server peer1 server2

rename:
	$(eval CC = clang++ -std=c++11 -pthread)

mac: rename ${OUTPUT_NAME}

install:
	sudo apt update
	sudo apt install libsdl2-dev

.PHONY: clean

clean:
	rm -rf ${BUILD_DIR}/ ./${OUTPUT_NAME}