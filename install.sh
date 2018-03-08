#!/usr/bin/env bash
sudo apt-get remove docker docker-engine
sudo sh -c "echo 'LC_ALL=en_US.UTF-8' >> /etc/environment"
sudo sh -c "echo 'LC_CTYPE=en_US.UTF-8' >> /etc/environment"
source /etc/environment
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"
sudo apt-get update
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common docker-ce
sudo sh -c "curl -L https://github.com/docker/compose/releases/download/1.13.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"
sudo chmod +x /usr/local/bin/docker-compose
exit