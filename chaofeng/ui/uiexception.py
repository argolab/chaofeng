class BaseUIInterrupt(Exception):
    pass

class TermitorInputInterrupt(BaseUIInterrupt):
    pass

class SkipInputInterrupt(BaseUIInterrupt):
    pass

class NullValueError(BaseUIInterrupt):
    pass
