class PhotoBundle:
    raw = None
    processed = None

    def __init__(self, raw, processed):
        self.raw = raw
        self.processed = processed

    def __str__(self):
        return "[%s:%s" % (self.processed, self.raw)
