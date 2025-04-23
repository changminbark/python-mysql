#!/bin/bash

# List of containers to check
containers=("mysql-db")
logfile=("../logs/container_health.log")

for container in "${containers[@]}"; do
    # Check if container is running
    if ! sudo docker inspect -f '{{.State.Running}}' "$container" 2>/dev/null | grep true > /dev/null; then
        echo "$(date): $container is NOT running"
        continue
    fi

    # Check if the container is healthy (only if HEALTHCHECK is defined)
    health_status=$(sudo docker inspect -f '{{.State.Health.Status}}' "$container" 2>/dev/null)

    if [ "$health_status" != "healthy" ]; then
        echo "$(date): $container is NOT healthy - status: $health_status"
        echo "$(date): $container is NOT healthy - status: $health_status" >> $logfile
        # Optional: restart the container
        # docker restart "$container"
    else
        echo "$(date): $container is healthy"
        echo "$(date): $container is healthy" >> $logfile
    fi
done
