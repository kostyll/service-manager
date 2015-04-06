#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

import service_api

import services

class ServiceManager(object):
    def __init__(self):
        self.registered_services = {}

        for service in services.__all__:
            self.registered_services.update({service:getattr(services,service)})
            print "Registered service %s" % service

    def get_service(self,service_name):
        return self.registered_services.get(service_name,None)

    def enumerate_service_classes(self,service_name):
        return self.get_service(service_name).register()

    def get_service_class(self,service,class_name):
        return getattr(service, class_name)

    def get_service_class_by_name(self,service_name,class_name):
        return self.get_service_class(self.get_service(service_name), class_name)


if __name__ == "__main__":

    service_manager = ServiceManager()

    print "Registered services:"

    for registered_service in service_manager.registered_services.keys():
        print "Service: %s" % registered_service

        classes = map(lambda x: x.represent(),service_manager.enumerate_service_classes(registered_service))
        print "Classes: %s" % classes

        for class_ in classes:
          describtion = service_manager.get_service_class_by_name(registered_service,class_)().describtion

          print describtion



