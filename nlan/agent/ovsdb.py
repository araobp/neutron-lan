"""
2014/3/18, 3/31

OVSDB client libraries for neutron-lan

Reference: http://tools.ietf.org/rfc/rfc7047.txt 

"""

import random
from collections import OrderedDict

DATABASE = 'Open_vSwitch'
PARENT = 'NLAN'

# For unit testing
if __name__ == '__main__':
    import __builtin__
    import nlan_agent
    with open('nlan_env.conf', 'r') as f:
        __builtin__.__dict__['__n__'] = eval(f.read())
    nlan_agent.setlogger(__n__)
    __n__['init'] = 'xxx'

TABLES = __n__['tables']

def _index():
    return random.randint(0, 999999)

# OpenWRT's python-mini does not include the UUID package.
def _uuid_name():
    return 'temp_' + str(random.randint(0, 999999))

# Get a value of row "_uuid" in the response
# Limitation: This can get only the first row in the table
def get_uuid(response):
    return response["result"][0]["rows"][0]["_uuid"][1]

# OVSDB returns a non-list value under the following condition:
# - either min or max is not 1 => supposed to be a list of values.
# - it has only one member in the list.
# NLAN assumes that a value with 'max' greater than 1 is a list
# even if it has only one member in the list.
def _iflist(module, param):
    iflist = False
    if module:
        if 'value' not in __n__['types'][module][param]: # if it is a map?
            if 'max' in __n__['types'][module][param]:
                max_ = __n__['types'][module][param]['max']
                if isinstance(max_, int):
                    if max_ > 1:
                        iflist = True
                elif isinstance(max_, str):
                    if max_ == 'unlimited':
                        iflist = True
    return iflist

def _iflist_tables(module):
    iflist = False
    try:
        maxparam = __n__['tables'][module]['max']
        if isinstance(maxparam, int):
            if int(maxparam) > 1:
                iflist = True
        elif isinstance(maxparam, str):
            if maxparam == 'unlimited':
                iflist = True
    except:
        pass
    return iflist

# Get a row in the form of Python dictionary 
def _todict(row, module=None):

    dict_value = {} 

    for key in row.keys():
        if key != '_uuid' and key != '_version':
            value = row[key]
            if isinstance(value, list):
                v = value[1]
                if isinstance(v, list) and value[0] == 'set':
                    if len(v) > 0:
                        dict_value[key] = v
                    else:
                        pass
                if isinstance(v, list) and value[0] == 'map':
                    if len(v) > 0:
                        d = {} 
                        for l in v:
                            d[l[0]] = l[1]
                        dict_value[key] = d
                    else:
                        pass
                elif not(isinstance(v, list)) and value[0] == 'uuid':
                    dict_value[key] = v
            else: 
                if _iflist(module, key):
                    dict_value[key] = [row[key]]
                else:
                    dict_value[key] = row[key]
    if dict_value:
        return dict_value
    else:
        return None

# Get a row in the form of Python dictionary 
def todict(response, module=None):
    rows = response["result"][0]["rows"]
    if isinstance(rows, list) and len(rows) == 0: # Empty list
        return None 
    else:
        row = rows[0]
        dict_ = _todict(row, module)
        return dict_

# Get rows in the form of Python dictionary 
def todicts(response, module=None):
    dicts = [] 
    rows = response["result"][0]["rows"]
    for row in rows:
        if isinstance(row, dict) and not row: # Empty dict
            pass 
        else:
            d = _todict(row, module)
            if d:
                dicts.append(d)
    if len(dicts) == 0:
        return None
    else:
        return dicts

            
# Get a value of count in the JSON-RPC response
def get_count(response):

    count = 0
    result = response["result"]
    for l in result:
        if 'count' in l:
            count = l['count']
    return count 

# Converts a Python list/dict object into set/map
# as defined in RFC7047.
def _row(model):

    model_row = {}
    for key in model.keys():
        v = model[key]
        if isinstance(v, list):
            v = ["set", v]
        elif isinstance(v, dict):
            l = []
            for kk, vv in v.iteritems():
                l.append([kk, vv])
            v = ["map", l]
        model_row[key] = v
    return model_row

