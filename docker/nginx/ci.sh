#!/bin/sh

set -o errexit
set -o nounset

# Testing configuration:
nginx -t

# Success
echo "Nginx configuration is valid."
exit 0
