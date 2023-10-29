KEYS_DIR=key_store


all: full

full:
	wg --version

build:
	docker build -t wg-peer .
	docker build -t nat-server -f NATDockerfile .

keys:
	wg genkey | tee ${KEYS_DIR}/peer1/privatekey | wg pubkey > ${KEYS_DIR}/peer1/publickey
	wg genkey | tee ${KEYS_DIR}/peer2/privatekey | wg pubkey > ${KEYS_DIR}/peer2/publickey
	wg genkey | tee ${KEYS_DIR}/server/privatekey | wg pubkey > ${KEYS_DIR}/server/publickey

mk:
	mkdir ./${BUILD_DIR}

rm:
	rm -rf ${BUILD_DIR}/ ./${OUTPUT_NAME}

rename:
	$(eval CC = clang++ -std=c++11 -pthread)

mac: rename ${OUTPUT_NAME}

install:
	sudo apt update
	sudo apt install libsdl2-dev

.PHONY: clean

clean:
	rm -rf ${BUILD_DIR}/ ./${OUTPUT_NAME}