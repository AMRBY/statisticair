#!/usr/bin/bash

## Extracting CSV without arrived_at: (flight_id, origin, destination, fix1, fix2, fix3)
awk 'BEGIN{FS=","}{if ($20 && $23 && $4!="M" && $20!=$(NF-2)){printf "%s,%s,%s,",$2,$5,$9;for (i=20;i<NF;i+=3) printf "%s ",$i; printf "\n"}}' $1>acb_without_date

## Extracting date(dd-mm-yy HH:MM:SS) 
awk 'BEGIN{FS=","}{if ($20 && $23 && $4!="M" && $20!=$(NF-2)){printf "%s\n", $13}}' $1 > acb_date

## Formating date to arrived_at(YYYY-mm-dd HH:MM:SS)
awk -F'[- ]' '{printf "20%s-%s-%s %s",$3,$2,$1,$4; printf "\n"}' acb_date > acb_date_formatted

## Fusionning "arrived_at" with CSV 
paste -d '\,' acb_date_formatted acb_without_date > $2

## Copy final ACB to SQL path
#sudo cp -p $2 /var/lib/mysql-files/
