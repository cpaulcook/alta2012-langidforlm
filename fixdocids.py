import sys

for line in sys.stdin:
    line = line.decode('utf8').strip()
    if line.startswith('<doc id="') and not line.endswith('>'):
        line += ">"
    print line.encode('utf8')
