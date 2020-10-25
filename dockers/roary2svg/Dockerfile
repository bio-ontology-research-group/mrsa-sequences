FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y moreutils liblist-moreutils-perl libtext-csv-perl libfile-path-tiny-perl libpath-tiny-perl libsvg-perl

RUN curl -L -O https://raw.githubusercontent.com/tseemann/nullarbor/master/bin/roary2svg.pl

RUN chmod +x roary2svg.pl

RUN mv roary2svg.pl /usr/local/bin/

