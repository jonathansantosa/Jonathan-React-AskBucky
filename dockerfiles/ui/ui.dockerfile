# Base image
FROM node:21

USER root

ENV PYTHONUNBUFFERED 1
ENV NVM_DIR $HOME/.nvm
ENV REPO askbucky

RUN mkdir -p $NVM_DIR

# Install system dependencies
RUN apt-get update && apt-get install -y vim curl nodejs npm dos2unix

WORKDIR /app
ADD ui /app/ui
COPY dockerfiles/ui/install_packages.sh /app/ui

RUN if [ "$(uname -s)" != "Windows" ]; then dos2unix /app/ui/install_packages.sh; fi

# Install node.js and package dependencies
RUN chmod +x /app/ui/install_packages.sh
RUN /app/ui/install_packages.sh

WORKDIR /app/ui

CMD [ "npm", "start" ]