#!/bin/bash

# Update package lists
sudo apt-get update

# Install Python3 and pip
sudo apt-get install -y python3 python3-pip

# Install required Python packages
sudo pip3 install torch alpaca-trade-api yfinance transformers requests beautifulsoup4 

transformers-cli download nlptown/bert-base-multilingual-uncased-sentiment

# Install required system packages
sudo apt-get install -y libopenblas-dev
