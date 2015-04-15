#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

import json

import urllib
import urllib2

###########################################################################
# This module connects to external service-manager and explores it's API's
###########################################################################

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


class Explorer(object):
    def __init__(self,host,port=8080):
        self.api_url = 'http://'+host+':'+str(port)
        services_list = self.make_request('/list/services')
        self.services = APIObject()
        for service_name in services_list:
            self.services.setdefault(service_name,APIObject())
            service_classes = self.make_request('/list/'+service_name)
            for class_ in service_classes:
                self.services[service_name].setdefault(class_,APIObject())
                class_methods = self.make_request('/list/'+service_name+'/'+class_)
                for class_method in class_methods:
                    api_method_object = APIMethodObject()
                    api_method_object.set_callback(self.decorate_call(service_name,class_,class_method))
                    self.services[service_name][class_].setdefault(class_method,api_method_object)
        # print self.services

    def make_request(self,path,params=None):
        if params is None:
            return json.loads(
                urllib2.urlopen(
                    self.api_url+path
                ).read()
            )
        else:
            data = urllib2.urlopen(
                        self.api_url+path+'?'+urllib.urlencode(params)
            ).read()
            try:
                return json.loads(data)
            except ValueError:
                return data

    def call_method_by_path(self,path,params):
        service_name,class_name,method_name = path.split('/')

        api_method_object = self.services[service_name][class_name][method_name]
        # print api_method_object
        # print dir(api_method_object)
        # print api_method_object.__call__
        # return api_method_object.__call__(params)

        return api_method_object(**params)

    def decorate_call(self,s_n,c_n,m_n):
        path = '/api/'+"/".join((s_n,c_n,m_n))
        def wrapper(**kwargs):
            return self.make_request(path,kwargs)
        return wrapper


if __name__ == "__main__":
    host,port,path, params = sys.argv[1:5]

    print host,port,path,params
    meth_params = dict()
    for param_pare in params.split('&'):
        key,dummy,value = param_pare.partition('=')
        meth_params.update({key:value})

    print params

    explorer = Explorer(host,port)

    print explorer.call_method_by_path(path, meth_params)

    print explorer.services.service_google.GOOGLE_CACHE.echo(message='2')




