FROM nginx:latest

RUN apt-get update && \
    apt-get install --no-cache -y procps

