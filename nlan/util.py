#from env import NLAN_DIR 
import os, copy, yaml

# [Reference] http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
def decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv

def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv

def decode(data):
    if isinstance(data, dict):
        return decode_dict(data)
    elif isinstance(data, list):
        return decode_list(data)
    else:
        return data

# Remove a specific key/value pair from data 
def remove_item(data, key):

    def _process_list(d):
        for l in d:
            if isinstance(l, list):
                _process_list(l)
            elif isinstance(l, dict):
                _process_dict(l)

    def _process_dict(d):
        if key in d:
            del d[key]
        for k, v in d.iteritems():
            if isinstance(v, list):
                _process_list(v)
            elif isinstance(v, dict):
                _process_dict(v)

    if isinstance(data, list):
        _process_list(data)
    elif isinstance(data, dict):
        _process_dict(data)

    return data




if __name__ == '__main__':

    import unittest
    import json
    import dictdiffer

    class TestSequenceFunctions(unittest.TestCase):

        def testDecodeDict(self):

            json_data = '{"a": 0, "b": 0, "c": {"d": null, "e": [1, {"f":"abc"}]}}'
            # Unicode dict
            dict_data0 = json.loads(json_data)
            sample_value  = dict_data0['c']['e']
            # Ascii dict
            dict_data1 = json.loads(json_data, object_hook=decode_dict )
            
            dict_data2 = {"a": 0, "b": 0, "c": {"d": None, "e": [1, {"f":"abc"}]}}

            self.assertNotIsInstance(sample_value, str)  # unicode
            self.assertEqual(len(list(dictdiffer.diff(dict_data1, dict_data2))), 0)


        def testDecodeDict3(self):
            
            args = [u"a", u"b", u"c", {u"d": None, u"e": [1, {u"f":u"abc"}]}]
            dict_data1 = decode(args)
            dict_data2 = ["a", "b", "c", {"d": None, "e": [1, {"f":"abc"}]}]
            self.assertEqual(len(list(dictdiffer.diff(dict_data1, dict_data2))), 0)
        def testRemoveItem(self):

            data1 = {'a':1, 'b':2, 'X':3, 'c':['d', {'X':4, 'e':5}]}
            data1R = {'a':1, 'b':2, 'c':['d', {'e':5}]}
            data2 = ['a', 'b', {'c':1, 'd':[{'X':2, 'e':3}, 'f']}]
            data2R = ['a', 'b', {'c':1, 'd':[{'e':3}, 'f']}]

            data1 = remove_item(data1, 'X')
            self.assertEqual(len(list(dictdiffer.diff(data1, data1R))),0)

            data2 = remove_item(data2, 'X')
            self.assertEqual(len(list(dictdiffer.diff(data2, data2R))),0)

    unittest.main(verbosity=2)
