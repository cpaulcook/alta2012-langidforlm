#!/bin/bash

echo "Fixing doc ids..."
cat $1 | python fixdocids.py > $1.fixids

echo "Deduping..."
bash runonion.bash $1.fixids

echo "Untokenising and removing corpus tags..."
cat $1.fixids.dedup | python simplewsuntokeniser.py | bash removetags.bash > $1.fixids.dedup.un_tok.no_tags

echo "Tokenising, sentence splitting, sentence per lining, and sanitizing..."
java -cp ~/stanford-corenlp-2012-07-09/stanford-corenlp-2012-07-09.jar edu.stanford.nlp.process.DocumentPreprocessor $1.fixids.dedup.un_tok.no_tags | python sanitize_for_srilm.py | gzip > $1.srilm.gz

echo "Cleaning up..."
rm $1.fixids
rm $1.fixids.dedup.un_tok.no_tags
