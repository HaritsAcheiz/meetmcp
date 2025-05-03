FROM n8nio/n8n:1.90.0

USER root

RUN apk update && apk add --no-cache docker-cli

RUN addgroup -g 996 docker && addgroup node docker

USER node