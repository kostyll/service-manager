#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from abc import abstractmethod
from collections import namedtuple
import json

import bottle

import service_api

import services

class ServiceManager(object):
    def __init__(self):
        self._registered_services = {}

        for service in services.__all__:
            self._registered_services.update({service:getattr(services,service)})
            print "Registered service %s" % service
    @property
    def registered_services(self):
        return self._registered_services.keys()

    def get_service(self,service_name):
        return self._registered_services.get(service_name,None)

    def enumerate_service_classes(self,service_name):
        return self.get_service(service_name).register()

    def get_service_class(self,service,class_name):
        return getattr(service, class_name)

    def get_service_class_by_name(self,service_name,class_name):
        return self.get_service_class(self.get_service(service_name), class_name)


class ServiceRunner(object):
    def __init__(self,service_manager):
        self.service_manager = service_manager
        self.service_instances = {}
        self.request_paths = {}
        # self.methods_handlers = {}
        self.method_handler = None
        self.api_docs = {}
        self.build_instances()
        self.set_method_handler_builder()
        self.build_runner()

    @abstractmethod
    def build_runner(self):
        """
        Generates requests handlers for service
        """

    @abstractmethod
    def run_service(self,*args,**kwargs):
        """
        Starts up the service
        """

    @abstractmethod
    def set_method_handler_builder(self):
        """
        Builds method args getter
        """

    def build_instances(self):
        for service in self.service_manager.registered_services:
            for service_class in self.service_manager.enumerate_service_classes(service):
                print service,service_class
                path_key,instance = self.get_service_instance(service, service_class)
                print instance

                class_describtion = instance.describtion

                # self.api_docs.update({path_key:{'class':class_describtion,'methods':[]}})
                self.api_docs.update({path_key:class_describtion})

                for method_name in instance.method_names:
                    method_params = instance.get_method_params(method_name)
                    method_describtion = instance.get_method_describtion(method_name)
                    method_runtime = instance.get_method_runtime(method_name)

                    # self.api_docs.update({"/".join((path_key,method_name)):})

                    path = path_key + '/' + method_name

                    self.request_paths.update(
                        {
                            path:{
                                'runtime':method_runtime,
                                'describtion':method_describtion,
                                'params':method_params
                            }
                        }
                    )

    def split_service_class(self,service_name,class_):
        return service_name+'/'+class_.represent()

    def get_service_instance(self,service_name,class_):
        key = self.split_service_class(service_name, class_)
        service_instance = self.service_instances.get(key,None)
        if service_instance is None:
            service_instance = self.service_manager.get_service_class_by_name(service_name,class_.represent())()
            self.service_instances.update({key:service_instance})
        return key,service_instance

    @abstractmethod
    def run(self):
        """
        Runs the current service
        """


class WebRunner(ServiceRunner):
    pass


class BottleRunner(WebRunner):
    def build_runner(self):
        self.RH = bottle.Bottle()

        ############ MAKING METHOD HTTP-HANDLERS #############

        def runtime_decorator(request_method_info):
            def wrapper():
                request_params = dict(bottle.request.params)
                print "Got params %s, req_method_info = %s " % (request_params,request_method_info)
                result = request_method_info['runtime'](request_params)
                print "Result = %s" % result
                return result
            return wrapper

        def params_decorator(request_method_info):
            def wrapper():
                return request_method_info['params']
            return wrapper

        def describtion_decorator(request_method_info):
            def wrapper():
                return request_method_info['describtion']
            return wrapper

        for request_path,request_method_info in self.request_paths.items():

            print "Building route of %s" % request_path
            # self.RH.route(request_path)(wrapper)
            self.RH.get('/api/'+request_path)(runtime_decorator(request_method_info))
            self.RH.get('/docs/'+request_path)(describtion_decorator(request_method_info))
            self.RH.get('/params/'+request_path)(params_decorator(request_method_info))

        def show_registered_services():
            return  json.dumps(self.service_manager.registered_services)

        self.RH.get('/list/services')(show_registered_services)

        def class_describtion_decorator(registered_service,class_):
            def wrapper():
                return self.service_manager.get_service_class_by_name(registered_service,class_)().describtion
            return wrapper

        def classes_list_decorator(classes):
            def wrapper():
                return json.dumps(classes)
            return wrapper

        def class_methods_list_decorator(registered_service,class_):
            def wrapper():
                return json.dumps(service_manager.get_service_class_by_name(registered_service,class_)().method_names)
            return wrapper

        for registered_service in self.service_manager.registered_services:
            classes = map(lambda x: x.represent(),self.service_manager.enumerate_service_classes(registered_service))

            service_classes_path = '/list/'+registered_service

            print "Building classes list  %s" % service_classes_path

            self.RH.get(service_classes_path)(classes_list_decorator(classes))

            for class_ in classes:

                class_help_path = '/docs/'+registered_service+'/'+class_
                class_methods_list = '/list/'+registered_service+'/'+class_

                print "Building class help path %s" % class_help_path

                self.RH.get(class_help_path)(class_describtion_decorator(registered_service,class_))

                print "Building class methods list path %s" % class_methods_list

                self.RH.get(class_methods_list)(class_methods_list_decorator(registered_service,class_))


        ############ MAKING METHOD HTTP-DOCS #############

    def run(self):
        bottle.run(self.RH)


