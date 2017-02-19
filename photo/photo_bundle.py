class PhotoBundle:
    raw = None
    processed = None
    background = None
    chroma = False
    images = None

    def __init__(self, raw, processed, chroma):
        self.raw = raw
        self.processed = processed
        self.chroma = chroma

    def __str__(self):
        return "[%s:%s" % (self.processed, self.raw)
