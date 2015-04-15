class APIMethodObject(object):
    def __init__(self):
        self.callback = lambda: None

    def set_callback(self,func):
        self.callback = func

    def __call__(self,**kwargs):
        return self.callback(**kwargs)


class APIObject(object):
    def __init__(self):
        self._classes = set()
        self.__dict__ = dict()

    def __getattribute__(self,attr_name):
        try:
            return object.__getattribute__(self,attr_name)
        except Exception,e:
            return self.__getitem__(attr_name)

    def __getitem__(self,item_name):
        return  self.__dict__.__getitem__(item_name)

    def __setitem__(self,item_name,value):
        self.__dict__.__setitem__(item_name, value)

    def setdefault(self,item_name,value):
        self.__dict__.setdefault(item_name, value)

