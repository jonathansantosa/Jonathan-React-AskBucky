#!/bin/bash

# Start Nginx using start-stop-daemon

# Path to Nginx binary
NGINX_BIN="/usr/sbin/nginx"

# Path to Nginx configuration file
NGINX_CONF="/etc/nginx/nginx.conf"

# Start Nginx server
$NGINX_BIN -c $NGINX_CONF -g "daemon off;"