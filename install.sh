#!/bin/bash

# Update package lists
sudo apt-get update

# Install required system packages
sudo apt-get install -y libopenblas-dev

# Initialize conda
conda init bash

# Activate Anaconda environment
conda activate

# Install required Python packages
pip3 install pytz 

pip3 install numpy 

pip3 install scipy 

pip3 install alpaca-trade-api 

pip3 install yfinance 

pip3 install scikit-learn 

pip3 install torch 

pip3 install torchvision 

pip3 install transformers 

pip3 install requests 

pip3 install beautifulsoup4

transformers-cli download nlptown/bert-base-multilingual-uncased-sentiment

# Inform the user about Anaconda installation
echo "Your Python commands will be the Python commands that run with Anaconda's Python programs."
echo "You can install anything else with pip3 ."

# Inform the user about the virtual environment
echo "Your Python commands in the directory for Anaconda will be the Python commands that run this installed virtual environment's Python programs."

echo "type:   conda activate  " 

echo "type:    pip3 install pytz numpy scipy alpaca-trade-api yfinance scikit-learn torch torchvision transformers requests beautifulsoup4"

echo "View the installed pip3 packages with the command: pip3 list  "

echo "I have found that pip3 will prefer to install 1 package at a time. Try this. "

echo "Then the python 3 packages installation is complete. "
