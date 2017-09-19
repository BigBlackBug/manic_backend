#!/usr/bin/env bash
set -e
docker-compose -f composefiles/compose-build.yml build
docker-compose -f composefiles/compose-test.yml -p 4hands-test up --abort-on-container-exit --exit-code-from app
