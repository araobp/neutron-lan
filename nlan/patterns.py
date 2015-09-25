# 2014/5/27
# Augumented OVSDB-schema supporing patterns for OVSDB-primitive type "string"
#
# The main purpose is to support ipv4-address, ipv4-prefix as defined in RFC6012.
# Also NLAN-specific patterns are defined in this module.

#--------------------------------------------------------------------------------

# OVSDB schema primitive types
string = '[a-zA-Z0-9_]+'
integer = '[-+]?[0-9]+'

# (Reference) RFC6021 "Common YANG Data Types"
ipv4_address = '(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}'\
                +  '([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])'\
                + '(%[\p{N}\p{L}]+)?'

ipv4_prefix =  '(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}' \
                +  '([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])' \
                + '/(([0-9])|([1-2][0-9])|(3[0-2]))'

# ovs-vsctl controller address
# (Reference) http://openvswitch.org/cgi-bin/ovsman.cgi?page=utilities%2Fovs-vsctl.8
# Limitations: tcp and ssl only
ofc_address = '(ssl|tcp):'+ipv4_address+':[1-9][0-9]{0,4}'

# NLAN-specfic string pattern 
dvr_mode = 'dvr|hub|spoke|spoke_dvr'

#---------------------------------------------------------------------------------

import re
import __builtin__

TYPES = None
if '__n__' in __builtin__.__dict__:
    TYPES = __n__['types']
else:
    from env import TYPES 


pattern_check = lambda pattern, value: re.match('^'+globals()[pattern]+'$', value)

debug = False

def key_in_dict(dict_, key):
    if key in dict_:
        return dict_[key]
    else:
        return None

def check_param(module, param, value):
    types = TYPES[module][param]
    type_ = types['key']['type']
    minInteger = None
    maxInteger = None
    if type_ == 'integer':
        minInteger = key_in_dict(types['key'], 'minInteger')
        if minInteger:
            minInteger = int(minInteger)
        maxInteger = key_in_dict(types['key'], 'maxInteger')
        if maxInteger:
            maxInteger = int(maxInteger)
    min_ = key_in_dict(types, 'min')
    max_ = key_in_dict(types, 'max')
    pattern = key_in_dict(types['key'], '_pattern')
    enum = key_in_dict(types['key'], 'enum')
    if isinstance(enum, list):
        enum = enum[1]
    value_ = key_in_dict(types, 'value')
    if value_:
        type_ = types['value']['type']
        pattern = key_in_dict(types['value'], '_pattern')

    if debug:
        print
        print '--- NLAN schema ---'
        print 'type', type_
        print 'minInteger', minInteger
        print 'maxInteger', maxInteger
        print 'min', min_
        print 'max', max_
        print '_pattern', pattern
        print 'enum', enum
        print 'value', value_
        print '--- args ---'
        print 'module', module
        print 'param', param
        print 'value', value

    def _iflist(m):
        if m == 'unlimited' or int(m) > 1 and not value_:
            return True # list
        else: # scalar or map
            return False

    def _intcheck(v):
        if not isinstance(v, int):
            return (False, "The value '{}' must be int".format(str(v)))
        if minInteger  and v < minInteger:
            return (False, "The int value '{}' must be larger than minInteger: {}".format(str(v), str(minInteger)))
        if maxInteger and v > maxInteger:
            return (False, "The int value '{}' must be smaller than maxInteger: {}".format(str(v), str(maxInteger)))
        if enum and v not in enum:
            return (False, "The int value '{}' is not a member of enum: {}".format(str(v), str(enum)))
        if pattern and not pattern_check(pattern, v):
                return (False, "The int value '{}' does not match the pattern: {}".format(str(v), globals()[pattern]))
        return (True, None)


    if type_ == 'integer':
        if _iflist(max_):
            if not isinstance(value, list):
                return (False, "The value '{}' must be list".format(str(value)))
            if max_ != 'unlimited' and len(value) > int(max_):
                return (False, "Length of the list '{}' out of range {}".format(value, max_))
            for i in value:
                (b, m) = _intcheck(value)
                if not b:
                    return (False, m)
        else:
            (b, m) = _intcheck(value)
            if not b:
                return (False, m)
    elif type_ == 'string':
        if _iflist(max_):
            if not isinstance(value, list):
                return (False, "the value '{}' must be list".format(str(value)))
            if max_ != 'unlimited' and len(value) > int(max_):
                return (False, "Length of the list '{}' out of range {}".format(str(value), max_))
            for s in value:
                if not isinstance(s, str) and not isinstance(s, unicode):
                    return (False, "The value '{}' must be str"'{}'.format(str(s)))
                if pattern and not pattern_check(pattern, s):
                    return (False, "The str value '{}' does not match the pattern: {}".format(s, globals()[pattern]))
            if enum and s not in enum:
                return (False, "The str value '{}' is not a member of enum: {}".format(s, str(enum)))
        elif value_:
            if not isinstance(value, dict):
                return (False, "The value '{}' must be dict".format(str(value)))
            if max_ != 'unlimited' and len(value.keys()) > int(max_):
                return (False, "The number of the dict keys '{}' out of range {}".format(str(value.keys()), max_))
            for k,v in value.iteritems():
                if enum and not k in enum:
                    return (False, "The str key '{}' is not a member of enum: {}".format(k, str(enum)))
                if not isinstance(v, str) and not isinstance(v, unicode):
                    return (False, "The value '{}' must be str".format(str(v)))
                if pattern and not pattern_check(pattern[k],v):
                    return (False, "The str value '{}' does not match the pattern: {}".format(v, globals()[pattern[k]]))
        else:
            if not isinstance(value, str) and not isinstance(value, unicode):
                return (False, "The value '{}' must be str".format(str(value)))
            if enum and not value in enum:
                return (False, "The str value '{}' is not a member of enum: {}".format(value, str(enum)))
            if pattern and not pattern_check(pattern, value):
                return (False, "The str value '{}' does not match the pattern: {}".format(value, globals()[pattern]))
            
    return (True, None)


