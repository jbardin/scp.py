#!/bin/sh

set -e

# Sets up an SSH server
rm -Rf /tmp/ssh_server
mkdir /tmp/ssh_server
cd /tmp/ssh_server

# Server config file
cat >config <<'EOF'
Port 10022
ListenAddress 127.0.0.1

Protocol 2
HostKey /tmp/ssh_server/key_rsa
HostKey /tmp/ssh_server/key_dsa
UsePrivilegeSeparation no

# Authentication
LoginGraceTime 10
PermitRootLogin no
StrictModes no
UsePAM no

RSAAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile /tmp/ssh_server/client/id_rsa.pub

PrintMotd yes
EOF

# Server keys
ssh-keygen -f key_rsa -N '' -t rsa
ssh-keygen -f key_dsa -N '' -t dsa

# Client keys
umask 077
mkdir client || true
ssh-keygen -f client/id_rsa -N '' -t rsa
umask 022

# Starts the server
/usr/sbin/sshd -f config -h key_rsa -h key_dsa -p 10022

# Sets up the client
umask 077
mkdir ~/.ssh || true
cp client/id_rsa ~/.ssh/id_rsa
umask 022
rm -f ~/.ssh/known_hosts
# ssh-keyscan is bugged, don't use it
# ssh-keyscan -v -p 10022 -t rsa 127.0.0.1 >> ~/.ssh/known_hosts
ssh -o StrictHostKeyChecking=no \
    -o PasswordAuthentication=no \
    -p 10022 127.0.0.1 exit
cat ~/.ssh/known_hosts
