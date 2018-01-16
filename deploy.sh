#!/bin/bash
set -e

if [ -z ${REMOTE_HOST+x} ]; then
    echo "Please set the REMOTE_HOST env variable";
    exit 1
fi

if [ -z ${FORHANDS_PROFILE+x} ]; then
    echo "Please set the FORHANDS_PROFILE env variable";
    exit 1
fi

# creating a correct folder
ssh ubuntu@${REMOTE_HOST} -o "StrictHostKeyChecking no" << EOF
    mkdir -p ~/${FORHANDS_PROFILE}
EOF

# copying a correct compose file
scp -o "StrictHostKeyChecking no" composefiles/compose-run-${FORHANDS_PROFILE}.yml \
    ubuntu@${REMOTE_HOST}:~/${FORHANDS_PROFILE}/docker-compose.yml

COMPOSE_OPTS="-f ./docker-compose.yml -p 4hands_${FORHANDS_PROFILE}"

# starting containers on the remote server
ssh ubuntu@${REMOTE_HOST} -o "StrictHostKeyChecking no" << EOF
    docker login -u $DOCKER_LOGIN -p $DOCKER_PASSWORD
    cd ~/${FORHANDS_PROFILE}
    docker-compose ${COMPOSE_OPTS} pull
    docker-compose ${COMPOSE_OPTS} down
    DEPLOY_PORT=${DEPLOY_PORT} DEPLOY_HTTPS_PORT=${DEPLOY_HTTPS_PORT} \
    docker-compose ${COMPOSE_OPTS} up -d
    echo "Applying a shitty permission fix"
    sleep 10
    sudo chown -R ${OWNER_USER_GROUP} /var/lib/4hands2go/dev-media/
    sudo chown -R ${OWNER_USER_GROUP} /var/lib/4hands2go/dev-static/
    sudo chown -R ${OWNER_USER_GROUP} /var/logs/4hands2go/dev/
EOF

echo "Done!"
exit 0
