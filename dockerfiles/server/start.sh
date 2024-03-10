#!/usr/bin/bash

# Start script that checks out the specified branch or tag, 
# installs the server package from that branch or tag,
# and starts the flask server.

set -e  # This will cause the script to exit if any command fails


# Start Gunicorn
# gunicorn --workers 2 --threads 8 --bind 0.0.0.0:8000 --access-logfile - app.server:flask_app

cd server && poetry run python -m app.main

exit $?