#def _logstr(*args):
#
#    l = list(args)
#    return '\n'.join(l)

# JSON-RPC transaction
def _send(request):

    import socket, json

    dumps = None
    loads = None
    sock = None
    dist = None 

    try:
        dist = __n__['platform']
    except:
        pass 

    if dist == 'openwrt':
        dumps = json.JsonWriter().write
        loads = json.JsonReader().read
        sock = '/var/run/db.sock'
    else:
        dumps = json.dumps
        loads = json.loads
        sock = '/var/run/openvswitch/db.sock'

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock)

    
    pdu = dumps(request)
    s.send(pdu)
    response = s.recv(4096)

    #__n__['logger'].debug(_logstr('... JSON-RPC request ...', str(pdu), '... JSON-RPC response ...', response))
    #transaction = '--json-rpc:{"request":%s, "response":%s}' % (str(pdu),response)
    transaction = '{"request":%s, "response":%s}' % (str(pdu),response)
    __n__['logger2'].debug(transaction, extra={'content_type': 'application/json'})

    return loads(response)

# JSON-RPC Operations as specified in RFC7047 #########################

"""
"op": "insert"              required
"table": <table>            required
"row": <row>                required
"uuid-name": <id>           optional

"""
def insert(table, row):
    
    i = _index()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "insert",
            "table": table,
            "row": row 
        }
        ],
    "id": i 
    }

    return _send(request)


"""
"op": "insert"              required
"table": <table>            required
"row": <row>                required
"uuid-name": <id>           optional

"""
def insert_mutate(table, row, parent_table, parent_column):

    i = _index() 
    uuid_name = _uuid_name()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "insert",
            "table": table,
            "row": row, 
            "uuid-name": uuid_name
        },{
            "op": "mutate",
            "table": parent_table,
            "where": [],
            "mutations": [
                [
                    parent_column,
                    "insert",
                    [
                        "set",
                        [
                            [
                                "named-uuid",
                                uuid_name
                            ]
                        ]
                    ]
                ]
            ]
        }
        ],
    "id": i 
    }

    return _send(request)


"""
"op": "select"              required
"table": <table>            required
"where": [<conditions>*]    required
"columns": [<column>*]      optional

"""
def select(table, where, columns=None):

    i = _index()

    obj = {
        "op": "select",
        "table": table,
        "where": where
        }

    if columns != None:
        obj['columns'] = columns

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        obj
        ],
    "id": i 
    }
    
    return _send(request)


"""
"op": "update"              required
"table": <table>            required
"where": [<conditions>*]    required
"row": <row>                required
"""
def update(table, where, row):

    i = _index()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "update",
            "table": table,
            "where": where,
            "row": row
        }
        ],
    "id": i 
    }
    
    return _send(request)


"""
"op": "delete"              required
"table": <table>            required
"where": [<condition>*]     required

"""
def delete(table, where):

    i = _index() 
    uuid_name = _uuid_name()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "delete",
            "table": table,
            "where": where 
        }
        ],
    "id": i 
    }

    return _send(request)


def mutate_delete(table, where, parent_table, parent_column):

    i = _index() 

    response = select(table, where)
    uuid = get_uuid(response)

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "mutate",
            "table": parent_table,
            "where": [],
            "mutations": [
                [
                    parent_column,
                    "delete",
                    [
                        "set",
                        [
                            [
                                "uuid",
                                uuid
                            ]
                        ]
                    ]
                ]
            ]
        }
        ],
    "id": i 
    }

    return _send(request)

