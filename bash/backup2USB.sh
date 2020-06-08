#!/bin/bash

#
# good crontab for this: 
#   0 17 * * *  /Users/trafferty/backup2USB.sh /Volumes/MacOS_SG/backup 2>&1 | tee -a ~/backup_log.txt
#

echo '-------------------------------------------------------------' 
echo 'Backup starting ('${0##*/}'):' $(date +%m-%d-%yT%H:%M:%S)
echo '-------------------------------------------------------------' 

if [ $# -eq 0 ]; then
    echo ">>> No arguments supplied, exiting"
    exit 1
fi

if [ -z "$1" ]; then
    echo ">>> No arguments supplied, exiting"
    exit 1
fi

TARGET=$1

if [ ! -d $TARGET ]; then
    echo ">>> Target ($TARGET) does not exist or not connected, exiting"
    exit 0
fi

echo ' Target: ' $TARGET

declare -a SOURCES=(
  '/Users/trafferty/*.sh'
  '/Users/trafferty/.bashrc'
  '/Users/trafferty/.bash_history'
  '/Users/trafferty/.bash_aliases'
  '/Users/trafferty/.ssh'
  '/Users/trafferty/Music/iTunes/iTunes Media/Music'
  '/Users/trafferty/Documents'
  '/Users/trafferty/bin'
  '/Users/trafferty/data'
  '/Users/trafferty/tmp'
  '/Users/trafferty/src'
  '/Users/trafferty/Downloads'
  '/Users/trafferty/Pictures'
  '/Users/trafferty/Movies'
  '/Users/trafferty/dev'
  '/Users/trafferty/workspace'
  '/Users/trafferty/VirtualBox VMs'
  '/Users/trafferty/Virtual Machines.localized'
  '/usr/local/var/db/redis/dump.rdb'
);

COUNT=${#SOURCES[@]} 

for idx in $(seq 0 $(($COUNT-1)) )
do
  echo "*************************************************************************************"
  echo "  rsync $(($idx+1)) of $COUNT: ${SOURCES[$idx]} $TARGET"
  echo "*************************************************************************************"
  if [ -d "${SOURCES[$idx]}" ]
  then
    echo '>>>  copying directory:' ${SOURCES[$idx]}
    /usr/bin/rsync -av --progress "${SOURCES[$idx]}" $TARGET
  else
    echo '>>>  copying file:' ${SOURCES[$idx]}
    /usr/bin/rsync -av --progress "${SOURCES[$idx]}" $TARGET/
  fi
done

echo '-------------------------------------------------------------' 
echo 'Backup complete ('${0##*/}'):' $(date +%m-%d-%yT%H:%M:%S)
echo '-------------------------------------------------------------' 
