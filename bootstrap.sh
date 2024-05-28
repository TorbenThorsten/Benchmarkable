#!/bin/bash

# Variables
ANSIBLE_USER=ansible
ANSIBLE_HOME=/home/$ANSIBLE_USER
SSH_DIR=$ANSIBLE_HOME/.ssh
AUTHORIZED_KEYS=$SSH_DIR/authorized_keys
ANSIBLE_PUBLIC_KEY="YOUR_PUBLIC_KEY_HERE"

# Create ansible user and set up SSH
useradd -m -s /bin/bash $ANSIBLE_USER
echo "$ANSIBLE_USER ALL=(ALL) NOPASSWD:ALL" | tee /etc/sudoers.d/$ANSIBLE_USER

# Set up SSH directory and authorized keys
mkdir -p $SSH_DIR
echo "$ANSIBLE_PUBLIC_KEY" | tee $AUTHORIZED_KEYS
chown -R $ANSIBLE_USER:$ANSIBLE_USER $SSH_DIR
chmod 700 $SSH_DIR
chmod 600 $AUTHORIZED_KEYS

# Ensure correct permissions for the sudoers file
chmod 440 /etc/sudoers.d/$ANSIBLE_USER

#Ensure python3 is installed

apt update

apt install python3

echo "Bootstrap script completed. Ansible user setup with SSH key. Dependencies installed"