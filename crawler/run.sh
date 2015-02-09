#!/bin/sh
for i in 1000 2000 3000;
do
  j=1000-i
  scrapy crawl cine -a sidx=$i -a eidx=$j -o "critic-new-$i".jsonlines -t jsonlines --logfile=log$i.txt &
done
