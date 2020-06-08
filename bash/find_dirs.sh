#!/bin/bash

if [ $# -eq 0 ]; then
    echo ">>> No arguments supplied, exiting"
    exit 1
fi

if [ -z "$1" ]; then
    echo ">>> No arguments supplied, exiting"
    exit 1
fi

ROOT_DIR=$1

if [ ! -d $ROOT_DIR ]; then
    echo ">>> Root dir ($ROOT_DIR) does not exist or not connected, exiting"
    exit 0
fi

echo ' Root dir: ' $ROOT_DIR

declare -a BOOK_LIST_XX=(
  'Lois Lowry - The Giver'
  'Stephen Chbosky - The Perks of Being a Wallflower'
  'John Knowles - A Separate Peace'
  'Mark Twain - The Adventures of Tom Sawyer or Huckleberry Finn'
  'John Green - The Fault of our Stars'
  'John Green - Looking for Alaska'
  'Suzanne Collins - The Ballad of Songbirds and Snakes'
  'Louisa May Alcott - Little Women'
  'Richard Adams - Watership Down'
  'John Green - Looking for Alaska'
  'Alex Michaelides - The Silent Patient'
  'Sally Rooney - Normal People'
  'Erik Larson - The Splendid and the Vile'
  'Tayari Jones - An American Marriage'
  'Gail Honey - Eleanor Oliphant is Completely Fine'
  'Amor Towles - A Gentleman in Moscow'
  'Erin Morgenstern - The Night Circus'
  'Kate Quinn - The Alice Network'
  'Christopher McDougall - born to run'
);
declare -a BOOK_LIST=(
  'Lois Lowry - Giver'
  'Stephen Chbosky - Wallflower'
  'John Knowles - Peace'
  'Mark Twain - Huckleberry'
  'John Green - Fault'
  'John Green - Alaska'
  'Suzanne Collins - Songbirds'
  'Louisa May Alcott - Women'
  'Richard Adams - Watership'
  'Alex Michaelides - Patient'
  'Sally Rooney - Normal'
  'Erik Larson - Splendid'
  'Tayari Jones - Marriage'
  'Gail Honey - Oliphant'
  'Amor Towles - Gentleman'
  'Erin Morgenstern - Circus'
  'Kate Quinn - Alice'
  'Christopher McDougall - Born'
);

COUNT=${#BOOK_LIST[@]} 

for idx in $(seq 0 $(($COUNT-1)) )
do
  echo "*************************************************************************************"
  echo "  [$(($idx+1)) of $COUNT] Searching for: \"${BOOK_LIST[$idx]}\""
  echo "*************************************************************************************"
  IFS='-'
  read -ra author_title_array <<< "${BOOK_LIST[$idx]}"
  author="$(echo -e "${author_title_array[0]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  book="$(echo -e "${author_title_array[1]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

  find $ROOT_DIR -type d | grep -i ".*${author}*" | grep -i ".*${book}*"
  #find . -type d -iregex ".*${author}*"
done




