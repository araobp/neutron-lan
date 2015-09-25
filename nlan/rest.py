#!/usr/bin/env python
#
# 2014/5/19
#
# NLAN REST APIs based on WSGI 
#

import os, sys, urlparse
from wsgiref import util, simple_server
from cStringIO import StringIO
import traceback
import json

import nlan, argsmodel
from errors import NlanException

# wsgiref's HTTP server does reverse DNS lookup for every HTTP request,
# and every HTTP transaction takes longer than 10 seconds.
# The following lines are monkeypatch to disable reverse DNS lookup.
# (reference): http://zqfan.github.io/openstack/2014/03/12/disable-reverse-dns-query-for-ceilometer-api/
bhs = __import__('BaseHTTPServer')
bhs.BaseHTTPRequestHandler.address_string = lambda x: x.client_address[0]
        

class RestApi(object):
    
    def __init__(self):
        pass 
        
    def __call__(self, environ, start_response):
       
        # Request method
        method = environ['REQUEST_METHOD']

        # /// URLs ///
        # /<router>/config/<module>/<_index>
        # /<router>/rpc/<module>/<func>
        path = environ['PATH_INFO'].split('/')
        router = None
        module_type = None # 'config' or 'rpc'
        module = None # name of a config module or a rpc module
        _index = None
        module_func = None
        if len(path) > 1:
            router = path[1]
        if len(path) > 2:
            module_type = path[2]
        if len(path) > 3:
            module = path[3]
        if len(path) > 4:
            if module_type == 'config': # Calls a config module
                _index = path[4]
            elif module_type == 'rpc': # Calls a rpc module
                module_func = '{}.{}'.format(module,path[4])
       
        # /// Methods ///
        # Method    NLAN operation
        # ------------------------
        # POST      --add or none(rpc) 
        # PUT       --update
        # DELETE    --delete
        # GET       --get
        # OPTIONS   --schema
        # /// Query parameters ///
        # -------------------------------------------------------
        # For POST(config)/PUT
        # Query parameters correspond to those --schema outputs
        # (excluding "_index").
        # -------------------------------------------------------
        # For POST(rpc)/DELETE/GET
        # args=<value1>,<value2>,...
        # -------------------------------------------------------
        # For OPTIONS
        # args=<module_name>
        # -------------------------------------------------------
        operations = {'POST': '--add',
                      'PUT': '--update',
                      'DELETE': '--delete',
                      'GET': '--get'}
        doc = None
        query = environ['QUERY_STRING'] 
        if method == 'POST' and module_type == 'config' or method == 'PUT': # add/update
            q = query.split('&')
            if _index:
                q.append('_index={}'.format(_index))
            doc = str(argsmodel.parse_args('add', module, *q))
        elif method == 'DELETE' or method == 'GET': # delete/get
            qq = query.split('=') 
            q = [] 
            if qq[0] == 'params':
                q = qq[1].split(',')
            if _index:
                q.append('_index={}'.format(_index))
            doc = str(argsmodel.parse_args('get', module, *q))
        elif method == 'POST' and module_type == 'rpc':
            doc = [] 
            doc.append(module_func)
            q = query.split('=') 
            if q[0] == 'params':
                doc.extend(q[1].split(','))
        elif method == 'OPTIONS': # schema
            if query: 
                qq = query.split('=')
                module = qq[1]

        # String buffer as a HTTP Response body
        out = StringIO()

        try:
            if method in operations and module_type == 'config': 
                operation = operations[method]
                results = nlan.main(router=router, operation=operation, doc=doc, output_stdout=True, rest_output=True)
                print >>out, json.dumps(results)
                start_response('200 OK', [('Content-type', 'application/json')])
            elif method == 'POST' and module_type == 'rpc':
                results = nlan.main(router=router, doc=doc, output_stdout=True, rest_output=True)
                print >>out, json.dumps(results)
                start_response('200 OK', [('Content-type', 'application/json')])
            elif method == 'OPTIONS':
                print >>out, argsmodel.schema_help(module, list_output=True)
                start_response('200 OK', [('Content-type', 'application/json')])
            else:
                print >>out, 'Not Implemented'
                start_response('501 Not Implemented', [('Content-type', 'text/plain')])
        except NlanException as e:
            results = e.get_result()
            print >>out, json.dumps(results)
            start_response('500 Internal Server Error', [('Content-type', 'application/json')])
        except Exception as e:
            print >>out, traceback.format_exc()
            start_response('500 Internal Server Error', [('Content-type', 'application/json')])

        # Return the result as a body of HTTP Response
        out.seek(0)
        return out 
       

if __name__ == '__main__':

    host_ip = '0.0.0.0'
    port = 8080
    appl = RestApi()
        
    try:
        print 'NLAN REST API server stareted, http://{}:{}'.format(host_ip,port)
        srv = simple_server.make_server(host_ip, port, appl)
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
    
