#!/bin/sh
# Entrypoint script for frontend nginx container
# Substitutes ${BACKEND_URL} at runtime so the same image works in any environment

export MAX_UPLOAD_SIZE=${MAX_UPLOAD_SIZE:-50M}
envsubst '${BACKEND_URL} ${MAX_UPLOAD_SIZE}' < /etc/nginx/conf.d/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
