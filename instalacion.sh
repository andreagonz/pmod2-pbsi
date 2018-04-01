#!/bin/bash


OPTS=`getopt -o dv:g -- "$@"`
eval set -- "$OPTS"

if [ $? != 0 ] ; then echo "Error" >&2 ; exit 1 ; fi

while true; do
    case "$1" in
        
        -d)
            sudo apt-get install python3-pip
            sudo apt-get install net-tools sysstat libapache2-mod-wsgi-py3
            sudo a2enmod wsgi
            sudo pip3 install virtualenv
            shift
        ;;
        
        -v)
            virtualenv -p python3 $2
            source $2/bin/activate
            pip3 install Django==2.0.3
            pip3 install configparser
            pip3 install file_read_backwards
            pip3 install mod_wsgi
            shift
            ;;
        
        -g)
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
            shift
            ;;
        
        -- ) shift; break ;;
        * ) break ;;
    esac
done
