class PhotoBundle:
    raw = None
    processed = None
    web = None

    def __init__(self, raw, processed, web):
        self.raw = raw
        self.processed = processed
        self.web = web

    def __str__(self):
        return "[%s:%s:%s]" % (self.processed, self.raw, self.web)