# O/R mapper  ################################################
# This O/R mapper manipulate a raw as described in RFC7047.
# Usage:
# r = Row('Interface', ('name', 'vxlan_102'))
# print r['ofport']
# Limitations:
# Can get only one row (the first row) even if
# multiple rows mactch the index.
class OvsdbRow(object):
   
    # Creates an instance of a row 
    def __init__(self, table, index=None):

        self.table = table 
        self.index = index

        self.where = [] 
        
        if self.index != None:

            column = self.index[0]
            value = self.index[1]

            self.where = [[
                column,
                "==",
                value
                ]]

        response = select(self.table, self.where)
        self.row = todict(response)


    def __setitem__(self, key, value):
        v = value
        if isinstance(v, list):
            v = ["set", v]
        elif isinstance(v, dict):
            l = []
            for kk, vv in v.iteritems():
                l.append([kk,vv])
            v = ["map", l]
        row = {key: v}
        update(self.table, self.where, row)
        self.row[key] = value

    def __getitem__(self, key):
        return self.row[key]

    def __delitem__(self, key):

        """
       (RFC7047)
       The operation inserts "row" into "table".  If "row" does not specify
       values for all the columns in "table", those columns receive default
       values.  The default value for a column depends on its type.  The
       default for a column whose <type> specifies a "min" of 0 is an empty
       set or empty map.  Otherwise, the default is a single value or a
       single key-value pair, whose value(s) depend on its <atomic-type>:

       o  "integer" or "real": 0
       o  "boolean": false
       o  "string": "" (the empty string)
       o  "uuid": 00000000-0000-0000-0000-000000000000 
        
        (RFC7047)
        If "min" and "max" are both 1 and "value" is not specified, the
        type is the scalar type specified by "key".

        If "min" is not 1 or "max" is not 1, or both, and "value" is not
        specified, the type is a set of scalar type "key".

        If "value" is specified, the type is a map from type "key" to type
        "value".
        """
        min_ = 1
        max_ = 1
        type_ = None 
        value_exists = False
        schema =  __n__['types'][self.module][key]
        if 'min' in schema:
            min_ = schema['min']
        if 'max' in schema:
            max_ = schema['max']
        if isinstance(schema['key'], dict):
            type_ = schema['key']['type']
        else:
            type_ = schema['key']
        if 'value' in schema:
            value_exists = True

        default = None 
        set_ = ["set", []]  # Empty set
        map_ = ["map", []]  # Empty map

        if value_exists:  # map
            default = map_
        elif min_ == 1 and max_ == 1:  # Scalar type
            if type_ == 'integer' or type_ == 'real':
                default = 0 
            elif type_ == 'string':
                default = ""
            elif type_ == 'boolean':
                default = False
            else:
                # This case never happens
                pass
        else:  # set
            default = set_ 
        
        update(self.table, self.where, {key: default})
        #self.row[key] = None
        del self.row[key]

    def getrow(self):
        return self.row

    def getparam(self, *args):

        for key in args:
            if key in self.row.keys():
                yield self.row[key]
            else:
                yield None

# O/R mapper for NLAN ################################################
# This O/R mapper manipulate a raw as described in RFC7047.
# Usage:
# r = Row('subnets', ('vni', 1001))
# r.setrow(model)
# r['vid'] = 101
# r['ports'] = ['eth0', 'eth1']
# vid = r['vid']
# d = r.getrow()
# r.delrow()
class Row(OvsdbRow):


    # Creates an instance of a row 
    def __init__(self, module, index=None):

        if not todict(select('NLAN', [])):
            insert('NLAN', {})
        self.module = module

        #self.parent = self.__class__.PARENT
        self.parent = PARENT

        #table = self.__class__.TABLES[module]
        self.table = TABLES[module]['key']['refTable']

        self.index = index
        self.where = [] 
        
        if self.index != None:

            column = self.index[0]
            value = self.index[1]

            self.where = [[
                column,
                "==",
                value
                ]]

        response = select(self.table, self.where)
        self.row = todict(response, self.module)
        
        #super(self.__class__, self).__init__(table, module, index)

    def setrow(self, model):
        row = _row(model)
        response = insert_mutate(self.table, row, self.parent, self.module)
        response = select(self.table, self.where)
        self.row = todict(response, self.module)

    def delrow(self):
        response = mutate_delete(self.table, self.where, self.parent, self.module)
        self.row = {} 

   
    # add/update/delete 
    def crud(self, crud, model):

        if __n__['init'] != 'start':
            
            ind = None
            if self.index:
                ind = self.index[0]
            keys = model.keys()

            __n__['logger'].debug("CRUD operation ({0}): {1}".format(crud,str(model)))

            if ind in keys and crud == 'add':
                self.setrow(model)
            elif not ind and not self.getrow():
                self.setrow(model)
            elif crud == 'add' or crud == 'update':
                for k in keys:
                    self[k] = model[k]
            elif ind in keys and crud == 'delete':
                self.delrow()
            elif crud == 'delete':
                for k in keys:
                    del self[k]
            else:
                raise Exception("Parameter error")

    def add(self, model):
        return self.crud('add', model)

    def update(self, model):
        return self.crud('update', model)
    
    def delete(self, model):
        return self.crud('delete', model)
   
    @classmethod
    def clear(cls):
        #response = delete(cls.PARENT, [])
        response = delete(PARENT, [])

