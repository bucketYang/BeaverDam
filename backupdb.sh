#!/bin/bash
abc=100
while true;do
    cp db.sqlite3 /home/gemfield/DB/db.sqlite3.${abc}
    abc=$((abc+1))
    sleep 3600
done
