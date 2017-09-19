#!/usr/bin/env bash
set -e
docker-compose -f composefiles/compose-build.yml build
docker-compose -p 4hands-local -f composefiles/compose-run-local.yml up -d