# Searches a table with 'column = value'.
# Returns rows in the form of Python dictionary
def search(table, columns, key=None, value=None):
  
    where = []
    if key and value:
        where = [[
            key,
            "==",
            value
            ]]

    response = select(table, where, columns)
    tables = __n__['tables']
    module = None
    for k, v in tables.iteritems():
        if v['key']['refTable'] == table:
            module = k
            break
    return todicts(response, module)

def nlan_search(module, columns=None, key=None, value=None): 

    where = [] 
    if key and value:
        where = [[
            key,
            "==",
            value
            ]]

    table = __n__['tables'][module]['key']['refTable']
    response = select(table, where, columns)
    return todicts(response, module)
    

# Obtains ofport <=> peers mapping data for vxlan ports
# to construct broadcast trees for each vni
def get_vxlan_ports(peers=None):

    ofports = []
    tablesearch = search('Interface', ['ofport', 'options'], 'type', 'vxlan')
    vxlan_ports = []
    if peers:
        for ip in peers:
            for l in tablesearch:
                if l['options']['remote_ip'] == ip:
                    vxlan_ports.append(str(l['ofport']))
    else:
        for l in tablesearch:
            vxlan_ports.append(str(l['ofport']))

    return vxlan_ports

def get_vxlan_port(peer):

    tablesearch = search('Interface', ['ofport', 'options'], 'type', 'vxlan')

    for l in tablesearch:
        if l['options']['remote_ip'] == peer:
            return l['ofport']

    raise Exception("No ofport found")

def get_current_state():

    state = OrderedDict()

    row = todict(select('NLAN', []))

    if row:
        for key in row:
            v = row[key]
            if _iflist_tables(key):
                if v:
                    d = todicts(select(table=TABLES[key]['key']['refTable'],where=[]),key)   
                    if d:
                        state[key] = d  
                    else:
                        pass
            elif isinstance(v, str) or isinstance(v, unicode):
                d = todict(select(table=TABLES[key]['key']['refTable'],where=[]),key)
                if d:
                    state[key] = d
                else:
                    pass

        return state
    else:
        return None


# CRUD get operation
def get_state(module, model):

    results = OrderedDict() 

    if module in __n__['indexes']: # list type
        l = []
        if model:
            for _model in model:
                _index = _model['_index']
                del _model['_index']
                columns = None
                if len(_model) > 0:
                    columns = []
                    for k in _model:
                        columns.append(k)
                s = nlan_search(module, columns, _index[0], _index[1])
                if s:
                    l.append(s[0])
            if len(l) > 0:
                results[module] = l
        else:
            s = nlan_search(module)
            if s:
                results[module] = s
    else: # non list type
        columns = None 
        if model:
            columns = []
            for k in model:
                columns.append(k)
        s = nlan_search(module, columns, key=None, value=None)
        if s:
            results[module] = s[0]

    if results:
        return results
    else:
        return None



#######################################################################

