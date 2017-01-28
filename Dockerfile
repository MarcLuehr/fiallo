FROM ubuntu:16.04
ADD idle.sh idle.sh

ENV USERNAME dockeruser
RUN useradd -m $USERNAME && \
        echo "$USERNAME:$USERNAME" | chpasswd && \
        usermod --shell /bin/bash $USERNAME && \
        usermod -aG sudo $USERNAME && \
        mkdir /etc/sudoers.d && \
        echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME && \
        chmod 0440 /etc/sudoers.d/$USERNAME && \
        usermod  --uid 1000 $USERNAME && \
        groupmod --gid 1000 $USERNAME

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y sudo qt5-default qttools5-dev-tools python3-pyqt5 pyqt5-dev-tools python3-pip
RUN pip3 install --upgrade pip

# requirements for zeroconf
RUN apt-get install -y python3-netifaces

ENTRYPOINT ./idle.sh