def check_model(operation, module, data):

    kk = TYPES[module]
    for k,v in data.iteritems():
        if k in kk:
            if operation != 'delete':
                (b, m) = check_param(module, k, v)
                if not b:
                    return (b, m)
        else:
            if k != '_index':
                return (False, "The state param '{}' does not exist in the schema".format(k))
    return (True, None)


if __name__ == '__main__':
    import sys
    import unittest
    #debug=True

    class TestSequenceFunctions(unittest.TestCase):

        def test1(self):
            print
            self.assertTrue(check_param('bridges', 'ovs_bridges', 'enabled')[0])
            self.assertTrue(check_param('bridges', 'ovs_bridges', u'enabled')[0])
            self.assertFalse(check_param('bridges', 'ovs_bridges', 'xxx')[0])
            print check_param('bridges', 'ovs_bridges', 'xxx')[1]
            self.assertTrue(check_param('bridges', 'controller', 'tcp:123.123.123.123:1111')[0])
            self.assertFalse(check_param('bridges', 'controller', 'tcp:123.123.123.323:1111')[0])
            print check_param('bridges', 'controller', '123.123.123.323/24')[1]
            self.assertFalse(check_param('bridges', 'controller', 'tcp:123.123.123.123:1111111111')[0])
            print check_param('bridges', 'controller', '123.123.123.123/33')[1]
            self.assertTrue(check_param('vxlan', 'local_ip', '123.123.123.123')[0])
            self.assertFalse(check_param('vxlan', 'local_ip', '123.123.123.123/24')[0])
            print check_param('vxlan', 'local_ip', '123.123.123.123/24')[1]
            self.assertFalse(check_param('vxlan', 'local_ip', ['123.123.123.123'])[0])
            print check_param('vxlan', 'local_ip', ['123.123.123.123'])[1]
            self.assertTrue(check_param('vxlan', 'remote_ips', ['123.123.123.124', '123.123.123.123'])[0])
            self.assertFalse(check_param('vxlan', 'remote_ips', ['123.123.123.124', '123.123.123.123/24'])[0])
            print check_param('vxlan', 'remote_ips', ['123.123.123.124', '123.123.123.123/24'])[1]
            self.assertTrue(check_param('subnets', 'vni', 16777215)[0])
            self.assertFalse(check_param('subnets', 'vni', 16777216)[0])
            print check_param('subnets', 'vni', 16777216)[1]
            self.assertTrue(check_param('subnets', 'vni', 0)[0])
            self.assertFalse(check_param('subnets', 'vni', -1)[0])
            print check_param('subnets', 'vni', -1)[1]
            self.assertTrue(check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123/24', 'mode':'dvr'})[0])
            self.assertTrue(check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123/24', 'mode':'dvr', 'dhcp': 'enabled'})[0])
            self.assertFalse(check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123', 'mode':'dvr'})[0])
            print check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123', 'mode':'dvr'})[1]
            self.assertFalse(check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123/24', 'mode':'xxx'})[0])
            print check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123/24', 'mode':'xxx'})[1]
            self.assertFalse(check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123/24', 'mode':'dvr', 'xxx': 'yyy'})[0])
            print check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123/24', 'mode':'dvr', 'xxx': 'yyy'})[1]
            self.assertTrue(check_param('subnets', 'ip_dvr', {'addr':'123.123.123.123/24', 'mode':'dvr', 'dhcp': 'xxx'})[0])

    unittest.main(verbosity=2)

