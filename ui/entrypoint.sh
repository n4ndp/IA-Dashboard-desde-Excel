#!/bin/sh
# Entrypoint script for frontend nginx container
# Substitutes ${BACKEND_URL} at runtime so the same image works in any environment

envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
