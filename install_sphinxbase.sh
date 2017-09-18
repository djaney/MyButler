#!/bin/bash
apt-get install unzip bison autoconf libtool swig pulseaudio -y
wget -O sb.zip https://github.com/cmusphinx/sphinxbase/archive/master.zip
unzip sb
cd sphinxbase-master/

./autogen.sh 
make
make install
