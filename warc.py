import cStringIO

class WarcRecord:
    def __init__(self, infile, version):
        self.header = {}
        self.header_str = version + "\n"
        for line in infile:
            self.header_str += line
            line = line.strip()
            if not line:
                break

            line = line.split(':', 1)
            if len(line) == 1:
                self.header[prev_k] += line[0].strip()
                
            elif len(line) == 2:
                k,v = line
                prev_k = k
                self.header[k.strip()] = v.strip()
            else:
                # This shouldn't happen so blow up...
                assert False

        self.content = infile.read(int(self.header['Content-Length']))

    def warc_type(self):
        return self.header['WARC-Type']

    def is_response(self):
        return self.warc_type() == 'response'

    def is_warcinfo(self):
        return self.warc_type() == 'warcinfo'

class WarcResponse:
    def __init__(self, warc_response):
        self.header = warc_response.header
        self.header_str = warc_response.header_str
        self.content = warc_response.content
        self.tld = self.header['WARC-Target-URI'].split('/')[2].split('.')[-1].split(':')[0]

        self.http_header = {}
        for line in cStringIO.StringIO(self.content):
            line = line.strip()
            if not line:
                break
            if line.startswith('HTTP'):
                continue
            k,v = line.split(':', 1)
            k = k.strip()
            if not self.http_header.has_key(k):
                self.http_header[k] = v.strip()

    def good_doc_for_corpus(self, min_size=5000, max_size=200000, 
                            mime_types=set(['text/html'])):
        return self.header['WARC-Type'] == 'response' and \
            min_size <= len(self.content) <= max_size and \
            self.http_header.has_key('Content-Type') and \
            self.http_header['Content-Type'].split(';')[0] in mime_types

    def __str__(self):
        return self.header_str + self.content[:-1]

def get_warcs(infile):
    while infile:
        wr = WarcRecord(infile)
        yield wr

        # ***** Not quite sure what's up with needing this extra read
        # ***** here...  *****
        if wr.is_warcinfo():
            infile.read(1)

def get_warcs(infile):
    version = infile.readline().strip()
    while version:
        assert version == "WARC/0.18"
        wr = WarcRecord(infile, version)
        yield wr

        # ***** Not quite sure what's up with needing this extra read
        # ***** here...  *****
        if wr.is_warcinfo():
            infile.read(1)
        version = infile.readline().strip()

def get_warc_responses(infile):
    for wr in get_warcs(infile):
        if wr.is_response():
            yield WarcResponse(wr)

if __name__ == '__main__':
    import gzip, sys
    for wr in get_warc_responses(gzip.open(sys.argv[1])):
        print wr.header['WARC-Target-URI']
