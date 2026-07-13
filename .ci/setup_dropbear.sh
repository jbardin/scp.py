#!/bin/sh

set -e

docker run -d --name dropbear -p 2222:22 ubuntu:24.04 sh -c "apt-get update && apt-get install -qq dropbear-bin && cd /root && cd /root && dropbearkey -t rsa -f id_rsa && dropbear -r id_rsa -F -E"

WAITED=0
while ! nc -z localhost 2222; do
    if [ $WAITED -ge 120 ]; then
        echo "dropbear didn't come up after $WAITED" >&2
        exit 1
    fi
    sleep 3
    WAITED=$((WAITED + 3))
done
