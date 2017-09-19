#!/usr/bin/env bash

sudo usermod -a -G docker $USER
echo "$DOCKER_LOGIN=bigblackbug" >> /etc/environment
echo "$DOCKER_PASSWORD=uhfyxltanf4" >> /etc/environment
