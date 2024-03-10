#!/usr/bin/bash

set -e  # This will cause the script to exit if any command fails
NVM_DIR=/.nvm

echo "Installing nvm..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash

if [ -f /.nvm/nvm.sh ]; then
	echo "Sourcing nvm.sh file..."
	source /.nvm/nvm.sh
fi

cd /app/ui
nvm install && nvm use && npm install

exit $?