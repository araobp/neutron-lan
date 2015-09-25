#!/usr/bin/env python

import os, sys, time, copy, string, random 
from optparse import OptionParser
from collections import OrderedDict
import logging
import cStringIO
import traceback

from cmdutil import CmdError
from errors import ModelError
import argsmodel 

ENVFILE = '/opt/nlan/nlan_env.conf'

random = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
multipart_boundary = '--'+random
stdout = cStringIO.StringIO()
sys.stdout.write("MIME-Version: 1.0\n")
sys.stdout.write('Content-Type: multipart/mixed;boundary="{}"\n\n'.format(random))
sys.stdout.write("{0}\nContent-Type: test/plain\nContent-Description: Default out\nX-NLAN-Type: default_out\n\n".format(multipart_boundary)) # data output to STDOUT and STDERR
sys.stdout.flush() # This is necessary due to sys.stdout buffering.

# MIME Multipart message
def mime_multipart(body, content_type='text/plain', content_description=None, x_nlan_type=None):

    if body:
        body = str(body)
    else:
        body = ''
        
    if content_description and x_nlan_type:
        stdout.write("{0}\nContent-Type: {1}\nContent-Description: {2}\nX-NLAN-Type: {3}\n\n{4}\n".format(multipart_boundary, content_type, content_description, x_nlan_type, body))
    elif content_description:
        stdout.write("{0}\nContent-Type: {1}\nContent-Description: {2}\n\n{3}\n".format(multipart_boundary, content_type, content_description, body))
    elif x_nlan_type:
        stdout.write("{0}\nContent-Type: {1}\nX-NLAN-Type: {2}\n\n{3}\n".format(multipart_boundary, content_type, x_nlan_type, body))
    else:
        stdout.write("{0}\nContent-Type: {1}\n\n{2}\n".format(multipart_boundary, content_type, body))


def _init(envfile=ENVFILE, loglevel=logging.WARNING):

    # Environment setting
    with open(envfile, 'r') as envfile:
        import __builtin__
        __builtin__.__dict__['__n__'] = eval(envfile.read())

    # Logger setting
    logger2 = logging.getLogger("nlan_agent")
    logger2.setLevel(loglevel)
    #handler = logging.StreamHandler(sys.stdout)
    handler = logging.StreamHandler(stdout)
    #handler2 = logging.FileHandler('/tmp/nlan_agent.log')
    handler.setLevel(loglevel)
    #handler2.setLevel(loglevel)
    header = "{}\nContent-Type: %(content_type)s\nContent-Description: [%(levelname)s] %(asctime)s module:%(module)s,function:%(funcName)s,router:{}\nX-NLAN-Type: logger\n\n".format(multipart_boundary, __n__['router'])
    formatter = logging.Formatter(header+"%(message)s")
    handler.setFormatter(formatter)
    #handler2.setFormatter(formatter)
    logger2.addHandler(handler)
    #logger.addHandler(handler2)
    __n__['logger2'] = logger2
    extra = {'content_type': 'text/plain'}
    logger = logging.LoggerAdapter(logger2, extra)
    __n__['logger'] = logger

    __n__['logger'].info('NLAN Agent initialization completed')
    __n__['logger'].debug('__n__: {}'.format(__n__))

# Progress of CRUD requests 
def _progress(data, func, _index):
    progress = OrderedDict()
    modules = data.keys()
    hereafter = False
    if func == None:
        hereafter = True
    for mod in modules:
        if mod in __n__['indexes']:
            progress[mod] = {}
            for l in data[mod]:
                idx = l['_index']
                if hereafter:
                    progress[mod][tuple(idx)] = False
                elif mod == func and idx == _index:
                    progress[mod][tuple(idx)] = False
                    hereafter = True
                else:
                    progress[mod][tuple(idx)] = True
        else:
            if hereafter:
                progress[mod] = False
            elif mod == func:
                progress[mod] = False
                hereafter = True 
            else:
                progress[mod] = True

    result = []
    for k,v in progress.iteritems():
        result.append((k,v))

    return result 

