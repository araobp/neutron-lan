#!/usr/bin/env python
#
# 2014/05/07
#

import os, sys, traceback, copy, time
from collections import OrderedDict
import yaml
from optparse import OptionParser
import dictdiffer
import nlan, cmdutil, env
from errors import NlanException
from util import remove_item

bar = '//////////////////////////////////////////////////////////////////////////////'

router = '_ALL' 
prev = None

def _args_od(args, reverse=False):
    od = OrderedDict()
    state_order = copy.copy(env.STATE_ORDER)
    if reverse:
        state_order.reverse()
    for module in state_order:
        if module in args:
            od[module] = args[module]
    return od

def _print_success():
    print '****************'
    print '*** SUCCESS! ***'
    print '****************'

def _print_failure():
    print 'XXXXXXXXXXXXXXXX'
    print 'XXX FAILURE! XXX'
    print 'XXXXXXXXXXXXXXXX'


def do(scenario, dirname, interactive):

    for l in scenario:
        if 'do' in l:
            do_file = os.path.join(dirname, l['do'])
            with open(do_file, 'r') as f:
                scenario = yaml.load(f.read())
            do(scenario, dirname, interactive)
        if 'sleep' in l:
            time.sleep(int(l['sleep']))
        if 'comment' in l:
            rp = "TEST: {}".format(l['comment'])
            print bar[:5], rp, bar[5+len(rp):]
        if interactive:
            raw_input("Press Enter to continue...") 
        if 'command' in l:
            cmdutil.check_cmd(l['command'])
        if 'nlan' in l:
            ll = l['nlan']
            options = None
            args = None
            if 'options' in ll:
                options = ll['options']
            if 'args' in ll:
                v = ll['args']
                if isinstance(v, dict):
                    if options == '--delete':
                        args = _args_od(v, reverse=True)
                    else:
                        args = _args_od(v)
                    prev = args
                    args = str(args)
                else:
                    args = v.split()
            if 'router' in ll:
                router = ll['router']
            try:
                result = nlan.main(router=router, operation=options, doc=args, output_stdout=True)
                if 'assert' in ll:
                    if ll['assert']:  # not null
                        #args1 = dict(eval(result[0]['stdout']))
                        args1 = dict(result[0]['stdout'])
                        args2 = ll['assert']
                        if args2 == '_prev':
                            args2 = remove_item(prev, '_index')
                        diff = None
                        try:
                            diff = list(dictdiffer.diff(args1, args2))
                            assert len(diff) == 0
                            _print_success()
                        except Exception as e:
                            _print_failure()
                            print diff 
                            print traceback.format_exc()
                    else:  # null
                        if result[0]['stdout']:
                            _print_failure()
                            print result[0]['stdout']
                        else:
                            _print_success()
            except NlanException as e:
                result = e.get_result() 
                type_ = result[0]['response']['exception']
                if 'assertRaises' in ll:
                    assert type_ == ll['assertRaises']['type'] 
                    _print_success()
                else:
                    raise

        


if __name__ == '__main__':

    logo = """
       _  ____   ___   _  __
      / |/ / /  / _ | / |/ /
     /    / /__/ __ |/    /
    /_/|_/____/_/ |_/_/|_/ SCENARIO RUNNER

    """

    usage = logo + "usage: %prog [scenario_file]"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--interactive", help="interactive mode", action="store_true", default=False)

    options, args = parser.parse_args()

    if len(args) == 1:
        with open(args[0], 'r') as f:
            scenario = yaml.load(f.read())
        dirname = os.path.dirname(args[0])
        do(scenario, dirname, options.interactive)
    else:
        parser.print_usage()
        
