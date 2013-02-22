#!/bin/bash
mkdir tmp
~/onion-1.1/src/hashgen -n7 -o tmp/7gram_hashes. $1
~/onion-1.1/src/hashdup -o tmp/dup_7gram_hashes tmp/7gram_hashes.* 
~/onion-1.1/src/onion -s -n7 -f tmp/dup_7gram_hashes $1 > $1.dedup
rm -rf tmp
