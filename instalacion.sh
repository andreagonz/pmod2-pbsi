#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install Django==2.0.3
sudo pip3 install configparser
sudo pip3 install file_read_backwards
sudo pip3 install mod_wsgi

sudo apt-get install libncursesw5-dev
wget https://github.com/maxmind/geoip-api-c/releases/download/v1.6.11/GeoIP-1.6.11.tar.gz
tar -xzvf GeoIP-1.6.11.tar.gz
cd GeoIP-1.6.11
./configure
make
sudo make install

wget http://tar.goaccess.io/goaccess-1.2.tar.gz
tar -xzvf goaccess-1.2.tar.gz
cd goaccess-1.2/
./configure --enable-utf8 --enable-geoip=legacy
make
sudo make install
