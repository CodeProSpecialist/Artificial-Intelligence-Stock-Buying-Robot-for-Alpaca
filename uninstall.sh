#!/bin/bash

# Uninstall Python packages
pip3 uninstall -y alpaca-trade-api yfinance transformers

# Remove system packages
sudo apt-get remove -y libopenblas-dev

# Purge configuration files for Python and system packages
sudo apt-get purge -y libopenblas-dev
