#!/bin/sh
for i in 0 1000 2000 3000;
do
  j=1000-i
  scrapy crawl cine -a sidx=$i -a eidx=$j -o "critic-$i".jsonlines -t jsonlines --logfile=log.txt
done
