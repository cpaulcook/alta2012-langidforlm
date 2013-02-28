#!/bin/sh
# Run all the language models trained from ClueWeb against the srilm files
# from each of the domains.

for i in `find -L ../data/clueweblangid_corpora -name '*.srilm' | grep -v 00`; do 
   PPL_FILE=`basename $i .srilm`.ppl; 
   if [ ! -e $PPL_FILE ]; then
     echo "DO $PPL_FILE";
     find . -maxdepth 1 -type f  -name '*.lm' | parallel -j1 "echo {};ngram -ppl $i -unk -lm {};echo " > $PPL_FILE;
     ./LMout2csv.py ${PPL_FILE} | sort > ${PPL_FILE}.csv;
   else
     echo "EXISTS $PPL_FILE";
   fi
done
