# Base image
FROM python:3.10

USER root

ENV PYTHONUNBUFFERED 1
ENV REPO askbucky

# Install system dependencies
RUN apt-get update && apt-get install -y bash vim dos2unix

# Set up the working directory
WORKDIR /app

# Copy the server directory and start.sh script to the container
ADD server /app/server
COPY dockerfiles/server/start.sh /app/server

# Convert line endings of the start.sh script if not Windows
RUN if [ "$(uname -s)" != "Windows" ]; then dos2unix /app/server/start.sh; fi

# Install Poetry
RUN pip install poetry

# Install project dependencies using Poetry
RUN cd server && poetry install --no-root

# Set Python 3.10 as the default version
RUN echo "alias python=python3.10" >> ~/.bashrc

# Set executable permissions for the start.sh script
RUN chmod +x /app/server/start.sh

# Set the command to execute the start.sh script
CMD [ "/bin/bash", "/app/server/start.sh" ]
