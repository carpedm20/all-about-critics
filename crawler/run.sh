#!/bin/sh
for i in 0 1000 2000 3000;
do
  scrapy crawl cine -a start_idx=$i -o "critic-$i".jsonlines -t jsonlines --logfile=log.txt
done
