#!/bin/bash

maps="`find maps -type f`"
bot1=$1
bot2=$2

rm -rf under_test

mkdir under_test
cp tron.py under_test
cp "$bot1" under_test/bot1.py
cp "$bot2" under_test/bot2.py

for map in $maps
do
  echo $map
  if [ -z $3 ]
  then
    java -jar engine/Tron.jar $map "under_test/bot1.py" "under_test/bot2.py" | grep -e "Win" -e "Draw" | tee under_test/log
  else
    java -jar engine/Tron.jar $map "under_test/bot1.py" "under_test/bot2.py"
  fi
done

echo "One   : `grep One under_test/log`"
echo "Two   : `grep Two under_test/log`"
echo "Draw  : `grep Draw under_test/log`"

rm -rf under_test
