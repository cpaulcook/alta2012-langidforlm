Code accompanying alta2012-langidforlm
==============================================

This repository contains code to reproduce experiments from the
following paper:

Paul Cook and Marco Lui. langid.py for better language modelling. In
Proceedings of the Australasian Language Technology Association
Workshop 2012 (ALTA 2012), pages 107–112. Dunedin, New Zealand.

Requirements:
------------

Jan Pomikalek's implementation of BTE: 
http://nlp.fi.muni.cz/~xpomikal/cleaneval/bte-3.0/bte.py

langid.py: https://github.com/saffsd/langid.py

Onion: http://code.google.com/p/onion/

StanfordNLP tools: http://www-nlp.stanford.edu/

ClueWeb09: http://www.lemurproject.org/clueweb09/


Building ClueWeb corpora
------------------------
To build the ClueWeb corpora, first create a file containing the paths
to the first 100 files in English ClueWeb. Then run 

# python extractvertcorporaforlangidexps.py FILE_OF_CLUEWEB_FILENAMES

(This takes a while...)

This creates 1 file per ClueWeb filename. The files are in vertical
format (token-per-line), whitespace separated. The "en" files contain
documents langid.py thinks are English, the "other" files contain
other languages.

Cat the extracted files together in various combinations. For the
paper we did the first 1, 5, 10, 50, 100 files, and just "en" and
"en"+"other". (So we created 10 files in total.)

(If you just want an English corpus from ClueWeb, and don't care about
reproducing our experiments, just cat all the "en" files into one
file at this stage.)

The next step is to put the files just created through the rest of the
corpus processing pipeline (to take care of deduplication, sentence
splitting, tokenisation, and getting rid of sentences with really long
tokens that seemed to trip up SRILM).

The path to the stanford NLP tools is hardcodede in
wsvert2srilm.bash. The path to Onion is hard-coded in
runonion.bash. You'll (probably) need to fix those accordingly.

Then run 

$ wsvert2srilm.bash FILE

This script creates files in sentence-per-line format, with tokens
separated by whitespace.