class ConsoleRunner(ServiceRunner):
    def build_runner(self):

        import argparse

        parser = argparse.ArgumentParser()

        parser.add_argument(
            'action',
            choices=[
                'lssrv', # show list of services
                'lscls', # show list of selected service classes
                'lsmth', # show list of selected class methods
                'pmth', # parameters of the selected methods
                'dcls', # show docs of selected class
                'dmth', # show docs of selected method
                'call', # call selected method
                'paths', # show all paths
            ],
            help="""
            lssrv - show list of services;
            lscls - show list of selected service classes;
            lsmth - show list of selected class methods;
            pmth - parameters of the selected methods;
            dcls - show docs of selected class;
            dmth - show docs of selected method;
            call - call selected method;
            paths - show all paths
            """
        )

        parser.add_argument(
            'path',
            action='store',
            help='path to service/class/method',
            default=""
        )

        parser.add_argument(
            '-p,--params',
            dest="params_query",
            action='store',
            help='params for calling API methods',
            default=""
        )

        self.parser = parser

    def show_services(self,arguments):
        for registered_service in self.service_manager.registered_services:
            print registered_service

    def show_service_classes(self,arguments):
        classes = map(lambda x: x.represent(),self.service_manager.enumerate_service_classes(arguments.path))
        for class_ in classes:
            print class_

    def show_class_methods(self,arguments):
        service,class_ = arguments.path.split('/')
        method_names = self.service_manager.get_service_class_by_name(service,class_)().method_names
        for method_name in method_names:
            print method_name

    def show_class_doc(self,arguments):
        service_name,class_name = arguments.path.split('/')

        class_ = self.service_manager.get_service_class_by_name(service_name,class_name)

        print class_().describtion

    def show_method_describtion(self,arguments):
        service_name,class_name,method_name = arguments.path.split('/')

        class_ = self.service_manager.get_service_class_by_name(service_name,class_name)

        print class_().get_method_describtion(method_name)

    def show_method_params(self,arguments):
        service_name,class_name,method_name = arguments.path.split('/')

        class_ = self.service_manager.get_service_class_by_name(service_name,class_name)

        params =  class_().get_method_params(method_name)

        for key in params.keys():
            print "%s: %s" % (key,params[key])

    def call_method(self,arguments):

        params = {}
        for param_pare in arguments.params_query.split("&"):
            key,dummy,value = param_pare.partition('=')
            params.update({key:value})

        print self.request_paths[arguments.path]['runtime'](params)

    def show_all_request_paths(self,arguments):
        for path in self.request_paths.keys():
            print path

    def run(self):
        console_arguments = sys.argv[2:]
        # print console_arguments
        args = self.parser.parse_args(console_arguments)
        print args

        commands_map = {
            'lssrv':self.show_services,
            'lscls':self.show_service_classes,
            'lsmth':self.show_class_methods,
            'pmth':self.show_method_params,
            'dcls':self.show_class_doc,
            'dmth':self.show_method_describtion,
            'call':self.call_method,
            'paths':self.show_all_request_paths,
        }

        commands_map[args.action](args)


if __name__ == "__main__":

    service_manager = ServiceManager()

    # print "Registered services:"

    # try:

    if sys.argv[1] == "web":

        runner = BottleRunner(service_manager)
        # bottle.run(bottle_runner.RH)
        runner.run()
        sys.exit(0)
    elif sys.argv[1] == "console":
        runner = ConsoleRunner(service_manager)
        runner.run()
        sys.exit(0)
    # except:
    for registered_service in service_manager.registered_services:
        print "Service: %s" % registered_service

        classes = map(lambda x: x.represent(),service_manager.enumerate_service_classes(registered_service))
        print "Classes: %s" % classes

        for class_ in classes:
          describtion = service_manager.get_service_class_by_name(registered_service,class_)().describtion

          print describtion




