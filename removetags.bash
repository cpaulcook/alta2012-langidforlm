#!/bin/bash
# Remove SGML-like tags from a vertical corpus.
grep -v "^<.*>$" $1
