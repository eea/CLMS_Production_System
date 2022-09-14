#!/bin/bash

# Script variables
DIR=ca_certificates
CERT_DURATION=3650

# Creates the directory if not exists already
if [[ ! -e $DIR ]]; then
    mkdir $DIR
fi

# Generates a private key without passphrase
openssl genrsa -out ./ca_certificates/server.key 2048

# Generates the server certificate
openssl req -new -key ./ca_certificates/server.key \
        -days $CERT_DURATION \
        -out ./ca_certificates/server.crt \
        -x509 \
        -subj '/C=AT/ST=Tyrol/L=Innsbruck/O=GeoVille Information Systems and Data Processing GmbH/CN=oauth.clcplusbackbone.geoville.com/emailAddress=IT-Services@geoville.com'

# Generates the server certificate
cp ./ca_certificates/server.crt ./ca_certificates/root.crt
