class SegmentationFactory:
    registry = {}
    
    @classmethod
    def register(cls,method):
        def inner(wrapped_cls):
            cls.registry[method] = wrapped_cls
            return wrapped_cls
        return inner
    
    @classmethod
    def get(cls,method,**kwargs):
        return cls.registry[method](**kwargs)