# Routing a request to a module
def _route(operation, data):
    
    exit = 0

    if operation in ('add', 'update', 'delete', 'get'): 
        # Calls config modules 
        from oputil import CRUD 
        if __n__['init'] != 'start':
            if isinstance(data, str) and (data.startswith('OrderedDict') or data.startswith('{')):
                data = eval(data)
        _data = copy.deepcopy(data)
        error = None 
        module = None
        _index = None
        try:
            # Model integrity check before the CRUD operation
            if operation != 'get':
                import patterns
                for mod, model in data.iteritems():
                    if mod in __n__['indexes']:
                        for _model in model:
                            (b, m) = patterns.check_model(operation, mod, _model)
                            if not b:
                                __n__['logger'].info("Model integrity check failure")
                                raise ModelError(message=m, model=_model)
                    else:
                        (b, m) = patterns.check_model(operation, mod, model)
                        if not b:
                            __n__['logger'].info("Model integrity check failure")
                            raise ModelError(message=m, model=model)
            # CRUD operation starts from here
            for module, model in data.iteritems():
                if operation == 'get': # CRUD get operation
                    import ovsdb
                    __n__['logger'].info('function:{0}.{1}, model:{2}'.format(module, operation, str(model)))
                    result = ovsdb.get_state(module, model)  
                    mime_multipart(result, content_type='application/x-nlan', content_description='CRUD get', x_nlan_type='crud_response')
                else: # CRUD add/update/delete operation
                    _mod = __import__('config.'+module, globals(), locals(), [operation], -1)
                    call = _mod.__dict__[operation]
                    if module in __n__['indexes']:
                        for _model in model:
                            _index = _model['_index']
                            del _model['_index']
                            __n__['logger'].info('function:{0}.{1}, index:{3}, model:{2}'.format(module, operation, str(_model), str(_index)))
                            # Routes a requested model to a config module ###
                            with CRUD(operation, module, _model, _index, gl = _mod.__dict__):
                                call()
                    else:
                        __n__['logger'].info('function:{0}.{1}, model:{2}'.format(module, operation, str(model)))
                        # Routes a requested model to a config module ###
                        with CRUD(operation, module, model, gl = _mod.__dict__):
                            call()
        except CmdError as e:
            exit = 1
            error = OrderedDict()
            error['exception'] = 'CmdError'
            error['message'] = e.message
            error['traceback'] = traceback.format_exc() 
            error['command'] = e.command
            error['stdout'] = e.out
            error['exit'] = e.returncode 
            error['operation'] = operation
            if operation != 'get':
                error['progress'] = _progress(_data, module, _index)
            __n__['logger'].debug(str(error))
        except ModelError as e:
            exit = 1
            error = OrderedDict()
            error['exception'] = 'ModelError'
            error['message'] = e.message
            error['traceback'] = traceback.format_exc() 
            error['exit'] = 1
            error['operation'] = operation
            if operation != 'get':
                error['progress'] = _progress(_data, module, _index)
            __n__['logger'].debug(str(error))
        except Exception as e:
            exit = 1
            error = OrderedDict()
            error['exception'] = type(e).__name__ 
            error['message'] = 'See the traceback message'
            error['traceback'] = traceback.format_exc() 
            error['exit'] = 1
            error['operation'] = operation
            if operation != 'get':
                error['progress'] = _progress(_data, module, _index)
            __n__['logger'].debug(str(error))
        finally:
            if error:
                mime_multipart(error, content_type='application/x-nlan', content_description='NLAN Response', x_nlan_type='nlan_response')
            else:
                if __n__['init'] != 'start':
                    completed = OrderedDict()
                    completed['message'] = 'Execution completed'
                    completed['exit'] = 0
                    mime_multipart(completed, content_type='application/x-nlan', content_description='NLAN Response', x_nlan_type='nlan_response')
    elif operation in ('rpc_dict', 'rpc_args'):        
        # Calls a rpc module
        rpc = None
        func = None
        args = None
        kwargs = {} 
        error = None 
        if operation == 'rpc_args':
            s = data[0].split('.')
            rpc = '.'.join(s[:-1])
            func = s[-1]
            args = tuple(data[1:])
        elif operation == 'rpc_dict':
            try:
                d = eval(data)
                if isinstance(d, OrderedDict):
                    rpc = d['module']
                    func = d['func']
                    args = d['args']
                    kwargs = d['kwargs']
                else:
                    raise Exception
            except:
                raise Exception("Illegal RPC request: {}".format(data))
        try:
            _mod = __import__('rpc.'+rpc, globals(), locals(), [func], -1)
            call = _mod.__dict__[func]
            __n__['logger'].info('function:{0}.{1}, args:{2}, kwargs:{3}'.format(rpc, func, str(args), str(kwargs)))
            result = call(*args, **kwargs)
            if result:
                mime_multipart(result, content_type='application/x-nlan', content_description='RPC Response', x_nlan_type='rpc_response')
        except CmdError as e:
            exit = 1
            error = OrderedDict()
            error['exception'] = 'CmdError'
            error['message'] = e.message
            error['command'] = e.command
            error['stdout'] = e.out
            error['exit'] = e.returncode 
        except Exception as e:
            exit = 1
            error = OrderedDict()
            error['exception'] = 'Exception'
            error['message'] = 'See the traceback message'
            error['exit'] = 1
            error['traceback'] = traceback.format_exc() 
        finally:
            if error:
                mime_multipart(error, content_type='application/x-nlan', content_description='NLAN Response', x_nlan_type='nlan_response')
            else:
                completed = OrderedDict()
                completed['message'] = 'Execution completed'
                completed['exit'] = 0
                mime_multipart(completed, content_type='application/x-nlan', content_description='NLAN Response', x_nlan_type='nlan_response')
    else:
        error = OrderedDict()
        error['exception'] = 'NlanException'
        error['message'] = 'Unsupported NLAN operation, {}'.format(operation) 
        error['exit'] = 1 
        mime_multipart(error, content_type='application/x-nlan', content_description='NLAN Response', x_nlan_type='nlan_response')

    return exit 


