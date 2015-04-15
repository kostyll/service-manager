from types import ModuleType, MethodType, ClassType

import explorer

class Service(object):
    def __init__(self,service_initial_object):
        if isinstance (service_initial_object,'str'):
            pass
        if isinstance (service_initial_object, ModuleType):
            pass

