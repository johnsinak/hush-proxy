FROM python:3.11-slim-bookworm
RUN apt update && apt install wireguard-tools nano iputils-ping iproute2 -y
COPY . /
RUN pip install -r /requirements.txt


CMD ["/bin/bash"]