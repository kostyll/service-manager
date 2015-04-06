
class BaseAPI(object):
    """
    Base class API
    """
    def __init__(self):
        self._methods = {}
        self.register_methods()
        self.represent()

    @property
    def describtion(self):
        """
        Returns the describtion of this API
        """
        try:
            return "%s:\n%s" % (self.get_class_name(),"\n\t".join([self.__doc__]+list(map(lambda x: "\n\t\t".join(["API-method [%s]" % x,"\n\t\t\t".join(self.get_method_describtion(x).split("\n")).lstrip()]),self.method_names))))
        except TypeError:
            return self.__doc__

    def get_class_name(self):
        """
        Returns the name of API-class
        """
        return repr(self).split(' ')[0].rpartition('.')[2]

    @property
    def method_names(self):
        """
        Returns the list of external names of the methods
        """
        return self._methods.keys()

    def register_methods(self):
        """
        Pass's throught the internal dict of attributes and
        checks if the attribute is callable and it's name starts with 'method_'.
        If succes, adding this attribute to own dictionary of methods
        """
        for attribute in dir(self):
            # print "Attribute %s " % attribute
            if callable(getattr(self,attribute)) == True:
                # print "callable attribute %s" % attribute
                method_name = attribute
                if method_name.startswith('method_'):
                    self._methods.update(
                        {
                            method_name.split('method_')[1]:
                                {
                                    'runtime': getattr(self,method_name),
                                    'describtion': getattr(getattr(self, method_name),'__doc__')
                                }
                        }
                    )

    def get_method(self,method_name):
        """
        Returns bounded method to instance by name
        """
        self._methods.setdefault(method_name, None)
        return self._methods[method_name]

    def get_method_describtion(self,method_name):
        """
        Returns describtion of method
        """
        return self.get_method(method_name)['describtion']

    def get_method_runtime(self,method_name):
        """
        Returns runtime of method
        """
        return self.get_method(method_name)['runtime']

    def call_method(self,method_name,kwargs):
        """
        Calls method
        """
        return self.get_result_of_method_call(method_name,kwargs)

    def get_result_of_method_call(self,method_name,kwargs):
        """
        Returns the result of called method
        """
        return self.get_method_runtime(method_name)(kwargs)

    def method_dummy(self,kwargs):
        """
        Dummy method that doesn't do anything
        """
        return kwargs

    def method_second_dummy(self,kwargs):
        """
        Second dummy method
        """
        return kwargs

    @classmethod
    def represent(some_class):
        """
        Gives the public name of the class
        """
        raise ValueError("This method must return public class name")


class SynchronizedBaseAPI(BaseAPI):
    pass


class AsynchronizedBaseAPI(BaseAPI):
    def call_method(self,method_name,kwargs):
        """
        Calls method asynchronously
        """
        return None