def _linux_init():

    import ovsdb 
    state = ovsdb.get_current_state()
    __n__['logger'].debug("Linux init, current_state: " + str(state))
    exit = 0

    for module in __n__['state_order']:

        model = None

        if module in __n__['indexes'] and module in state:
            ind_key = __n__['indexes'][module]
            for d in state[module]: # dict in the list
                d['_index'] = [ind_key, d[ind_key]] # Adds _index
            model = {module: state[module]}
        elif module in state:
            model = {module: state[module]}

        if model:
            __n__['logger'].info("Linux init, model: " + str(model))
            exit = _route('add', model) 
            if exit > 0:
                return exit

    return exit


if __name__ == "__main__":

    import sys

    logo = """
       _  ____   ___   _  __
      / |/ / /  / _ | / |/ /
     /    / /__/ __ |/    /
    /_/|_/____/_/ |_/_/|_/ AGENT

    """

    usage = logo + "usage: %prog [options] [arg]..."
    
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--add", help="(CRUD) add NLAN states", action="store_true", default=False)
    parser.add_option("-g", "--get", help="(CRUD) get NLAN states", action="store_true", default=False)
    parser.add_option("-u", "--update", help="(CRUD) update NLAN stateus", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="(CRUD) delete NLAN states", action="store_true", default=False)
    parser.add_option("-s", "--schema", help="(CRUD) print schema", action="store_true", default=False)
    parser.add_option("-r", "--rpc", help="RPC w/ args from stdin", action="store_true", default=False)
    parser.add_option("-I", "--info", help="set log level to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set log level to DEBUG", action="store_true", default=False)
    parser.add_option("-f", "--envfile", help="NLAN Agent environment file", action="store", type="string", dest="filename")
    parser.add_option("-i", "--init", help="Linux init script", action="store", type="string", dest="init_action")

    (options, args) = parser.parse_args()

    operation = None 
      
    if options.add:
        operation = 'add'
    elif options.get:
        operation = 'get'
    elif options.update:
        operation = 'update'
    elif options.delete:
	operation = 'delete'	
    elif options.rpc:
        operation = 'rpc_dict'

    loglevel = logging.WARNING
    if options.info:
        loglevel = logging.INFO
    elif options.debug:
        loglevel = logging.DEBUG

    if options.filename:
        _init(options.filename, loglevel=loglevel)
    else:
        _init(loglevel=loglevel)

    if options.schema:
        if len(args) == 1:
            print argsmodel.schema_help(args[0])
        else:
            print argsmodel.schema_help(None)
        sys.exit(0)
	
    data = None 
    if operation and len(args) == 0:
        # Obtains data from nlan.py via SSH
        data = sys.stdin.read().replace('"','') 
    elif operation and len(args) > 0:
        # Obtains data from command arguments
        data = argsmodel.parse_args(operation, args[0], *args[1:])
    else: # RPC w/ command arguments
        data = args
        operation = 'rpc_args'

    exit = 0
    if options.init_action:
        __n__['init'] = options.init_action
        exit = _linux_init()
    else:
        __n__['init'] = False
        exit = _route(operation=operation, data=data)

    __n__['logger'].info('NLAN Agent execution completed')
    stdout.seek(0)
    sys.stdout.write(stdout.read())
    sys.stdout.write('--'+random+'--\n')
    sys.stdout.flush()
    stdout.close()
    sys.exit(exit)

