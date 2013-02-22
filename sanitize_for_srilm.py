import sys

# Get rid of lines with long tokens in SRILM format file (1 sent per
# line, WS delimited tokens) for input to SRILM.

max_t_len = 1000

for line in sys.stdin:
    line = line.strip()
    tokens = line.split()
    if all([len(t) < max_t_len for t in tokens]):
        print line
