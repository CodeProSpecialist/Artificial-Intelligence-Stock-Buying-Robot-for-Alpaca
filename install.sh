#!/bin/bash

# Update package lists
sudo apt-get update

# Install required system packages
sudo apt-get install -y libopenblas-dev

# Install required Python packages
pip3 install torch alpaca-trade-api yfinance transformers requests beautifulsoup4 

transformers-cli download nlptown/bert-base-multilingual-uncased-sentiment
