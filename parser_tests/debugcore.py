from parser.boot import load_environment


class DebugStub:
    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None
        return _noop


load_environment()