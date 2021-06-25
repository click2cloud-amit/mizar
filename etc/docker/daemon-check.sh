#!/bin/bash

while : ; do
    nsenter -t 1 -m -u -n -i kubectl get pods --no-headers | grep -i -w daemon | awk {'print'} | grep Running > /dev/null
    if [ $? -ne 1 ]; then
        break
    fi
    echo "Waiting for mizar daemon running..."
    sleep 5
done