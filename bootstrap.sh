#!/usr/bin/env bash

apt-get update
apt-get -y install python-pip
pip install Flask
pip install requests
pip install Flask-Limiter
pip install -U pytest
pip install pytest-cov