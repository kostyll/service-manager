from types import ModuleType, MethodType, ClassType

import explorer
import common
from common import APIObject

class Service(object):
    pass


class ServiceBuilder(object):

    def build(self,service_initial_object):

        # ACCESSING MODULE BY PATH
        if isinstance (service_initial_object,str):
            pass

        # ACCESSING MODULE BY IMPORTED OBJECT
        if isinstance (service_initial_object, ModuleType):
            pass

        # ACCESSING MODULE BY APIObject class instance
        if isinstance (service_initial_object, APIObject):
            pass

        # ACCESSING MODULE BY EXPLORING host:port pare
        if isinstance (service_initial_object, tuple):
            pass