# Unit test
if __name__=='__main__':

    def _printcount(response):
        c = get_count(response)
        if c == 1:
            print 'SUCCESS, get_count: {}'.format(str(c))
        else:
            print 'FAILURE, get_count: {}'.format(str(c))

    # Clear NLAN tables
    Row.clear()

    where = [[
        "vni",
        "==",
        1001
        ]]

    print "##### Insert test: 'NLAN' table #####"
    response = insert('NLAN', {})

    row = {
        "vid": 101,
        "vni": 1001,
        "ip_dvr": ["map", [["addr","10.0.0.1/24"],["mode","dvr"]]],
        #"ports": ["set", ["eth0", "veth-test"]]
        }
   
    print "##### Insert and Mutate test: 'NLAN_Subnet' table #####"
    response = insert_mutate('NLAN_Subnet', row, 'NLAN', 'subnets')
    _printcount(response)

    print "##### Select test #####" 
    select('NLAN_Subnet', where)
    print "##### Select (search) test #####"
    print search('NLAN_Subnet', ["vni", "ip_dvr"], "vid", 101)

    # This transaction shuld fail, since a row with vni=1001
    # has already been inserted.
    print "##### Insert and Mutate test: 'NLAN_Subnet' table (fails) #####"
    response = insert_mutate('NLAN_Subnet', row, 'NLAN', 'subnets')

    select('NLAN_Subnet', where)

    print "##### Update test #####"
    row = {
            "ip_dvr": ["map",[["addr", "10.0.1.2/24"]]],
            "ports": ["set", ["eth0", "veth-test"]]
          }

    response = update('NLAN_Subnet', where, row)
    _printcount(response)

    response = select('NLAN_Subnet', where)
    print str(todict(response, 'subnets'))
   
    # Creates an instance of OVSDB O/R mapper 
    print "##### Row instance creation test #####"
    row = Row('subnets', ('vni', 1001))
    print "row: " + str(row.row)
    #print "_uuid: " + row['_uuid']

    print "----- add 'ports' ------"
    row['ports'] = ["eth0", "eth1"]
    print "----- add 'ip_dvr' ------"
    row['ip_dvr'] = {'addr':'10.0.111.222/24'}
    print "----- row ------"
    print row.getrow()
    print "----- del 'ports' ------"
    del row['ports']
    print "----- del 'vid' ------"
    del row['vid']
    print "----- Select ------"
    select('NLAN_Subnet', where)
   
    print "##### Delete test ######"
    
    # This fuction call fails, since one reference remains in 'NLAN' table.
    print "----- This test fails ------"
    delete('NLAN_Subnet', where)
    print "----- Row.delrow() ------"
    #mutate_delete('NLAN_Subnet', where, 'NLAN', 'subnets')
    row.delrow()
    print "----- Select ------"
    response = select('NLAN', [])
    print str(todict(response))

    print "##### Row class test #####"
    model = {
        "vid": 101,
        "vni": 1001,
        "ip_dvr": {"addr":"10.0.0.1/24"},
        "ports": ["eth0", "veth-test"]
        }
    print "----- Row.setrow(model) -----"
    row.setrow(model)
    print "----- Row.getrow() -----"
    v = row.getrow()
    print v
    for key in v.keys():
        print key + ': ' + str(v[key])
    #row.delrow()
    #print (row.getrow())
    print "----- Row.clear() -----"
    Row.clear()

    print "##### Row class test2 #####"
    row = Row('subnets', ('vni', 1001))
    print "----- crud: add -----"
    model = {
        "vid": 101,
        "vni": 1001,
        "ip_dvr": {"addr":"10.0.0.1/24"},
        "ports": ["eth0", "veth-test"]
        }
    row.crud('add', model)
    print row.getrow()
    print "----- crud: update -----"
    model = {
            "ip_dvr": {"addr":"20.0.0.1/24", "mode":"dvr"},
        "ports": ["eth0"]
        }
    row.crud('update', model)
    print row.getrow()
    print "----- crud: delete -----"
    model = {
        "vid": 101,
        "ip_dvr": {"addr": "20.0.0.1/24", "mode": "dvr"},
        "ports": ["eth0"]
        }
    row.crud('delete', model)
    print row.getrow()
    print "----- Row.clear() -----"
    Row.clear()

    print "##### Ovsdb search test #####"
    try:
        print search('Interface', ['ofport', 'options'], 'type', 'patch')
    except:
        pass


