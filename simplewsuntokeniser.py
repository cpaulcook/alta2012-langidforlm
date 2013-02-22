import sys

for line in sys.stdin:
    line = line.decode('utf8')
    line = line.strip()
    if line.startswith('<doc id=') or line.startswith('</doc>'):
        print line.encode('utf8')

    elif line.startswith('<p>'):
        print line.encode('utf8')
        curr_tokens = []

    elif line.startswith('</p>'):
        if curr_tokens is None:
            print >> sys.stderr, "Warning: </p> without <p>"
        else:
            tokens_str = ' '.join(curr_tokens)
            print tokens_str.encode('utf8')
            print line.encode('utf8')
            curr_tokens = None

    else:
        if curr_tokens is None:
            # Alternatively we could just assume there should have been a <p> tag 
            # and initialise curr_tokens to an empty list...
            print >> sys.stderr, "Warning: Not in <p>: Ignoring token %s" % line
        else:
            curr_tokens.append(line)
