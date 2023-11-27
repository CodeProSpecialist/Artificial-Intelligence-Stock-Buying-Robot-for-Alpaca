#!/bin/bash

# Update package lists
sudo apt-get update

# Install Python3 and pip
sudo apt-get install -y python3 python3-pip

# Install required Python packages
pip3 install alpaca-trade-api yfinance transformers

# Install required system packages
sudo apt-get install -y libopenblas-dev