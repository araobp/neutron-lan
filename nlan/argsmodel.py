# 2014/5/14
# Command arguments => model conversion
#

import collections

# For unit testing
if __name__ == '__main__':
    import __builtin__
    with open('nlan_env.conf', 'r') as f:
        __builtin__.__dict__['__n__'] = eval(f.read())

def _type(schema, key):

    if 'value' in schema[key]: # dict
        type_ = schema[key]['value']['type']
        enum = None
        if 'enum' in schema[key]['key']:
            enum = schema[key]['key']['enum'][1] # ['set', [key1, key2,...]]
        if type_ == 'string':
            return (dict, str, enum)
        elif type_ == 'integer':
            return (dict, int, enum)
        else:
            return None
    else:
        type_ = schema[key]['key']['type']
        t = None
        if type_ == 'string':
            t = str 
        elif type_ == 'integer':
            t = int
        if 'max' in schema[key]:
            max_ = schema[key]['max']
            if max_ == 'unlimited' or int(max_) > 1: # list
                return (list, t)
            else:
                return (None, t)
        else:
            return (None, t)


def _get_schema(module):
    import __builtin__
    schema = None
    indexes = None
    if '__n__' in __builtin__.__dict__:
        schema = __n__['types'][module]
        indexes = __n__['indexes']
    else:
        import env
        schema = env.TYPES[module]
        indexes = env.INDEXES
    yield schema
    yield indexes




# List up parameters with types
def schema_help(module, list_output=False):

    if module:
        schema, indexes = _get_schema(module)
        help_ = [] 

        if module in indexes:
            key = indexes[module]
            help_.append("- Use '{}' as _index".format(key))
            help_.append(' _index={}'.format(str(_type(schema,key)[1]))) 
        for key in schema:
            t = _type(schema, key)
            if t[0]:
                if t[0] == list:
                    help_.append('- {}'.format(schema[key]['_description']))
                    help_.append(' {0}={1},{1},...'.format(key,str(t[1])))
                elif t[0] == dict:
                    type_ = str(t[1])
                    line = ""
                    if len(t) == 3:
                        l = []
                        for k in t[2]: # enum
                            l.append('{}:{}'.format(k, type_))
                        line=','.join(l)
                    else:
                        line='param1:{},parm2:{},...'.format(type_)
                    help_.append('- {}'.format(schema[key]['_description']))
                    help_.append(' {0}={1}'.format(key,line))
            else:
                help_.append('- {}'.format(schema[key]['_description']))
                help_.append(' {0}={1}'.format(key,str(t[1])))

        if list_output:
            return help_
        else:
            return '\n'.join(help_)
    else:
        import __builtin__
        tables = None
        if '__n__' in __builtin__.__dict__:
            tables = __n__['tables']
            modules = tables.keys()
        else:
            import env
            modules = env.TABLES.keys()
        if list_output:
            return modules
        else:
            return '\n'.join(modules)


# Converts command arguments into a model
def parse_args(operation, module, *args):
    
    schema, indexes = _get_schema(module)

    model = collections.OrderedDict() 
    submodel = {} 
    index = None
    if operation == 'get' or operation == 'delete':
        for s in args:
            ss = s.split('=')
            k = ss[0]
            v = None
            if k == '_index':
                key = indexes[module] 
                value = ss[1]
                index = [key, _type(schema, key)[1](value)]
            else:
                submodel[k] = v 
    else: # add/update
        for s in args:
            ss = s.split('=')
            k = ss[0]
            v = ss[1]
            if k == '_index':
                key = indexes[module] 
                value = ss[1]
                index = [key, _type(schema, key)[1](value)]
            else:
                t = _type(schema, k)
                
                if t[0] == None:
                    value = t[1](v)
                    submodel[k] = value
                elif t[0] == dict:
                    value = {}
                    for item in v.split(','):
                        pair = item.split(':')
                        value[pair[0]] = t[1](pair[1])
                    submodel[k] = value
                elif t[0] == list:
                    value = []
                    for item in v.split(','):
                        value.append(t[1](item))
                    submodel[k] = value

    if index:
        submodel['_index'] = index
        model[module] = [submodel]
    else:
        model[module] = submodel

    return model

if __name__=='__main__':

    args = ('_index=vni,101', 'vni=101', 'vid=1', 'peers=192.168.0.1,192.168.0.2', 'ip_dvr=addr:10.0.1.1/24,mode:dvr')

    print parse_args('add', 'subnets', *args)

    args = ('ovs_bridges=enabled',)

    print parse_args('add', 'bridges', *args)

    print schema_help('subnets')

    print module_help()
